import configparser
import cv2
import numpy as np
import time
import threading
from matplotlib import pyplot as plt
from crypto_automation.commands.image_processing.helper import ImageHelper
from crypto_automation.commands.shared.thread_helper import Job
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
        
            slide_button = self.__image_helper.wait_until_match_is_found(cv2.imread, 
                                                                [captcha_screen_test], self.__config['TEMPLATES']['captcha_slide'], self.__config['TIMEOUT'].getint('imagematching'), 
                                                                    0.05, False, False)   
            
            captcha_image = self.get_game_window_image()[captcha_y:captcha_y+captcha_h,captcha_x:captcha_x+captcha_w]

            desktop_game_gray = cv2.cvtColor(captcha_image, cv2.COLOR_BGR2GRAY) 
            _, thresh_image = cv2.threshold(desktop_game_gray, 91, 255, cv2.THRESH_BINARY_INV) 

            #Create a structure to aggregate incomplete elements
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT,(3,3))
            cv2.dilate(thresh_image,kernel,thresh_image, iterations = 1)

            # get the contours and hierarchy so that we can filter only the contours from the digits
            contours, hierarchy  = cv2.findContours(thresh_image, cv2.RETR_CCOMP , cv2.CHAIN_APPROX_SIMPLE)
            hierarchy = hierarchy[0] # get the actual inner list of hierarchy descriptions

            newContours = list()
            for currentContour, currentHierarchy in zip(contours, hierarchy):  
                # these are the innermost child components for the outermost,
                # you should use currentHierarchy[3] < 0          
                if currentHierarchy[2] < 0:                
                    newContours.append(currentContour)  

            digits_to_validate = self.get_correct_captcha_number(captcha_image)
                        
            digits_to_validate  = [(digit[0], digit[1][0]) for digit in zip(range(len(digits_to_validate)), digits_to_validate)]

            self.__result_number_detection = digits_to_validate.copy()

            slide_width = self.get_slide_width(self.__captcha_contours)
            
            
            self.__windows_action_helper.click_and_hold(slide_button.x, slide_button.y)

            first_slide_movement = round(slide_width * 0.25)
            self.__windows_action_helper.move_to(slide_button.x + first_slide_movement, slide_button.y)
            self.__windows_action_helper.move_to(slide_button.x , slide_button.y)          

            seconds = 10
            slide_movement = 0 
            iteration = 0

            start_time = time.time()

            #validate phases of captcha
            while self.success == False and iteration < 5:                  
                
                captcha_image = self.get_game_window_image()[captcha_y:captcha_y+captcha_h,captcha_x:captcha_x+captcha_w]
                
                #fill numbers to extract for better extraction of the captcha 
                cv2.drawContours(captcha_image, newContours, -1, (82,112,181), thickness=-1) 

                mask = cv2.inRange(captcha_image, (250,250,250), (255,255,255))

                kernel = cv2.getStructuringElement(cv2.MORPH_RECT,(3,3))        
                to_validate_number = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=2)

                cleaning_kernel = cv2.getStructuringElement(cv2.MORPH_RECT,(3,3))    
                to_locale_position = cv2.morphologyEx(mask, cv2.MORPH_OPEN, cleaning_kernel, iterations=3)

                #remove noise from image
                rect_contours = self.getting_rectangle_countours(to_locale_position, 0,20,0,20)
                to_locale_position = self.draw_rectangles_in_image(to_locale_position, rect_contours)  

                #Close gaps from corrupted numbers
                #One idea is start with low x value for structure and increase until we have only 3 contours 
                # if it turns into 2 or less, we give up the image and try the take another        
                aux_y = 0
                for y in range(55, 80, 2):
                    kernel = cv2.getStructuringElement(cv2.MORPH_RECT,(1, y))
                    to_locale_position_morph = cv2.morphologyEx(to_locale_position, cv2.MORPH_CLOSE, kernel)
                    contours = self.getting_rectangle_countours(to_locale_position_morph, 100, 200, 5, 200)  

                    if len(contours) == 3:
                        aux_y = y
                        break  
                    
                temp_contours = list()
                for x in range(1, 30, 2):
                    kernel = cv2.getStructuringElement(cv2.MORPH_RECT,(x, aux_y if aux_y > 0 else 60))
                    to_locale_position_morph = cv2.morphologyEx(to_locale_position, cv2.MORPH_CLOSE, kernel)
                    contours = self.getting_rectangle_countours(to_locale_position_morph, 90, 200, 5, 200)  

                    if len(contours) == 3:
                        temp_contours = contours                
                    elif len(contours) < 3:
                        if len(temp_contours) > 0:
                            contours = temp_contours
                            break
                        
                if len(contours) != 3:                    
                    continue
                
                #fix border if its near the image's border
                contours = [(contour[0], 25 if contour[1] == 0 else contour[1], contour[2], contour[3]) for contour in contours]

                #Sort contours position to be equals to text position
                contours.sort(key=lambda tup: tup[0])                 
                
                threads = list()
                for p, i in list(self.__result_number_detection):
                    #prepare template to compare
                    threads.append(Job(self.validate_captcha, (p, i), contours, to_validate_number, slide_button, slide_movement))             
                                   
                for x in threads:
                    x.join()

                #check timeout
                current_time = time.time() 
                elapsed_time = current_time - start_time

                if self.success == False and elapsed_time > seconds :  
                    print(f"Timeout, Captcha number not found") 
                    iteration += 1  
                    if iteration < 5:
                        self.__result_number_detection = digits_to_validate.copy()
                        slide_movement += round(slide_width * 0.25)
                        self.__windows_action_helper.move_to(slide_button.x + slide_movement, slide_button.y)                      
                        start_time = time.time()               
            
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
            
                

    def validate_captcha(self, digit, contours, to_validate_number, slide_button, slide_movement):        
        p, i = digit
        #prepare template to compare
        template = cv2.imread(self.__config['TEMPLATES'][f"complex_{i}"])
        grey_digit_template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)                     
        _, thresh_digit_template = cv2.threshold(grey_digit_template, 200, 255, cv2.THRESH_BINARY) 
        x,y,w,h = self.resolve_contours_exception(i, contours[p])
        resized_template = cv2.resize(thresh_digit_template, (w,h) , interpolation = cv2.INTER_LANCZOS4)
        image_to_validate = to_validate_number[y:y+h, x:x+w] + resized_template                    
        result = self.__image_helper.find_exact_match_position(resized_template, image_to_validate, False, 0.12)
        if result:
            with self.lock:
                self.__result_number_detection.remove((p,i))
                if len(self.__result_number_detection) == 0:
                    self.success = True      
                    self.__windows_action_helper.move_to(slide_button.x + slide_movement, slide_button.y - 100)                      
                    print("success all")       
        else: 
            print(f"error getting letter: {i}")                      
            
        
                        


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
        desktop_image =  cv2.imread(captcha_screen_test)
        desktop_image_gray = cv2.cvtColor(desktop_image, cv2.COLOR_BGR2GRAY)
        _, thresh_image = cv2.threshold(desktop_image_gray, 30, 255, cv2.THRESH_BINARY)        
        edg_img = cv2.Canny(thresh_image, 225, 255)
        
        contours = self.getting_rectangle_countours(edg_img, 500, 700, 400, 1000) 
        
        self.__game_window_position = contours[0]


    def get_game_window_image(self):
        desktop_image = cv2.imread(captcha_screen_test)
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


    def get_correct_captcha_number(self, captcha_image):
        #get numbers to validate
        digits_to_validate = list()
        for number in range(10):
            template = cv2.imread(self.__config['TEMPLATES'][f"simple_{number}"])
            position = self.__image_helper.find_exact_match_position(template, captcha_image, True, 0.01)
            if position:
                digits_to_validate.append((number, position))

        digits_to_validate.sort(key=lambda tup: tup[1].x) 

        return digits_to_validate


    def resolve_contours_exception(self, number, contour):
        x,y,w,h = contour
        if number == 4:
            if(w < 25):
                x -= 40
                w += 40
        return (x,y,w,h)

    
captcha_screen_test = '../resources/images/test/captcha_new/captcha_error.png'

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


