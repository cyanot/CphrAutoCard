# -*- coding: utf-8 -*-

'''
Created on 2011-8-24
主要用途：
    对程序中所使用的loggong模式做一般性配置
@author: JerryKwan

'''

import logging
import datetime
import time

import logging.handlers

import os
# from pythonjsonlogger import jsonlogger
import json

LEVELS = {'NOSET': logging.NOTSET,
          'DEBUG': logging.DEBUG,
          'INFO': logging.INFO,
          'WARNING': logging.WARNING,
          'ERROR': logging.ERROR,
          'CRITICAL': logging.CRITICAL}


def json_translate(obj):
    return {"special": obj.special}


# jsonFormatter = jsonlogger.JsonFormatter(json_default=json_translate,
#                                      json_encoder=json.JSONEncoder())

# set up logging to file

# logging.basicConfig(level = logging.NOTSET,
#                    format = "%(asctime)s %(name)-12s %(levelname)-8s %(message)s"
#                    )

##                    filename = "./log.txt",

##                    filemode = "w")

# create logs file folder
logs_dir = os.path.join(os.path.curdir, "logs")
if os.path.exists(logs_dir) and os.path.isdir(logs_dir):
    pass
else:
    os.mkdir(logs_dir)


FILENAME = "./logs/%s.log" % time.strftime('%Y%m%d',time.localtime())


# define a rotating file handler
rotatingFileHandler = logging.handlers.RotatingFileHandler(filename=FILENAME, maxBytes=1024 * 1024 * 50,
                                                           backupCount=5, encoding="UTF-8")

formatter = logging.Formatter("%(asctime)s %(levelname)s %(module)s.%(funcName)s Line:%(lineno)d %(message)s")

rotatingFileHandler.setFormatter(formatter)

logging.getLogger("").addHandler(rotatingFileHandler)

# define a handler whitch writes messages to sys

console = logging.StreamHandler()

console.setLevel(logging.INFO)

# set a format which is simple for console use
# jsonFormatter = jsonlogger.JsonFormatter()
formatter = logging.Formatter("%(asctime)s %(levelname)s %(module)s.%(funcName)s Line:%(lineno)d %(message)s")

# tell the handler to use this format

console.setFormatter(formatter)

# add the handler to the root logger

logging.getLogger("").addHandler(console)

# set initial log level
logger = logging.getLogger("")
logger.setLevel(logging.INFO)