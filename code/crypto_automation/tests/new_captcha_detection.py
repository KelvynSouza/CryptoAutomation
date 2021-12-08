import configparser
import cv2
import numpy as np
import time
from matplotlib import pyplot as plt
from crypto_automation.commands.image_processing.helper import ImageHelper
from crypto_automation.commands.shared.os_helper import create_log_folder
from crypto_automation.commands.windows_actions.helper import WindowsActionsHelper


class TestCaptchaSolver:
    def __init__(self, config: configparser):
        self.__config = config
        self.__image_helper = ImageHelper()
        self.__windows_action_helper = WindowsActionsHelper(config, self.__image_helper)


    def show_info(self, image, original=False):
        print('-----------------------------------------------------')    
        print('shape:', image.shape, 'and', 'size:', image.size)    
        print(image.dtype)
        if original:
            plt.imshow(image)
        else:
            if len(image.shape) < 3:
                plt.imshow(image, cmap='gray')        
            else:
                plt.imshow(image[:,:,::-1])

        plt.show()


    def getting_rectangle_countours(self, image_treated, h_min = None, h_max = None, w_min = None, w_max = None, find_mode = cv2.RETR_CCOMP):
        contours, _ = cv2.findContours(image_treated, find_mode, cv2.CHAIN_APPROX_SIMPLE)

        if h_min:
            h_min_fuction = lambda h: h >= h_min
        else:
            h_min_fuction = lambda h: True

        if h_max:
            h_max_fuction = lambda h: h <= h_max
        else:
            h_max_fuction = lambda h: True

        if w_min:
            w_min_fuction = lambda w: w >= w_min
        else:
            w_min_fuction = lambda w: True

        if w_max:
            w_max_fuction = lambda w: w <= w_max
        else:
            w_max_fuction = lambda w: True

        valid_contours = list()
        for contour in contours:
            (x,y,w,h) = cv2.boundingRect(contour)
            if (w_min_fuction(w) and w_max_fuction(w)) and (h_min_fuction(h) and h_max_fuction(h)):
                valid_contours.append((x,y,w,h))

        return valid_contours


    def draw_rectangles_in_image(self, image, contours):
        for x,y,w,h in contours:
            cv2.rectangle(image, (x, y), (x + w, y + h), (225, 255, 0), 2)
        return image
    

    def run(self):

        game_image = cv2.imread("../resources/images/test/captcha_new/captcha_2.png") 

        desktop_game_gray = cv2.cvtColor(game_image, cv2.COLOR_BGR2GRAY)
        #self.show_info(desktop_game_gray)

        _, thresh_image = cv2.threshold(desktop_game_gray, 80, 255, cv2.THRESH_BINARY)
        #self.show_info(thresh_image)

        contours, _ = cv2.findContours(thresh_image, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

        cv2.drawContours(game_image, contours, -1, (255,0,0), 1)
        self.show_info(game_image)

        edg_img = cv2.Canny(thresh_image, 225, 255)
        self.show_info(edg_img)        

        #find place to put captcha
        game_img = cv2.medianBlur(game_image, 5)


config_filename = "C:\\Users\\carlo\\Documents\\dev\\CryptoOcrAutomation\\code\\crypto_automation\\settings.ini"

config = configparser.ConfigParser(
    interpolation=configparser.ExtendedInterpolation())
config.read(config_filename)
config['TEMPLATES']['game_images_path'] = '..\\resources\\images\\game'

create_log_folder(config['COMMON']['log_path'],
                  config['COMMON']['screenshots_path'])

asd = TestCaptchaSolver(config)
asd.run()


