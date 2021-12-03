import configparser
import cv2
import numpy as np
import pyautogui
from matplotlib import pyplot as plt
from crypto_automation.commands.image_processing.helper import ImageHelper
from crypto_automation.commands.shared.os_helper import create_log_folder
from crypto_automation.commands.windows_actions.helper import WindowsActionsHelper
from crypto_automation.tests.test_detect_corners import show_info


class TestCaptchaSolver:
    def __init__(self, config: configparser):
        self.__config = config
        self.__image_helper = ImageHelper()
        self.__windows_action_helper = WindowsActionsHelper(config, self.__image_helper)        
        self.get_game_window()

    #region Util
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


    def getting_rectangle_countours(self, image_treated, h_min = None, h_max = None, w_min = None, w_max = None):
        contours, _ = cv2.findContours(image_treated, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)

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

    #endregion

    def get_game_window(self):
        desktop_image = self.__windows_action_helper.take_screenshot()
        desktop_image_gray = cv2.cvtColor(desktop_image, cv2.COLOR_BGR2GRAY)
        _, thresh_image = cv2.threshold(desktop_image_gray, 30, 255, cv2.THRESH_BINARY)
        
        edg_img = cv2.Canny(thresh_image, 225, 255)
        
        contours = self.getting_rectangle_countours(edg_img, 500, 700, 400, 1000)        

        #store this variable globally so that it can be used again
        self.__game_window_position = contours[0]


    def get_gray_piece(self, lower_gray, upper_gray):
        desktop_image = self.__windows_action_helper.take_screenshot()
        x,y,w,h = self.__game_window_position
        game_image = desktop_image[y:y+h,x:x+w]
        #find place to put captcha
        game_img = cv2.medianBlur(game_image, 5)
        # Detection in binary
        mask = cv2.inRange(game_img, lower_gray, upper_gray)        
        #locale piece
        contours = self.getting_rectangle_countours(mask, 60, 90, 40, 90) 
        #store this variable globally so that it can be used again
        self.draw_rectangles_in_image(mask, contours)
        self.show_info(mask)
        self.__gray_piece_position = contours[0]  

    def run(self):
        loop = True

        slide_button = self.__image_helper.wait_until_match_is_found(self.__windows_action_helper.take_screenshot, 
                                                                [], self.__config['TEMPLATES']['captcha_slide'], self.__config['TIMEOUT'].getint('imagematching'), 
                                                                    0.05, False, False)

        #self.__windows_action_helper.click_and_hold(slide_button.x, slide_button.y)

        lower_gray = np.array([110, 110, 110])
        upper_gray = np.array([173, 173, 173])

        self.get_gray_piece(lower_gray, upper_gray)        

        offset_x = 0

        while loop:
            offset_x = offset_x + 1

            self.__windows_action_helper.click_and_hold(slide_button.x + offset_x, slide_button.y)

            desktop_image = self.__windows_action_helper.take_screenshot()

            x_screen, y_screen, w_screen, h_screen = self.__game_window_position

            game_image = desktop_image[y_screen:y_screen+h_screen,x_screen:x_screen+w_screen]

            #find place to put captcha
            game_img = cv2.medianBlur(game_image, 5)

            x_piece,y_piece,w_piece,h_piece = self.__gray_piece_position

            gray_piece = game_img[y_piece:y_piece+h_piece,x_piece:x_piece+w_piece]
            mask_piece = cv2.inRange(gray_piece, lower_gray, upper_gray)
            result = np.where(mask_piece == 255)

            if result[0].size <= 250 or slide_button.x + offset_x > (x_screen + w_screen):
                self.__windows_action_helper.release_click(slide_button.x + offset_x, slide_button.y)
                loop = False





config_filename = "D:\dev\CryptoOcrAutomation\code\crypto_automation\settings.ini"

config = configparser.ConfigParser(
    interpolation=configparser.ExtendedInterpolation())
config.read(config_filename)
config['TEMPLATES']['game_images_path'] = '..\\resources\\images\\game'

create_log_folder(config['COMMON']['log_path'],
                  config['COMMON']['screenshots_path'])

asd = TestCaptchaSolver(config)
asd.run()


