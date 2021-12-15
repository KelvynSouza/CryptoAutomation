import configparser
import cv2
import numpy as np
import time
import threading
from matplotlib import pyplot as plt
from crypto_automation.commands.image_processing.helper import ImageHelper
from crypto_automation.commands.shared.thread_helper import Thread
from crypto_automation.commands.shared.os_helper import create_log_folder
from crypto_automation.commands.windows_actions.helper import WindowsActionsHelper


class TestCaptchaSolver:
    def __init__(self, config: configparser):
        self.__config = config
        self.__image_helper = ImageHelper()
        self.__windows_action_helper = WindowsActionsHelper(config, self.__image_helper)
        self.get_game_window()
        self.__captcha_contours = None
        self.lock = threading.Lock()


    def run(self):        
        if self.__captcha_contours == None:
           self.__captcha_contours = self.get_captcha_window_contour(self.get_game_window_image()) 

        captcha_x, captcha_y, captcha_w, captcha_h = self.__captcha_contours

        self.success = False
        for l in range(4): 
            slide_button = self.__image_helper.wait_until_match_is_found(self.__windows_action_helper.take_screenshot, 
                                                                [], self.__config['TEMPLATES']['captcha_slide'], self.__config['TIMEOUT'].getint('imagematching'), 
                                                                    0.05, False, False)   
            
            captcha_image = self.get_game_window_image()[captcha_y:captcha_y+captcha_h,captcha_x:captcha_x+captcha_w]
            
            
            true_captcha_numbers = self.get_correct_captcha_number()

            slide_width = self.get_slide_width(self.__captcha_contours)            
            
            self.__windows_action_helper.click_and_hold(slide_button.x, slide_button.y)

            first_slide_movement = round(slide_width * 0.25)
            self.__windows_action_helper.move_to(slide_button.x + first_slide_movement, slide_button.y)
            self.__windows_action_helper.move_to(slide_button.x , slide_button.y)          

            
            slide_movement = 0 
            iteration = 0

            #validate phases of captcha
            while self.success == False and iteration < 5: 
                captcha_image = self.get_game_window_image()[captcha_y:captcha_y+captcha_h,captcha_x:captcha_x+captcha_w]

                digits_to_validate = self.get_numbers_to_compare(captcha_image)

                if(digits_to_validate):
                    self.success = True

                if self.success == False:
                    iteration += 1  
                    if iteration < 5:                        
                        slide_movement += round(slide_width * 0.25)
                        self.__windows_action_helper.move_to(slide_button.x + slide_movement, slide_button.y)                     
                                      
            
            if self.success:
                self.__windows_action_helper.release_click(slide_button.x + slide_movement, slide_button.y - 100) 
                captcha_match = self.__image_helper.wait_until_match_is_found(self.__windows_action_helper.take_screenshot, [], self.__config['TEMPLATES']['robot_message'], 5, 0.05, False, False)
                if captcha_match:   
                    self.success = False
                    continue
                else:            
                    break
            else:
                self.__windows_action_helper.release_click(slide_button.x + slide_movement, slide_button.y)
            
                

    def show_info(self, image, original=False, image_name = "Imagem"):
        print('-----------------------------------------------------')  
        print(image_name)  
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


    def getting_rectangle_countours(self, image_treated, h_min = None, h_max = None, w_min = None, w_max = None, find_mode = cv2.RETR_CCOMP, reduce_box_size_by = 0):
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
                valid_contours.append((x+reduce_box_size_by,y+reduce_box_size_by,w-(reduce_box_size_by*2),h-(reduce_box_size_by*2)))

        return valid_contours

   
    def draw_rectangles_in_image(self, image, contours, border_color = (0, 0, 0), thickness=-1, space_between_contour_image = 0):
        for x,y,w,h in contours:
            x -= space_between_contour_image
            y -= space_between_contour_image
            w += space_between_contour_image
            h += space_between_contour_image
            cv2.rectangle(image, (x, y), (x + w, y + h), border_color, thickness)
        return image


    def get_game_window(self):
        desktop_image =  self.__windows_action_helper.take_screenshot()
        desktop_image_gray = cv2.cvtColor(desktop_image, cv2.COLOR_BGR2GRAY)
        _, thresh_image = cv2.threshold(desktop_image_gray, 30, 255, cv2.THRESH_BINARY)        
        edg_img = cv2.Canny(thresh_image, 225, 255)
        
        contours = self.getting_rectangle_countours(edg_img, 500, 700, 400, 1000) 
        
        self.__game_window_position = contours[0]


    def get_game_window_image(self):
        desktop_image = self.__windows_action_helper.take_screenshot()
        x_screen, y_screen, w_screen, h_screen = self.__game_window_position
        return desktop_image[y_screen:y_screen+h_screen,x_screen:x_screen+w_screen]


    def get_captcha_window_contour(self, captcha_image):
        captcha_image_gray = cv2.cvtColor(captcha_image, cv2.COLOR_BGR2GRAY)
        _, thresh_image = cv2.threshold(captcha_image_gray, 97, 255, cv2.THRESH_BINARY)        
        edg_img = cv2.Canny(thresh_image, 225, 255)
        captcha_window_contours = self.getting_rectangle_countours(edg_img, 350, 400, 500, 600, reduce_box_size_by=10) 
        if len(captcha_window_contours) > 0:
            return captcha_window_contours[0]
        else:
            return None        


    def get_slide_width(self, captcha_contours):
        captcha_x, captcha_y, captcha_w, captcha_h = captcha_contours

        slide_info = self.get_game_window_image()[captcha_y:captcha_y+captcha_h,captcha_x:captcha_x+captcha_w]
        mask_slide = cv2.inRange(slide_info, (61,81,129), (68,89,136))        
        self.show_info(mask_slide, True)
        self.show_info(slide_info, True)
        result = self.getting_rectangle_countours(mask_slide, 20, 40, 0, 0)
        _,_,w,_ = result[0]
        return w


    def get_numbers_to_compare(self, captcha_image):
        #get numbers to validate
        digits_to_validate = list()
        for number in range(10):
            template = cv2.imread(self.__config['TEMPLATES'][f"simple_{number}"])
            position = self.__image_helper.find_exact_match_position(template, captcha_image, True, 0.01)
            if position:
                digits_to_validate.append((number, position))

        digits_to_validate.sort(key=lambda tup: tup[1].x) 

        return [(digit[0], digit[1][0]) for digit in zip(range(len(digits_to_validate)), digits_to_validate)]


    def get_correct_captcha_number(self):
        game_x, game_y, _, _ = self.__game_window_position
        captcha_x, captcha_y, captcha_w, captcha_h = self.__captcha_contours
        
        y_start = round((game_y+captcha_y) + ((game_y+captcha_y) * 0.1))
        y_end = round((game_y+captcha_y+captcha_h) - ((game_y+captcha_y+captcha_h) * 0.15))
        final_mask = np.zeros((captcha_h, captcha_w), np.uint8)
        for y in range(y_start, y_end, 10):
            for x in range(game_x+captcha_x, (game_x+captcha_x+captcha_w), 10):                
                self.__windows_action_helper.move_to(x, y, True)
                captcha_image = self.get_game_window_image()[captcha_y:captcha_y+captcha_h,captcha_x:captcha_x+captcha_w]
                mask = cv2.inRange(captcha_image, (200,200,200), (220, 230, 245))
                final_mask = cv2.add(final_mask, mask)
        
        
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT,(3,3))        
        final_mask = cv2.morphologyEx(final_mask, cv2.MORPH_OPEN, kernel)        
        
        digits_to_validate = list()
        for number in range(10):
            template = cv2.imread(self.__config['TEMPLATES'][f"simple_{number}"])
            _, thresh_image = cv2.threshold(template, 254, 255, cv2.THRESH_BINARY) 
            position = self.__image_helper.find_exact_match_position(final_mask, thresh_image, False, 0.01)
            if position:
                digits_to_validate.append((number, position))

        digits_to_validate.sort(key=lambda tup: tup[1].x) 

        digits_to_validate = [(digit[0], digit[1][0]) for digit in zip(range(len(digits_to_validate)), digits_to_validate)]
        


    

config_filename = "..\\settings.ini"

config = configparser.ConfigParser(
    interpolation=configparser.ExtendedInterpolation())
config.read(config_filename)
config['TEMPLATES']['game_images_path'] = '..\\resources\\images\\game'
config['TEMPLATES']['captcha_image_path'] = '..\\resources\\images\\game\\captcha'
config['TEMPLATES']['captcha_simple_image_path'] = '..\\resources\\images\\game\\captcha\\simple'
config['TEMPLATES']['captcha_complex_image_path'] = '..\\resources\\images\\game\\captcha\\complex'

create_log_folder(config['COMMON']['log_path'],
                  config['COMMON']['screenshots_path'])

asd = TestCaptchaSolver(config)
asd.run()


