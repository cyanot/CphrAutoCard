from common.methods import *
import configparser
CONFIG = configparser.ConfigParser()
CONFIG.read('./config/configure.conf', encoding='utf-8')


if __name__ == '__main__':
    send_email('screenshot.png', 'test', CONFIG)