import os
import subprocess
import time
import psutil
# from colorama import init, Fore
# init(autoreset=True)
EMU_PROCESS_NAME = "MEmu.exe"
EMU_PATH = "D:\Program Files\Microvirt\MEmu\MEmu.exe"


class Android:
    def __init__(self, filename):
        self.filename = filename
        # 按下电源键
        self.cmd_push_power = 'adb shell input keyevent 26'
        # 返回桌面
        self.cmd_back_home = 'adb shell input keyevent 3'
        # 截屏
        self.cmd_screen_cap = 'adb shell screencap -p sdcard/%s' % self.filename
        # 获取截屏 保存到当前目录
        self.cmd_pull_screen = 'adb pull sdcard/%s .' % self.filename
        # 删除截屏
        self.cmd_rm_screen_cap = 'adb shell rm -r sdcard/%s' % self.filename
        # 启动员工自助app
        self.cmd_open_cphr = 'adb shell am start -n com.cptc.cphr/.WelcomeActivity'
        # app 退出
        self.cmd_kill_cphr = 'adb shell am force-stop com.cptc.cphr'
        # 滑动解锁
        self.cmd_swipe_unlock = 'adb shell input swipe 300 1000 300 500'
        #
        self.cmd_dumpsys = 'adb shell dumpsys window policy'
        # check devices
        self.cmd_check_devices = 'adb devices'
        # tap position
        self.cmd_tap_position = 'adb shell input tap '

    def connect(self, name):
        cmd = 'adb connect %s ' % name
        process = subprocess.Popen(cmd)
        process.wait()
        print('cmd connect %s success' % name)

    def check_devices(self):
        find_str = 'device'
        lines = os.popen(self.cmd_check_devices).readlines()
        # print(lines)
        for line in lines[1:]:
            if find_str in line:
                return True
        return False

    def is_awake(self):
        '''
        判断的依据是'    mAwake=false\n'
        '''
        awake_value = 'mAwake=true'
        lines = os.popen(self.cmd_dumpsys).readlines()
        # print(lines)
        for line in lines:
            if awake_value in line:
                return True
        return False

    def is_lock(self):
        '''
        判断锁屏状态，指令二选一，或都选
        返回 True:锁屏未解锁
        返回 False:锁屏已解锁
        '''

        cmd = 'adb shell dumpsys window policy|findstr isStatusBarKeyguard'

        with os.popen(cmd) as f:
            res = str(f.read()).split()
        # print(res)
        if 'isStatusBarKeyguard=true' in res:
            # print('锁屏未解锁')
            return True
        elif 'isStatusBarKeyguard=false' in res:
            # print('锁屏已解锁')
            return False

    def open_cphr(self):
        operations = [self.cmd_open_cphr]
        if self.is_lock():
            operations.insert(0, self.cmd_swipe_unlock)
        if not self.is_awake():
            operations.insert(0, self.cmd_push_power)
        for operation in operations:
            process = subprocess.Popen(operation, shell=False, stdout=subprocess.PIPE)
            process.wait()
            # 确保完全启动，并且加载上相应按键
        # print('sleep 35 s to wait app')
        time.sleep(15)
        print("open cphr success")

    def close_cphr(self):
        operations = [self.cmd_back_home, self.cmd_kill_cphr]
        for operation in operations:
            process = subprocess.Popen(operation, shell=False, stdout=subprocess.PIPE)
            process.wait()
        print("kill cphr success")

    def screen_cap(self):
        operations = [self.cmd_screen_cap, self.cmd_pull_screen, self.cmd_rm_screen_cap]
        for operation in operations:
            process = subprocess.Popen(operation, shell=False, stdout=subprocess.PIPE)
            process.wait()
        print("screencap to computer success")

    def tap_postion(self, x, y):
        cmd = self.cmd_tap_position + ' %d %d ' % (x, y)
        operations = [cmd]
        for operation in operations:
            process = subprocess.Popen(operation, shell=False, stdout=subprocess.PIPE)
            process.wait()
        print("tap position %d %d success" % (int(x), int(y)))


class Simulator:
    def __init__(self, name, path):
        if len(name) < 1:
            self.name = EMU_PROCESS_NAME
        else:
            self.name = name

        if len(path) < 1 or path is None:
            self.path = EMU_PATH
        else:
            self.path = path

    def open(self):
        process = subprocess.Popen(self.path)
        # process.wait()
        print('open emu success')

    def close(self):
        cmd = 'taskkill /IM %s /F' % self.name
        os.system(cmd)

    def process_exist(self):
        for pid in psutil.pids():
            process = psutil.Process(pid)
            # print(process.name())
            # print(process)
            if process.name() == self.name:
                if process.status() == 'running':
                    return True
        return False

    def reopen(self):
        if self.process_exist():
            print('simulator exists, close it..')
            self.close()
            time.sleep(2)
        self.open()
        print("sleep 100 s ")
        time.sleep(100)
