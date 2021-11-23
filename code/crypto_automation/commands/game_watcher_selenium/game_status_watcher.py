import time
import threading
import logging
import traceback
from win32con import *
from crypto_automation.commands.image_processing.helper import ImageHelper
from crypto_automation.commands.shared.thread_helper import Thread
from crypto_automation.commands.web_manipulation.helper import SeleniumHelper
from crypto_automation.commands.windows_actions.helper import WindowsActionsHelper
from configparser import ConfigParser
from selenium.webdriver.chrome.webdriver import WebDriver
from .connect_to_wallet import ConnectWallet


class GameStatusWatcherSelenium:
    def __init__(self, webdriver: WebDriver, config: ConfigParser, wallethelper: ConnectWallet):
        self.webdriver = webdriver        
        self.__config = config        
        self.wallet_helper = wallethelper
        self.lock = threading.Lock()
        self.__image_helper = ImageHelper()
        self.__selenium_helper = SeleniumHelper(config)
        self.__windows_action_helper = WindowsActionsHelper(config)
  

    def start_game(self):
        self.wallet_helper.configure_wallet()

        self.webdriver.get(self.__config['COMMON']['bomb_crypto_url'])  

        self.__connect_wallet_and_start()

        error_handling = Thread(self.__thread_safe, self.__verify_and_handle_game_error, self.__config['RETRY'].getint('verify_error'))
        newmap_handling = Thread(self.__thread_safe, self.__verify_and_handle_newmap, self.__config['RETRY'].getint('verify_newmap'))
        hero_handling = Thread(self.__thread_safe, self.__verify_and_handle_heroes_status, self.__config['RETRY'].getint('verify_heroes_status'))


    def __connect_wallet_and_start(self, reconnect = False):
        self.__find_and_click_by_template(self.__config['TEMPLATES']['connect_wallet_button'])

        self.__security_check()

        self.wallet_helper.connect_wallet_to_game(reconnect)

        self.__find_and_click_by_template(self.__config['TEMPLATES']['MapMode'])

        self.__image_helper.wait_until_match_is_found(self.__selenium_helper.selenium_screenshot_to_opencv, [self.webdriver], self.__config['TEMPLATES']['map_screen_validator'], 2 , 0.05, True)


    def __security_check(self):
        assert self.webdriver.current_url == self.__config['COMMON']['bomb_crypto_url']


    def __verify_and_handle_game_error(self):
        error = self.__image_helper.wait_until_match_is_found(self.__selenium_helper.selenium_screenshot_to_opencv, [self.webdriver], self.__config['TEMPLATES']['error_message'], 2 , 0.05)
        if error:
            logging.error('Error on game, refreshing page.')
            self.webdriver.refresh()
            self.__connect_wallet_and_start(True)

        expected_screen = self.__image_helper.wait_until_match_is_found(self.__selenium_helper.selenium_screenshot_to_opencv, [self.webdriver], self.__config['TEMPLATES']['map_screen_validator'], 2 , 0.05)
        if expected_screen == None:
            logging.error('game on wrong page, refreshing page.')
            self.webdriver.refresh()
            self.__connect_wallet_and_start(True)


    def __verify_and_handle_newmap(self):
        newmap = self.__image_helper.wait_until_match_is_found(self.__selenium_helper.selenium_screenshot_to_opencv, [self.webdriver], self.__config['TEMPLATES']['newmap_button'], 2 , 0.05)
        if newmap:
            logging.warning('entering new map')
            self.__find_and_click_by_template(self.__config['TEMPLATES']['newmap_button'])


    def __verify_and_handle_heroes_status(self):
        logging.warning('Checking heroes status')        
        self.__find_and_click_by_template(self.__config['TEMPLATES']['back_button'])
        self.__find_and_click_by_template(self.__config['TEMPLATES']['heroes_icon'])
        
        timeout = self.__config['TIMEOUT'].getint('imagematching')

        if(self.__image_helper.wait_until_match_is_found(self.__selenium_helper.selenium_screenshot_to_opencv, [self.webdriver], self.__config['TEMPLATES']['work_active_button'], timeout, 0.02) 
        or self.__image_helper.wait_until_match_is_found(self.__selenium_helper.selenium_screenshot_to_opencv, [self.webdriver], self.__config['TEMPLATES']['work_button'], timeout, 0.02)):
            self.__click_all_work_buttons()

        self.__find_and_click_by_template(self.__config['TEMPLATES']['exit_button'])
        self.__find_and_click_by_template(self.__config['TEMPLATES']['MapMode'])
        self.__image_helper.wait_until_match_is_found(self.__selenium_helper.selenium_screenshot_to_opencv, [self.webdriver], self.__config['TEMPLATES']['map_screen_validator'], 2 , 0.05, True)


    def __click_all_work_buttons(self):
        result_match = self.__image_helper.wait_all_until_match_is_found(self.__selenium_helper.selenium_screenshot_to_opencv, [self.webdriver], self.__config['TEMPLATES']['work_button'], 2, 0.02)

        count = 0
        while len(result_match) == 0 and count <= 5:
            result_active_match = self.__image_helper.wait_all_until_match_is_found(self.__selenium_helper.selenium_screenshot_to_opencv, [self.webdriver],self.__config['TEMPLATES']['work_active_button'], 25, 0.02)
            if result_active_match:
                last_active_button_x, last_active_button_y  = result_active_match[len(result_active_match)-1]
                self.__windows_action_helper.click_and_scroll_down(last_active_button_x, last_active_button_y)
                result_match = self.__image_helper.wait_all_until_match_is_found(self.__selenium_helper.selenium_screenshot_to_opencv, [self.webdriver], self.__config['TEMPLATES']['work_button'], 25, 0.02)
            count += 1

        count = 0
        while len(result_match) > 0 and count <= 5:                    
            for (x, y) in result_match:
                self.__selenium_helper.click_element_by_position(self.webdriver, x, y)
                time.sleep(0.5)            
            last_button_x, last_button_y = result_match[len(result_match)-1]            
            self.__windows_action_helper.click_and_scroll_down(last_button_x, last_button_y)
            result_match = self.__image_helper.wait_all_until_match_is_found(self.__selenium_helper.selenium_screenshot_to_opencv, [self.webdriver], self.__config['TEMPLATES']['work_button'], 25, 0.02)

            count +=1


#region Util
    def __find_and_click_by_template(self, template_path, confidence_level = 0.1):
        result_match = self.__image_helper.wait_until_match_is_found(self.__selenium_helper.selenium_screenshot_to_opencv, [self.webdriver], template_path, self.__config['TIMEOUT'].getint('imagematching'), confidence_level)

        if result_match:
            self.__selenium_helper.click_element_by_position(self.webdriver, result_match.x, result_match.y)


    def __find_all_and_click_by_template(self, template_path):
        result_match = self.__image_helper.wait_all_until_match_is_found(self.__selenium_helper.selenium_screenshot_to_opencv, [self.webdriver], template_path, self.__config['TIMEOUT'].getint('imagematching'))

        if result_match:
            for (x, y) in result_match:
                self.__selenium_helper.click_element_by_position(self.webdriver, x, y)
                time.sleep(0.3)
  

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
        logging.warning('Restarting automation.')
        self.webdriver.quit()
        self.webdriver = self.__selenium_helper.setup_driver()
        self.wallet_helper.configure_wallet()
        self.webdriver.get(self.__config['COMMON']['bomb_crypto_url']) 
        self.__connect_wallet_and_start()
#endregion