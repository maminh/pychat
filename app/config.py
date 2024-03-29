import os

from local_params import REDIS_URL

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE_DIR = os.path.join(BASE_DIR, 'templates')
STATIC_DIR = os.path.join(BASE_DIR, 'static')


class Config():
    SECRET_KEY = 'KG5X60YF1NBBA68T19EHDJN2VE85RP721990176OFM4LOYTBGUTO2O617HQX9QX6'
    REDIS_URL = REDIS_URL
    DEBUG_MODE = True
