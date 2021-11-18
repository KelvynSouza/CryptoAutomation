import cv2
import numpy as np
import time
import threading
import logging
import traceback
from configparser import ConfigParser
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.action_chains import ActionChains
from web_manipulation.connect_to_wallet import ConnectWallet
from .helper import ImageHelper
from crypto_automation.shared.thread_helper import Thread
import win32api, win32con
from win32con import *
from crypto_automation.web_manipulation.helper import SeleniumHelper

#Scroll one up


class GameStatusWatcher:
    def __init__(self, webdriver: WebDriver, config: ConfigParser, wallethelper: ConnectWallet):
        self.webdriver = webdriver
        self.image_helper = ImageHelper()
        self.__selenium_helper = SeleniumHelper(config)
        self.__config = config        
        self.wallet_helper = wallethelper
        self.lock = threading.Lock()
  

    def start_game(self):
        self.wallet_helper.configure_wallet()

        self.webdriver.get(self.__config['URL']['bomb_crypto'])  

        self.__connect_wallet_and_start()

        error_handling = Thread(self.__thread_safe, self.__verify_and_handle_game_error, self.__config['RETRY'].getint('verify_error'))
        newmap_handling = Thread(self.__thread_safe, self.__verify_and_handle_newmap, self.__config['RETRY'].getint('verify_newmap'))
        hero_handling = Thread(self.__thread_safe, self.__verify_and_handle_heroes_status, self.__config['RETRY'].getint('verify_heroes_status'))


    def __connect_wallet_and_start(self, reconnect = False):
        self.__find_and_click_by_template(self.__config['TEMPLATES']['connect_wallet_button'])

        self.__security_check()

        self.wallet_helper.connect_wallet_to_game(reconnect)

        self.__find_and_click_by_template(self.__config['TEMPLATES']['MapMode'])


    def __security_check(self):
        assert self.webdriver.current_url == self.__config['URL']['bomb_crypto']


    def __verify_and_handle_game_error(self):
        error = self.__wait_until_match_is_found( self.__config['TEMPLATES']['error_message'], 2 , 0.05)
        if error:
            logging.error('Error on game, refreshing page.')
            self.webdriver.refresh()
            self.__connect_wallet_and_start(True)

        expected_screen = self.__wait_until_match_is_found( self.__config['TEMPLATES']['map_screen_validator'], 2 , 0.05)
        if expected_screen == None:
            logging.error('game on wrong page, refreshing page.')
            self.webdriver.refresh()
            self.__connect_wallet_and_start(True)


    def __verify_and_handle_newmap(self):
        newmap = self.__wait_until_match_is_found( self.__config['TEMPLATES']['newmap_button'], 2 , 0.05)
        if newmap:
            logging.warning('entering new map')
            self.__find_and_click_by_template(self.__config['TEMPLATES']['newmap_button'])


    def __verify_and_handle_heroes_status(self):
        logging.warning('Checking heroes status')        
        self.__find_and_click_by_template(self.__config['TEMPLATES']['back_button'])
        self.__find_and_click_by_template(self.__config['TEMPLATES']['heroes_icon'])
        
        timeout = self.__config['TIMEOUT'].getint('imagematching')

        if(self.__wait_until_match_is_found( self.__config['TEMPLATES']['work_active_button'], timeout, 0.02) 
        or self.__wait_until_match_is_found( self.__config['TEMPLATES']['work_button'], timeout, 0.02)):
            self.__click_all_work_buttons()

        self.__find_and_click_by_template(self.__config['TEMPLATES']['exit_button'])
        self.__find_and_click_by_template(self.__config['TEMPLATES']['MapMode'])


    def __click_all_work_buttons(self):
        result_match = self.__wait_all_until_match_is_found(self.__config['TEMPLATES']['work_button'], 25, 0.02)

        count = 0
        while len(result_match) == 0 and count <= 2:
            result_active_match = self.__wait_all_until_match_is_found(self.__config['TEMPLATES']['work_active_button'], 25, 0.02)

            if(result_active_match):
                first_active_button_x, first_active_button_y  = result_active_match[0]

                self.__click_and_scroll_down(first_active_button_x, first_active_button_y)            

                result_match = self.__wait_all_until_match_is_found(self.__config['TEMPLATES']['work_button'], 25, 0.02)

            count +=1


        while len(result_match):
            for (x, y) in result_match:
                self.__click_element_by_position(x, y)
                time.sleep(0.5)
            
            first_button_x, first_button_y = result_match[0]
            
            self.__click_and_scroll_down(first_button_x, first_button_y)

            result_match = self.__wait_all_until_match_is_found(self.__config['TEMPLATES']['work_button'], 25, 0.02)


#region Util
    def __find_and_click_by_template(self, template_path, confidence_level = 0.1):
        result_match = self.__wait_until_match_is_found(template_path, self.__config['TIMEOUT'].getint('imagematching'), confidence_level)

        if result_match:
            self.__click_element_by_position(result_match.x, result_match.y)


    def __find_all_and_click_by_template(self, template_path):
        result_match = self.__wait_all_until_match_is_found(template_path, self.__config['TIMEOUT'].getint('imagematching'))

        if result_match:
            for (x, y) in result_match:
                self.__click_element_by_position(x, y)
                time.sleep(0.3)


    def __wait_until_match_is_found(self, template_path, timeout, confidence_level = 0.1): 
        duration = 0
        result = None        
        template = cv2.imread(template_path)    

        while result == None and duration < timeout:
            time.sleep(1)
            duration += 1
            website_picture = self.__selenium_screenshot_to_opencv() 
            result = self.image_helper.find_exact_match_position(website_picture, template, confidence_level)  

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
        y_body_offset = -(zero_elem.size['height']/2)+self.__config['IMAGEDETECTION'].getint('click_y_offset')

        actions = ActionChains(self.webdriver)
        actions.move_to_element(zero_elem)
        actions.move_by_offset(x_body_offset, y_body_offset).perform()
        actions.move_by_offset(x_position, y_position).click().perform()


    def __click_and_scroll_down(self, x, y):
        win32api.SetCursorPos((x, y))
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,x, y,0,0)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,x, y,0,0)   
        for x in range(self.__config['IMAGEDETECTION'].getint('scroll_intensity')):  
            win32api.mouse_event(win32con.MOUSEEVENTF_WHEEL, 0, 0, -1, 0)

    #usage example: self.__thread_sensitive(method, 2, ['spam'], {'ham': 'ham'})
    def __thread_safe(self, method, retrytime, positional_arguments = None, keyword_arguments = None):
        while True:            
            with self.lock:
                try:
                    if positional_arguments:
                        method(*positional_arguments)
                    elif keyword_arguments:
                        method(**keyword_arguments)
                    elif positional_arguments and keyword_arguments: 
                        method(*positional_arguments, **keyword_arguments)
                    else:
                        method()
                except BaseException as ex:
                    logging.error('Error:' + traceback.format_exc())                   
                    self.__restart_driver()
            time.sleep(retrytime) 


    def __restart_driver(self):
        logging.warning('Restarting automation:')
        self.webdriver.quit()
        self.webdriver = self.__selenium_helper.setup_driver()
        self.wallet_helper.configure_wallet()
        self.webdriver.get(self.__config['URL']['bomb_crypto']) 
        self.__connect_wallet_and_start()
#endregion