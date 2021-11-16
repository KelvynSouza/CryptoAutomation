from configparser import ConfigParser
import cv2
import numpy as np
import time
import threading
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.action_chains import ActionChains
from web_manipulation.connect_to_wallet import ConnectWallet
from .helper import ImageHelper
from crypto_automation.shared.thread_helper import Thread
import win32api, win32con
from win32con import *

#Scroll one up


class GameStatusWatcher:
    def __init__(self, webdriver: WebDriver, config: ConfigParser, wallethelper: ConnectWallet):
        self.webdriver = webdriver
        self.__config = config
        self.image_helper = ImageHelper()
        self.wallet_helper = wallethelper
        self.lock = threading.Lock()


    def start_game(self):
        self.wallet_helper.configure_wallet()

        self.webdriver.get(self.__config['URL']['bomb_crypto'])  

        self.__connect_wallet_and_start()

        #error_handling = Thread(self.__thread_safe, self.__verify_and_handle_game_error, self.__config['RETRY'].getint('verify_error'))
        #newmap_handling = Thread(self.__thread_safe, self.__verify_and_handle_newmap, self.__config['RETRY'].getint('verify_newmap'))
        hero_handling = Thread(self.__thread_safe, self.__verify_and_handle_heroes_status, self.__config['RETRY'].getint('verify_heroes_status'))


    def __connect_wallet_and_start(self):
        self.__find_and_click_by_template(self.__config['TEMPLATES']['connect_wallet_button'])

        self.__security_check()

        self.wallet_helper.connect_wallet_to_game()

        self.__find_and_click_by_template(self.__config['TEMPLATES']['MapMode'])


    def __security_check(self):
        assert self.webdriver.current_url == self.__config['URL']['bomb_crypto']


    def __verify_and_handle_game_error(self):
        error = self.__wait_until_match_is_found( self.__config['TEMPLATES']['error_message'], 2 )
        if error:
            self.__find_and_click_by_template(self.__config['TEMPLATES']['ok_button'])
            self.__connect_wallet_and_start()


    def __verify_and_handle_newmap(self):
        newmap = self.__wait_until_match_is_found( self.__config['TEMPLATES']['newmap_button'], 2 )
        if newmap:
            self.__find_and_click_by_template(self.__config['TEMPLATES']['newmap_button'])


    def __verify_and_handle_heroes_status(self):        
        self.__find_and_click_by_template(self.__config['TEMPLATES']['back_button'])
        self.__find_and_click_by_template(self.__config['TEMPLATES']['heroes_icon'])

        self.__click_all_work_buttons()

        self.__find_and_click_by_template(self.__config['TEMPLATES']['exit_button'])
        self.__find_and_click_by_template(self.__config['TEMPLATES']['MapMode'])


    def __click_all_work_buttons(self):
        result_match = self.__wait_all_until_match_is_found(self.__config['TEMPLATES']['work_button'], 10, 0.02)

        if len(result_match) == 0:
            result_active_match = self.__wait_all_until_match_is_found(self.__config['TEMPLATES']['work_active_button'], 10, 0.02)

            first_active_button_x, first_active_button_y = result_active_match[0]
            last_active_button_x, last_active_button_y  = result_active_match[len(result_active_match)-1]

            zero_elem = self.webdriver.find_element_by_tag_name('body')
            x_body_active_offset = -(zero_elem.size['width']/2)
            y_body_active_offset = -(zero_elem.size['height']/2)+130

            space_to_scroll = -(last_active_button_x - first_active_button_y)


            iframe = self.webdriver.find_element_by_tag_name('iframe')

            # switch to selected iframe
            self.webdriver.switch_to.frame(iframe)

            canvas_elem = self.webdriver.find_element_by_tag_name('canvas')


            win32api.SetCursorPos((last_active_button_x, last_active_button_y))
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,last_active_button_x, last_active_button_y,0,0)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,last_active_button_x, last_active_button_y,0,0)
            #actions = ActionChains(self.webdriver)            
            #actions.move_to_element_with_offset(canvas_elem, 300, 500).pause(1).click().pause(1).perform()
            for x in range(100):  
                win32api.mouse_event(win32con.MOUSEEVENTF_WHEEL, 0, 0, -1, 0)
            #actions.move_to_element_with_offset(canvas_elem).pause(1).release().pause(1).perform()
            #actions.move_to_element(zero_elem)
            #actions.move_by_offset(x_body_active_offset, y_body_active_offset).perform()
            #actions.move_by_offset(last_active_button_x, last_active_button_y).click_and_hold().pause(2).

            self.webdriver.switch_to.default_content()
            
        result_match = self.__wait_all_until_match_is_found(self.__config['TEMPLATES']['work_button'], 10, 0.02)

        while len(result_match):

            for (x, y) in result_match:
                self.__click_element_by_position(x, y)
                time.sleep(0.3)

            first_button_x, first_button_y = result_match[0]
            last_button_x, last_button_y = result_match[len(result_match)-1]

            zero_elem = self.webdriver.find_element_by_tag_name('body')
            x_body_offset = -(zero_elem.size['width']/2)
            y_body_offset = -(zero_elem.size['height']/2)+130

            actions = ActionChains(self.webdriver)
            actions.move_to_element(zero_elem)
            actions.move_by_offset(x_body_offset, y_body_offset).perform()
            actions.move_by_offset(last_button_x, last_button_y).click_and_hold().move_by_offset(0, -(last_button_x - first_button_y)).release().perform()

            result_match = self.__wait_all_until_match_is_found(self.__config['TEMPLATES']['work_button'], 10, 0.02)


#region Util
    def __find_and_click_by_template(self, template_path):
        result_match = self.__wait_until_match_is_found(template_path, self.__config['TIMEOUT'].getint('imagematching'))

        if result_match:
            self.__click_element_by_position(result_match.x, result_match.y)


    def __find_all_and_click_by_template(self, template_path):
        result_match = self.__wait_all_until_match_is_found(template_path, self.__config['TIMEOUT'].getint('imagematching'))

        if result_match:
            for (x, y) in result_match:
                self.__click_element_by_position(x, y)
                time.sleep(0.3)


    def __wait_until_match_is_found(self, template_path, timeout): 
        duration = 0
        result = None        
        template = cv2.imread(template_path)    

        while result == None and duration < timeout:
            time.sleep(1)
            duration += 1
            website_picture = self.__selenium_screenshot_to_opencv() 
            result = self.image_helper.find_exact_match_position(website_picture, template)  

        return result


    def __wait_all_until_match_is_found(self, template_path, timeout, confidence_level = 0.1): 
        duration = 0
        result = None        
        template = cv2.imread(template_path)    

        while result == None and duration < timeout:
            time.sleep(1)
            duration += 1
            website_picture = self.__selenium_screenshot_to_opencv() 
            result = self.image_helper.find_exact_matches_position(website_picture, template, confidence_level)  

        return result


    def __selenium_screenshot_to_opencv(self):
        png = self.webdriver.get_screenshot_as_png()

        nparr = np.frombuffer(png, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        return img


    def __click_element_by_position(self, x_position, y_position):
        zero_elem = self.webdriver.find_element_by_tag_name('body')

        x_body_offset = -(zero_elem.size['width']/2)
        #caso ocorra algum problema com click baseado em image, esta pode ser a 
        #causa, por algum motivo bizarro ele tem uns 130px da borda, para 
        #validar a posição do cursor usar click_perform()
        y_body_offset = -(zero_elem.size['height']/2)+130

        actions = ActionChains(self.webdriver)
        actions.move_to_element(zero_elem)
        actions.move_by_offset(x_body_offset, y_body_offset).perform()
        actions.move_by_offset(x_position, y_position).click().perform()
        
    #usage example: self.__thread_sensitive(method, 2, ['spam'], {'ham': 'ham'})
    def __thread_safe(self, method, retrytime, positional_arguments = None, keyword_arguments = None):
        while True:
            with self.lock:
                if positional_arguments:
                    method(*positional_arguments)
                elif keyword_arguments:
                    method(**keyword_arguments)
                elif positional_arguments and keyword_arguments: 
                    method(*positional_arguments, **keyword_arguments)
                else:
                    method()
            time.sleep(retrytime) 