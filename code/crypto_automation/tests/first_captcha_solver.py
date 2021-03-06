import configparser
import cv2
import numpy as np
import time
from matplotlib import pyplot as plt
from app.shared.image_processing_helper import ImageHelper
from app.shared.os_helper import create_log_folder
from app.shared.windows_action_helper import WindowsActionsHelper


class CaptchaSolver:
    def __init__(self, config: configparser, image_helper: ImageHelper, action_helper: WindowsActionsHelper):
        self.__config = config
        self.__image_helper = image_helper
        self.__windows_action_helper = action_helper       
        
   
    def __getting_rectangle_countours(self, image_treated, h_min = None, h_max = None, w_min = None, w_max = None, find_mode = cv2.RETR_CCOMP):
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


    def get_game_window(self):
        desktop_image = self.__windows_action_helper.take_screenshot()
        desktop_image_gray = cv2.cvtColor(desktop_image, cv2.COLOR_BGR2GRAY)
        _, thresh_image = cv2.threshold(desktop_image_gray, 30, 255, cv2.THRESH_BINARY)
        
        edg_img = cv2.Canny(thresh_image, 225, 255)
        
        contours = self.__getting_rectangle_countours(edg_img, 500, 700, 400, 1000)        

        #store this variable globally so that it can be used again
        if contours:
            self.__game_window_position = contours[0]
        else:
            self.__game_window_position = None


    def __get_gray_piece(self, lower_gray, upper_gray):
        result = False
        count = 1
        while result == False:            
            desktop_image = self.__windows_action_helper.take_screenshot()
            x,y,w,h = self.__game_window_position
            game_image = desktop_image[y:y+h,x:x+w]
            #find place to put captcha
            game_img = cv2.medianBlur(game_image, 5)
            # Detection in binary
            mask = cv2.inRange(game_img, lower_gray, upper_gray)        
            #locale piece
            contours = self.__getting_rectangle_countours(mask, 60, 90, 40, 90) 
            #store this variable globally so that it can be used again               
           
            if count > 10:
                self.__gray_piece_position = None
                result = True

            if contours:   
                self.__gray_piece_position = contours[0]  
                result = True

            count +=1
            time.sleep(0.2)


    def solve_captcha(self):
        for x in range(3):
            loop = True
            slide_button = self.__image_helper.wait_until_match_is_found(self.__windows_action_helper.take_screenshot, 
                                                                    [], self.__config['TEMPLATES']['captcha_slide'], self.__config['TIMEOUT'].getint('imagematching'), 
                                                                        0.05, True, False)

            lower_gray = np.array([110, 110, 110])
            upper_gray = np.array([173, 173, 173])

            self.__get_gray_piece(lower_gray, upper_gray)        

            if self.__game_window_position == None:
                raise Exception("Game window position not found to solve captcha!")

            if self.__gray_piece_position == None:
                raise Exception("Gray piece position not found to solve captcha!")

            self.__windows_action_helper.click_and_hold(slide_button.x , slide_button.y)

            offset_x = 0        
            while loop:
                offset_x = offset_x + 1

                self.__windows_action_helper.move_click_hold(slide_button.x + offset_x, slide_button.y)

                desktop_image = self.__windows_action_helper.take_screenshot()

                x_screen, y_screen, w_screen, h_screen = self.__game_window_position

                game_image = desktop_image[y_screen:y_screen+h_screen,x_screen:x_screen+w_screen]

                #find place to put captcha
                game_img = cv2.medianBlur(game_image, 5)

                x_piece,y_piece,w_piece,h_piece = self.__gray_piece_position

                gray_piece = game_img[y_piece:y_piece+h_piece,x_piece:x_piece+w_piece]
                mask_piece = cv2.inRange(gray_piece, lower_gray, upper_gray)
                result = np.where(mask_piece == 255)

                if result[0].size <= self.__config['IMAGEDETECTION'].getint('captcha_piece_release') or slide_button.x + offset_x > (x_screen + w_screen) * 0.75:
                    self.__windows_action_helper.release_click(slide_button.x + offset_x, slide_button.y)
                    loop = False

            captcha_match = self.__image_helper.wait_until_match_is_found(self.__windows_action_helper.take_screenshot, [], self.__config['TEMPLATES']['robot_message'], 2, 0.05, False, False)
            if captcha_match == None:
                break


