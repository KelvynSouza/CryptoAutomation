import configparser
import logging
import time
import cv2
import numpy as np
import threading
from matplotlib import pyplot as plt
from app.shared.image_processing_helper import ImageHelper
from app.shared.thread_helper import Job
from app.shared.os_helper import create_log_folder
from app.shared.windows_action_helper import WindowsActionsHelper


class TestThreadsSolution:
    def __init__(self, config: configparser):
        self.__config = config
        self.__image_helper = ImageHelper()
        self.__windows_action_helper = WindowsActionsHelper(config, self.__image_helper)


    def run(self): 
        thread_1 = Job(self.thread_1, 0.1, False, "sucesso 1")
        thread_2 = Job(self.thread_2, 0.1, False, "sucesso 2")
        thread_3 = Job(self.thread_3, 0.1, False, "sucesso 3")
        
        thread_1.start()
        thread_2.start()
        thread_3.start()
        time.sleep(5)
        thread_1.pause()
        time.sleep(5)
        thread_2.pause()
        time.sleep(5)
        thread_3.pause()
        time.sleep(5)
        thread_1.resume()
        time.sleep(5)
        thread_2.resume()
        time.sleep(5)
        thread_3.resume()
        time.sleep(5)


        print("fim")

    
    def thread_1(self, message):
        print(message)

    def thread_2(self, message):
        print(message)

    def thread_3(self, message):
        print(message)

config_filename = "..\\settings.ini"

config = configparser.ConfigParser(
    interpolation=configparser.ExtendedInterpolation())
config.read(config_filename)
config['TEMPLATES']['bomb_images_path'] = '..\\resources\\images\\game'
config['TEMPLATES']['captcha_image_path'] = '..\\resources\\images\\game\\captcha'
config['TEMPLATES']['captcha_simple_image_path'] = '..\\resources\\images\\game\\captcha\\simple'
config['TEMPLATES']['captcha_complex_image_path'] = '..\\resources\\images\\game\\captcha\\complex'
config['TEMPLATES']['captcha_magnifier_image_path'] = '..\\resources\\images\\game\\captcha\\magnifier'

create_log_folder(config['COMMON']['log_path'],
                  config['COMMON']['screenshots_path'])

asd = TestThreadsSolution(config)
asd.run()


