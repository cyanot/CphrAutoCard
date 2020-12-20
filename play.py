from PIL import Image
from common import ocr
from threading import Thread
import time
import random
import configparser
import smtplib
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
import logging
from colorama import init, Fore
import re
from common.work import Work
from common.phone import Android
from apscheduler.schedulers.blocking import BlockingScheduler

#
init(autoreset=True)

logger = logging.getLogger(__name__)

from log import mylogging

# 读取配置文件
CONFIG = configparser.ConfigParser()
# config.read('./config/configure.conf', encoding='utf-8')
CONFIG.read('./config/configure.conf', encoding='utf-8')

# 全局变量
# 每天班次list
WORKS = []
#
REST_REGION = CONFIG.get('work', 'rest_region')
REST_TEXT = CONFIG.get('work', 'rest_text')

REFRESH_RUNNING = 0
CLEAR_RUNNING = 0
CHECK_RUNNING = 0

SCREEN_FILE = 'screenshot.png'

android = Android(SCREEN_FILE)


def send_email(img_file_path, subject, config):
    host = config.get("mail", "host")
    port = config.get('mail', 'port')

    receiver = config.get('mail', 'receiver')
    sender = config.get('mail', 'sender')

    username = config.get('mail', 'username')
    password = config.get('mail', 'password')

    message = MIMEMultipart('related')
    message['Subject'] = subject
    message['From'] = sender
    message['To'] = receiver
    content = MIMEText('<html><body><img src="cid:imageid" alt="imageid"></body></html>', 'html', 'utf-8')
    message.attach(content)
    file = open(img_file_path, "rb")
    img_data = file.read()
    file.close()
    img = MIMEImage(img_data)
    img.add_header('Content-ID', 'imageid')
    message.attach(img)

    try:
        server = smtplib.SMTP_SSL(host, port)
        server.login(username, password)
        server.sendmail(sender, receiver, message.as_string())
        server.quit()
        print(Fore.MAGENTA + "发送邮件成功")
    except smtplib.SMTPException as e:
        print(e)


def print_object(obj):
    print('\n'.join(['%s:%s' % item for item in obj.__dict__.items()]))


def get_work_off_range(off_time):
    """
    下班打卡时间范围生成
    :param off_time:
    :return:
    """
    times = list(map(int, re.split('[:：]', off_time)))
    after = random.randint(0, 4)
    # start_minutes = (times[1]+10)%60
    # start_hour = times[0] + int((times[1]+10)/60)
    return '%d:%d-%d:%d' % (
        times[0] + int((times[1] + after) / 60),
        (times[1] + after) % 60,
        times[0] + int((times[1] + after + 20) / 60),
        (times[1] + after + 20) % 60
    )


def get_work_on_range(on_time):
    times = list(map(int, re.split('[:：]', on_time)))
    before = random.randint(6, 30)
    # start_minutes = (times[1]+10)%60
    # start_hour = times[0] + int((times[1]+10)/60)
    return '%d:%d-%d:%d' % (
        times[0] - 1 + int((times[1] + 60 - before) / 60),
        (times[1] + 60 - before) % 60,
        times[0],
        times[1]
    )


def get_work_type(on_time, off_time):
    """
    根据上下班时间判断是否需要 上下班考勤
    :param on_time:
    :param off_time:
    :return:
    """
    #
    # return on ,off
    on_times = list(map(int, re.split('[:：]', on_time)))
    off_times = list(map(int, re.split('[:：]', off_time)))
    if on_times[0] < off_times[0]:
        return 1, 1
    if on_times[0] > off_times[0]:
        return 1, 0
    return 0, 0


def is_today_rest():
    img = Image.open(SCREEN_FILE)
    result = ocr.ocr_img_region_baidu(img, CONFIG, REST_REGION)
    if len(result) < 1:
        return False
    if REST_TEXT in result[0]:
        return True
    return False


def refresh_works():
    global REFRESH_RUNNING, WORKS

    print(Fore.CYAN + "开始刷新班次")

    if len(WORKS) > 1:
        print(Fore.RED + "班次已经获取，跳过..")
        REFRESH_RUNNING = 0
        return

    try:
        android.open_cphr()
        android.screen_cap()
        android.close_cphr()
    except:
        REFRESH_RUNNING = 0
        print(Fore.RED + "ADB 运行故障，跳过本次检测...")
        return

    if is_today_rest():
        print(Fore.MAGENTA + "今天休息")
        WORKS.clear()
        REFRESH_RUNNING = 0
        return

    img = Image.open(SCREEN_FILE)
    config = CONFIG
    max = int(config.get('work', 'max'))
    rect = config.get('work', 'rect').replace(' ', '').split(',')
    rect = list(map(int, rect))
    on_left = int(config.get('work', 'on_left'))
    off_left = int(config.get('work', 'off_left'))
    clearance = int(config.get('work', 'clearance'))
    special_text = config.get('work', 'special_text')
    work_on_end = config.get('work', 'work_on_end')
    work_off_end = config.get('work', 'work_off_end')
    # left top width height
    for i in range(0, max):
        print(i)
        print(Fore.BLUE + "获取第 %d 个班次信息" % (i + 1))
        # for baidu openapi 2 rps limit
        time.sleep(0.5)
        text_region = '%d,%d,%d,%d' % (
            rect[0], rect[1] + (rect[3] + clearance) * i, on_left, rect[1] + (rect[3] + clearance) * i + rect[3])
        work_on_region = '%d,%d,%d,%d' % (
            on_left, rect[1] + (rect[3] + clearance) * i, off_left, rect[1] + (rect[3] + clearance) * i + rect[3])
        work_off_region = '%d,%d,%d,%d' % (
            off_left, rect[1] + (rect[3] + clearance) * i, rect[0] + rect[2],
            rect[1] + (rect[3] + clearance) * i + rect[3])

        print(text_region)
        text = ocr.ocr_img_region_baidu(img, config, text_region)
        if len(text) < 1:
            print(Fore.RED + "未能识别上下班打卡信息，跳过..")
            continue
        if '(' not in text[0]:
            print(Fore.RED + "打卡信息识别有误，跳过..")
            continue
        name = text[0]

        times = re.split('[-(]', text[0])
        print(times)
        work_on_range = get_work_on_range(times[0])
        print(work_on_range)
        work_off_range = get_work_off_range(times[1])
        print(work_off_range)
        work_on = 0
        work_off = 0
        special = 0

        if special_text in text[0]:
            #
            work_off = 1
            work_on = 0

        else:
            work_off, work_on = get_work_type(times[0], times[1])

        work = Work(
            name,
            work_on, work_off,
            work_on_range, work_off_range,
            '', '',
            text_region, work_on_region, work_off_region,
            work_on_end, work_off_end,
            special, special_text
        )
        print(Fore.MAGENTA +"第 %d 个班次信息：" % (i + 1))
        print_object(work)
        # print(work.name)
        WORKS.append(work)
    print(Fore.MAGENTA + "获取到 %d 个班次信息" % len(WORKS))

    REFRESH_RUNNING = 0
    return


def go_check():
    global WORKS
    if len(WORKS) < 1:
        return
    print(Fore.CYAN + time.strftime("%Y-%m-%d-%H:%M:%S", time.localtime())+"开始例行检查")
    random_sleep = random.randint(5, 20)
    print(Fore.CYAN + "随机等待 %d s" % random_sleep)
    time.sleep(random_sleep)
    now = time.localtime(time.time())
    for work in WORKS:
        if work.need_work_on(now.tm_hour, now.tm_min):
            print(Fore.GREEN + "当前班次此时需要签到")
            print_object(work)
            x, y = work.get_region_center(work.work_on_region)
            # open app
            android.open_cphr()
            # card
            android.tap_postion(x, y)
            android.screen_cap()
            # check work_on
            img = Image.open(SCREEN_FILE)
            work.check_work(img, CONFIG)
            # print check
            print(Fore.CYAN + "签到之后检查")
            print_object(work)
            # close
            android.close_cphr()
            # send mail
            title = '%s 上班打卡[%d-%d-%d %d:%d:%d]' % (
                work.name,
                now.tm_year, now.tm_mon, now.tm_mday,
                now.tm_hour, now.tm_min, now.tm_sec
            )
            send_email(SCREEN_FILE, title, CONFIG)
            continue
        if work.need_work_off(now.tm_hour, now.tm_min):
            print(Fore.GREEN + "当前班次此时需要签退")
            print_object(work)
            x, y = work.get_region_center(work.work_off_region)
            # open app
            android.open_cphr()
            # card
            android.tap_postion(x, y)
            android.screen_cap()
            # check work
            img = Image.open(SCREEN_FILE)
            work.check_work(img, CONFIG)
            # print check
            print(Fore.CYAN + "签退之后检查")
            print_object(work)
            # close
            android.close_cphr()
            # send mail
            title = '%s 下班打卡[%d-%d-%d %d:%d:%d]' % (
                work.name,
                now.tm_year, now.tm_mon, now.tm_mday,
                now.tm_hour, now.tm_min, now.tm_sec
            )
            send_email(SCREEN_FILE, title, CONFIG)
            continue
    print(Fore.GREEN + "本次检查完成")


def clear_works():
    """
    day end
    :return:
    """
    global WORKS
    if len(WORKS) > 0:
        print(Fore.CYAN + "开始清空当日班次..")
        WORKS.clear()
    else:
        print(Fore.RED + "当日班次已清空，跳过..")


def test():
    print(Fore.CYAN + time.strftime("%Y-%m-%d-%H:%M:%S", time.localtime()) + '\n')
    time.sleep(4)


def send_mail_test():
    send_email(SCREEN_FILE, "test", CONFIG)


def test_app_open_close():
    android.open_cphr()
    android.close_cphr()


def is_mail_config_passed():
    config = CONFIG
    host = config.get("mail", "host")
    port = config.get('mail', 'port')

    receiver = config.get('mail', 'receiver')
    sender = config.get('mail', 'sender')

    username = config.get('mail', 'username')
    password = config.get('mail', 'password')
    if host is None \
            or port is None \
            or receiver is None \
            or sender is None \
            or username is None \
            or password is None:
        return False
    return True


if __name__ == '__main__':
    # send_mail_test()
    # now = time.localtime(time.time())
    # print(now)
    # print(now.tm_hour)
    # print(now.tm_min)
    # check environment
    print(Fore.CYAN + "开始检查运行环境")

    if not android.check_devices():
        print(Fore.RED + "adb 未检测到 设备，无法继续运行")
        exit(1)
    else:
        print(Fore.GREEN + "设备检查通过")

    if not is_mail_config_passed():
        print(Fore.RED+"邮箱配置检查失败，无法继续运行")
        exit(1)
    else:
        print(Fore.GREEN+"邮箱配置检查通过")

    # 第一次运行先获取班次信息
    refresh_works()

    # go_check()

    scheduler = BlockingScheduler()

    # scheduler.add_job(test, 'cron', day="*", hour="10-11", minute="*", second="*/2")

    # scheduler.add_job(test_app_open_close, 'cron', day="*", minute="*", second="*")
    scheduler.add_job(refresh_works, 'cron', day="*", hour="5-7")
    scheduler.add_job(clear_works, 'cron', day="*", hour="21-23")
    scheduler.add_job(go_check, 'cron', day="*", minute="*", hour="8-20")
    print(Fore.GREEN + "调度器开始运行..")
    scheduler.start()
