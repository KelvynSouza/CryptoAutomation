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

    def draw_rectangles_in_image(self, image, contours):
        for x,y,w,h in contours:
            cv2.rectangle(image, (x, y), (x + w, y + h), (0, 0, 0), -1)
        return image
    

    def run(self):

        game_image = cv2.imread("../resources/images/test/captcha_new/captcha_2.png")         

        desktop_game_gray = cv2.cvtColor(game_image, cv2.COLOR_BGR2GRAY)           
        
        
        _, thresh_image = cv2.threshold(desktop_game_gray, 91, 255, cv2.THRESH_BINARY_INV)                 

        #Create a structure to aggregate incomplete elements
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(3,3))
        cv2.dilate(thresh_image,kernel,thresh_image, iterations = 1)

        contours, hierarchy  = cv2.findContours(thresh_image, cv2.RETR_CCOMP , cv2.CHAIN_APPROX_SIMPLE)
        hierarchy = hierarchy[0] # get the actual inner list of hierarchy descriptions
        
        newContours = list()
        for currentContour, currentHierarchy in zip(contours, hierarchy):            
            if currentHierarchy[2] < 0:
                # these are the innermost child components for the outermost,
                # you should use currentHierarchy[3] < 0
                newContours.append(currentContour)  
        
        #fill numbers to extract captcha
        cv2.drawContours(game_image, newContours, -1, (82,112,181), thickness=-1) 
        mask = cv2.inRange(game_image, (255,255,255), (255,255,255))
        
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT,(7,5))
        opening = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

        rect_contours = self.getting_rectangle_countours(opening,0,20,0,20)
        opening = self.draw_rectangles_in_image(opening, rect_contours) 
        self.show_info(opening)

        numberContours, hierarchy = cv2.findContours(opening, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        cv2.drawContours(game_image, numberContours, -1, (0,0,255), thickness=3) 

        # create hull array for convex hull points

        hull_list  = []
        # calculate points for each contour
        for i in range(len(numberContours)):
            # creating convex hull object for each contour
            hull_list.append(cv2.convexHull(numberContours[i], False))            

        drawing = np.zeros((opening.shape[0], opening.shape[1], 3), dtype=np.uint8)
        for i in range(len(numberContours)):
            color = (255, 0,0)
            cv2.drawContours(drawing, numberContours, i, color)
            cv2.drawContours(drawing, hull_list, i, color)

        self.show_info(drawing)

'''
Código exemplo para pegar area do contorno
img_contour = img.copy()
for i in range(len(contours)):
    area = cv2.contourArea(contours[i])
    if 100 < area < 10000:
        cv2.drawContours(img_contour, contours, i, (0, 0, 255), 2)
'''


config_filename = "D:\\dev\\CryptoOcrAutomation\\code\\crypto_automation\\settings.ini"

config = configparser.ConfigParser(
    interpolation=configparser.ExtendedInterpolation())
config.read(config_filename)
config['TEMPLATES']['game_images_path'] = '..\\resources\\images\\game'

create_log_folder(config['COMMON']['log_path'],
                  config['COMMON']['screenshots_path'])

asd = TestCaptchaSolver(config)
asd.run()


