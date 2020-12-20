import re
from common import ocr
from colorama import init, Fore
init(autoreset=True)


class Work:
    def __init__(self, name,
                 work_on, work_off,
                 work_on_time_range, work_off_time_range,
                 work_on_position, work_off_position,
                 text_region, work_on_region, work_off_region,
                 work_on_end, work_off_end,
                 special, special_text
                 ):
        self.current_work_on = 0
        self.current_work_off = 0

        self.name = name
        self.work_on = int(work_on)
        self.work_off = int(work_off)
        self.work_on_time_range = re.split('[-,，]', work_on_time_range)
        self.work_off_time_range = re.split('[-,，]', work_off_time_range)
        self.work_on_position = work_on_position
        self.work_off_position = work_off_position
        self.text_region = text_region
        self.work_on_region = work_on_region
        self.work_off_region = work_off_region
        self.work_on_end = re.split('[-,，]', work_on_end)
        self.work_off_end = re.split('[-,，]', work_off_end)
        self.special = int(special)
        self.special_text = special_text

    def check_work_on(self, image, config):
        if self.work_on == 0:
            print('this work does not require work-on')
            return
        if self.current_work_on == 1:
            print('aleardy work_on')
            return

        if self.special == 1:
            # 判断是否有当前班
            text = ocr.ocr_img_region_baidu(image, config, self.text_region)
            print(text)
            if len(text) < 1:
                # 未包含特殊字符，则没有当前班
                print(Fore.RED+'can not ocr any string, there is no current work today...')
                self.current_work_on = 1
                return
            if self.special_text not in text[0]:
                self.current_work_on = 1
                print(Fore.RED+'can not find special work text, there is no current work today...')
                return
        # 
        result = ocr.ocr_img_region_baidu(image, config, self.work_on_region)
        print(result)
        if len(result) < 1:
            return
        if result[0] in self.work_on_end:
            self.current_work_on = 1

    def check_work_off(self, image, config):
        if self.work_off == 0:
            print('this work does not require work-off')
            return
        if self.current_work_off == 1:
            print('aleardy work_off')
            return
        # 
        result = ocr.ocr_img_region_baidu(image, config, self.work_off_region)
        print(result)
        if len(result) < 1:
            return
        if result[0] in self.work_off_end:
            self.current_work_off = 1

    def check_work(self, image, config):
        self.check_work_on(image, config)
        self.check_work_off(image, config)

    @staticmethod
    def time_in_range(hour, min, range):
        start = list(map(int, re.split('[:：]', range[0])))
        end = list(map(int, re.split('[:：]', range[1])))
        _start = start[0]*60+start[1]
        _end = end[0]*60+end[1]
        _now = hour*60+min
        if _now < _start or _now > _end:
            return False
        else:
            return True

    def need_work_on(self, hour, min):
        if self.current_work_on == 1:
            return False
        if self.work_on == 0:
            return False
        if self.time_in_range(hour, min, self.work_on_time_range):
            return True
        return False

    def need_work_off(self, hour, min):
        if self.current_work_off == 1:
            return False
        if self.work_off == 0:
            return False
        if self.time_in_range(hour, min, self.work_off_time_range):
            return True
        return False

    @staticmethod
    def get_region_center(region):
        rect = list(map(int, region.split(',')))
        return int((rect[0]+rect[2])/2), int((rect[1]+rect[3])/2)

