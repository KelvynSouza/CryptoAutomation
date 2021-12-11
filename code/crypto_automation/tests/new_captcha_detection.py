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
        self.show_info(game_image, image_name="Original")

        #convert image to gray
        desktop_game_gray = cv2.cvtColor(game_image, cv2.COLOR_BGR2GRAY)        

        #threshould it for better digits detection
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
        
        #fill numbers to extract for better extraction of the captcha 
        cv2.drawContours(thresh_image, newContours, -1, (255,255,255), thickness=-1) 
        cv2.drawContours(game_image, newContours, -1, (82,112,181), thickness=-1)
        
        #clean the number for better detection with ocr
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(3,3))
        erosion = cv2.erode(thresh_image, kernel, iterations = 3)
        _, erosion = cv2.threshold(erosion, 0, 255, cv2.THRESH_BINARY_INV)
        self.show_info(erosion)
                 
        #get numbers with ocr
        digits_to_validate = pytesseract.image_to_string(erosion, config=custom_config)
        digits_to_validate = digits_to_validate[:3]
        print(f"OCR value captured: {digits_to_validate}" )
        
        #get white number on background
        mask = cv2.inRange(game_image, (250,250,250), (255,255,255))

        kernel = cv2.getStructuringElement(cv2.MORPH_RECT,(3,3))        
        to_validate_number = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=2)

        cleaning_kernel = cv2.getStructuringElement(cv2.MORPH_RECT,(3,3))    
        to_locale_position = cv2.morphologyEx(mask, cv2.MORPH_OPEN, cleaning_kernel, iterations=3)

        #remove noise from image
        rect_contours = self.getting_rectangle_countours(to_locale_position, 0,20,0,20)
        to_locale_position = self.draw_rectangles_in_image(to_locale_position, rect_contours)         
        
        self.show_info(to_validate_number,  image_name="Image to validate number")
        self.show_info(to_locale_position,  image_name="Image to get number position")

        #Close gaps from corrupted numbers
        #One idea is start with low x value for structure and increase until we have only 3 contours 
        # if it turns into 2 or less, we give up the image and try the take another        
        aux_y = 0
        for y in range(55, 80, 2):
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT,(1, y))
            to_locale_position_morph = cv2.morphologyEx(to_locale_position, cv2.MORPH_CLOSE, kernel)
            contours = self.getting_rectangle_countours(to_locale_position_morph, 90, 200, 10, 200)  

            if len(contours) == 3:
                aux_y = y
                break  

        temp_contours = list()
        for x in range(1, 30, 2):
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT,(x, aux_y if aux_y > 0 else 60))
            to_locale_position_morph = cv2.morphologyEx(to_locale_position, cv2.MORPH_CLOSE, kernel)
            contours = self.getting_rectangle_countours(to_locale_position_morph, 90, 200, 10, 200)  

            if len(contours) == 3:
                temp_contours = contours                
            elif len(contours) < 3:
                if len(temp_contours) > 0:
                    contours = temp_contours
                    break
        
        if len(contours) < 3:
            raise Exception("Error getting numbers position")

        #fix border if its near the image's border
        contours = [(contour[0], 20 if contour[1] == 0 else contour[1], contour[2], contour[3]) for contour in contours]
        
        #Sort contours position to be equals to text position
        contours.sort(key=lambda tup: tup[0])       

        self.show_info(to_locale_position_morph)
        self.draw_rectangles_in_image(game_image, contours,  (255,0,0), 2)
        self.show_info(game_image)

        for i in range(0, len(digits_to_validate)):
            #prepare template to compare
            template = cv2.imread(config['TEMPLATES'][digits_to_validate[i]])
            grey_digit_template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY) 
            _, thresh_digit_template = cv2.threshold(grey_digit_template, 200, 255, cv2.THRESH_BINARY)            

            x,y,w,h = contours[i]
            resized_template = cv2.resize(thresh_digit_template, (w,h) , interpolation = cv2.INTER_LANCZOS4)

            image_to_validate = to_validate_number[y:y+h, x:x+w] + resized_template
            self.show_info(image_to_validate)

            result = self.__image_helper.find_exact_match_position(resized_template, image_to_validate, False, 0.2)

            if result:
                print(f"Success letter: {digits_to_validate[i]}")
            else:
                print(f"Letter '{digits_to_validate[i]}' not found")









pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'
custom_config = r'--oem 3 --psm 10 -c tessedit_char_whitelist=0123456789'
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

