import configparser
import cv2
import numpy as np
import time
import pytesseract
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

   
    def draw_rectangles_in_image(self, image, contours, border_color = (0, 0, 0), thickness=-1, space_between_contour_image = 0):
        for x,y,w,h in contours:
            x -= space_between_contour_image
            y -= space_between_contour_image
            w += space_between_contour_image
            h += space_between_contour_image
            cv2.rectangle(image, (x, y), (x + w, y + h), border_color, thickness)
        return image


    def run(self):
        game_image = cv2.imread("../resources/images/test/captcha_new/captcha_6.png")         
        self.show_info(game_image)

        #convert image to gray
        desktop_game_gray = cv2.cvtColor(game_image, cv2.COLOR_BGR2GRAY) 
        self.show_info(desktop_game_gray)

        #threshould it for better digits detection
        _, thresh_image = cv2.threshold(desktop_game_gray, 91, 255, cv2.THRESH_BINARY_INV)                 
        self.show_info(thresh_image)

        #Create a structure to aggregate incomplete elements
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT,(3,3))
        cv2.dilate(thresh_image,kernel,thresh_image, iterations = 1)
        self.show_info(thresh_image)

        # get the contours and hierarchy so that we can filter only the contours from the digits
        contours, hierarchy  = cv2.findContours(thresh_image, cv2.RETR_CCOMP , cv2.CHAIN_APPROX_SIMPLE)
        hierarchy = hierarchy[0] # get the actual inner list of hierarchy descriptions
        
        newContours = list()
        for currentContour, currentHierarchy in zip(contours, hierarchy):  
            # these are the innermost child components for the outermost,
            # you should use currentHierarchy[3] < 0          
            if currentHierarchy[2] < 0:                
                newContours.append(currentContour)  
        
        #fill numbers to extract for better extraction of the captcha 
        cv2.drawContours(thresh_image, newContours, -1, (255,255,255), thickness=-1) 
        cv2.drawContours(game_image, newContours, -1, (82,112,181), thickness=-1)
        self.show_info(thresh_image)
        self.show_info(game_image)

        #clean the number for better detection with ocr
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(3,3))
        erosion = cv2.erode(thresh_image, kernel, iterations = 3)
        _, erosion = cv2.threshold(erosion, 0, 255, cv2.THRESH_BINARY_INV)
        self.show_info(erosion)
                 
        #get numbers with ocr
        digits_to_validate = pytesseract.image_to_string(erosion, config=custom_config)
        digits_to_validate = digits_to_validate[:3]
        
        mask = cv2.inRange(game_image, (250,250,250), (255,255,255))        
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT,(7,5))
        opening = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

        #remove noise from image
        rect_contours = self.getting_rectangle_countours(opening, 0,20,0,20)
        opening = self.draw_rectangles_in_image(opening, rect_contours)         
        self.show_info(opening)

        #Close gaps from corrupted numbers
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT,(31,45))
        opening = cv2.morphologyEx(opening, cv2.MORPH_CLOSE, kernel)
        self.show_info(opening)

        contours = self.getting_rectangle_countours(opening, 50,200,10,200)
        self.draw_rectangles_in_image(game_image, contours,  (255,0,0), 2)

        self.show_info(game_image)
      

pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'
custom_config = r'--oem 2 --psm 10 -c tessedit_char_whitelist=0123456789'
config_filename = "D:\\dev\\CryptoOcrAutomation\\code\\crypto_automation\\settings.ini"

config = configparser.ConfigParser(
    interpolation=configparser.ExtendedInterpolation())
config.read(config_filename)
config['TEMPLATES']['game_images_path'] = '..\\resources\\images\\game'
config['TEMPLATES']['captcha_image_path'] = '..\\resources\\images\\game\\captcha'

create_log_folder(config['COMMON']['log_path'],
                  config['COMMON']['screenshots_path'])

asd = TestCaptchaSolver(config)
asd.run()


