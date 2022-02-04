import configparser
import cv2
import numpy as np
from crypto_automation.app.commands.chat_bot_command import ChatBotCommand
import crypto_automation.app.shared.log_helper as log 
from crypto_automation.app.shared.image_processing_helper import ImageHelper
from crypto_automation.app.shared.numbers_helper import random_number_between
from crypto_automation.app.shared.thread_helper import Job
from crypto_automation.app.shared.windows_action_helper import WindowsActionsHelper


class CaptchaSolver:
    def __init__(self, config: configparser, image_helper: ImageHelper, action_helper: WindowsActionsHelper, chat_bot: ChatBotCommand):
        self.__config = config
        self.__image_helper = image_helper
        self.__windows_action_helper = action_helper        
        self.__captcha_contours = None
        self.__chat_bot = chat_bot

    def solve_captcha(self): 
        log.warning("Started solving captcha!", self.__chat_bot)
        if self.__captcha_contours == None:
           self.__captcha_contours = self.get_captcha_window_contour(self.get_game_window_image()) 

        captcha_x, captcha_y, captcha_w, captcha_h = self.__captcha_contours

        self.success = False
        for l in range(3): 
            slide_button = self.__image_helper.wait_until_match_is_found(self.__windows_action_helper.take_screenshot, 
                                                                [], self.__config['TEMPLATES']['captcha_slide'], self.__config['TIMEOUT'].getint('imagematching'), 
                                                                    0.02, True, False)   
            
            captcha_image = self.get_game_window_image()[captcha_y:captcha_y+captcha_h,captcha_x:captcha_x+captcha_w]            
            
            true_captcha_numbers = self.get_correct_captcha_number()

            slide_width = self.get_slide_width(self.__captcha_contours)            
            
            self.__windows_action_helper.click_and_hold(slide_button.x, slide_button.y)

            first_slide_movement = round(slide_width * 0.25)
            self.__windows_action_helper.move_to(slide_button.x + first_slide_movement, slide_button.y)
            self.__windows_action_helper.move_to(slide_button.x , slide_button.y)
            
            slide_movement = 0
           
            for movement in range(0, slide_width, 10):
                slide_movement = movement
                captcha_image = self.get_game_window_image()[captcha_y:captcha_y+captcha_h,captcha_x:captcha_x+captcha_w]

                digits_to_validate = self.get_numbers_to_compare(captcha_image)                

                if digits_to_validate == true_captcha_numbers:
                    self.success = True
                    break

                if self.success == False:                                          
                    self.__windows_action_helper.move_to(slide_button.x + movement, slide_button.y)  
            
                
            if self.success:
                self.__windows_action_helper.release_click(slide_button.x + slide_movement, slide_button.y - 100) 
                captcha_match = self.__image_helper.wait_until_match_is_found(self.__windows_action_helper.take_screenshot, [], self.__config['TEMPLATES']['robot_message'], 5, 0.05, False, False)
                if captcha_match:   
                    self.success = False
                    continue
                else: 
                    log.warning("Captcha solved successfully!", self.__chat_bot)
                    break
            else:
                self.__windows_action_helper.release_click(slide_button.x + slide_movement, slide_button.y)
                metamask = self.__image_helper.wait_until_match_is_found(self.__windows_action_helper.take_screenshot, [], self.__config['TEMPLATES']['metamask_welcome_text'], 5, 0.02)
                if metamask:
                    log.warning("Captcha solved successfully!", self.__chat_bot)
                    break

            if l == 2 and self.success == False:
                raise Exception("Couldn't solve captcha!")


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
        
        result = self.getting_rectangle_countours(mask_slide, 20, 40, 0, 0)
        _,_,w,_ = result[0]

        if w < 1:
            raise Exception("Couldn't get slide width!")

        return w


    def get_numbers_to_compare(self, captcha_image):
        #get numbers to validate
        digits_to_validate = list()
        for number in range(10):
            template = cv2.imread(self.__config['TEMPLATES'][f"simple_{number}"])
            position = self.__image_helper.find_exact_match_position(template, captcha_image, True, 0.05)
            if position:
                digits_to_validate.append((number, position))

        digits_to_validate.sort(key=lambda tup: tup[1].x) 

        return [(digit[0], digit[1][0]) for digit in zip(range(len(digits_to_validate)), digits_to_validate)]


    signal = False
    final_mask = []
    def watch_and_treat_captcha_screen(self):
        global signal
        global final_mask
        captcha_x, captcha_y, captcha_w, captcha_h = self.__captcha_contours

        screenshots = list()
        while signal:
            screenshots.append(self.get_game_window_image()[captcha_y:captcha_y+captcha_h,captcha_x:captcha_x+captcha_w])

        final_mask = np.zeros((captcha_h, captcha_w), np.uint8)
        for screenshot in screenshots:
            mask = cv2.inRange(screenshot, (180,180,180), (220, 230, 245))
            final_mask = cv2.add(final_mask, mask)

        kernel = cv2.getStructuringElement(cv2.MORPH_RECT,(5,5))        
        final_mask = cv2.morphologyEx(final_mask, cv2.MORPH_OPEN, kernel)
    
        cv2.dilate(final_mask, kernel, final_mask, iterations=2)
        final_mask = cv2.morphologyEx(final_mask, cv2.MORPH_CLOSE, kernel, iterations=1)   
        cv2.erode(final_mask, kernel, final_mask, iterations=2)


    def get_correct_captcha_number(self):
        global signal
        global final_mask

        game_x, game_y, _, _ = self.__game_window_position
        captcha_x, captcha_y, captcha_w, captcha_h = self.__captcha_contours
        
        signal = True
        watch_captcha_reveal = Job(self.watch_and_treat_captcha_screen, 0, True, True)
        watch_captcha_reveal.start()

        x_start = game_x+captcha_x
        x_end = game_x+captcha_x+captcha_w
        y_start = round((game_y+captcha_y) + ((game_y+captcha_y) * 0.1))
        y_end = round((game_y+captcha_y+captcha_h) - ((game_y+captcha_y+captcha_h) * 0.15))      
        for y in range(y_start, y_end, 20):                           
            self.__windows_action_helper.move_to(x_start, y, random_number_between(0.5, 0.7))
            self.__windows_action_helper.move_to(x_end, y, random_number_between(1, 1.5), False)

        signal = False
        watch_captcha_reveal.join()        
       
        digits_to_validate = list()
                    
        for number in range(10):
            template = cv2.imread(self.__config['TEMPLATES'][f"magnifier_{number}"])
            grey_digit_template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)                
            _, thresh_digit_template = cv2.threshold(grey_digit_template, 254, 255, cv2.THRESH_BINARY)  
            
            position = self.__image_helper.find_exact_match_position(final_mask, thresh_digit_template, False, 0.20)
            if position:
                digits_to_validate.append((number, position))        
        
        digits_to_validate.sort(key=lambda tup: tup[1].x) 
        
        if len(digits_to_validate) != 3:
            raise Exception("Captcha true numbers not found")

        return [(digit[0], digit[1][0]) for digit in zip(range(len(digits_to_validate)), digits_to_validate)]