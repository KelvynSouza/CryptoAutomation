import cv2
import numpy as np
from .helper import ImageHelper
import time
from selenium.webdriver.common.action_chains import ActionChains

class GameStatusWatcher:
    def __init__(self, webdriver):
        self.webdriver = webdriver
        self.image_helper = ImageHelper()


    def connect_wallet_button(self):
        template_path = 'images\connect_wallet.png'

        result_match = self.__wait_until_match_is_found(template_path, 15)
        
        if result_match:
            self.__click_element_by_position(result_match.x, result_match.y)


    def start_map_mode(self):
        template_path = 'images\map_mode.png'

        result_match = self.__wait_until_match_is_found(template_path, 25)

        if result_match:
            self.__click_element_by_position(result_match.x, result_match.y)


    def find_and_click_by_template(self, template_path):
        result_match = self.__wait_until_match_is_found(template_path, 15)

        if result_match:
            self.__click_element_by_position(result_match.x, result_match.y)


#region Util
    def __wait_until_match_is_found(self, template_path, timeout): 
        result = None
        template = cv2.imread(template_path)  
        duration = 0
        while result == None and duration < timeout:
            time.sleep(1)
            duration += 1
            website_picture = self.__selenium_screenshot_to_opencv() 
            result = self.image_helper.find_exact_match_position(website_picture, template)    
        return result


    def __selenium_screenshot_to_opencv(self):
        png = self.webdriver.get_screenshot_as_png()

        nparr = np.frombuffer(png, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        return img


    def __click_element_by_position(self, x_position, y_position):
        zero_elem = self.webdriver.find_element_by_tag_name('body')

        x_body_offset = -(zero_elem.size['width']/2)
        y_body_offset = -(zero_elem.size['height']/2)+130

        actions = ActionChains(self.webdriver)
        actions.move_to_element(zero_elem)
        actions.move_by_offset(x_body_offset, y_body_offset).perform()
        actions.move_by_offset(x_position, y_position).click().perform()
        