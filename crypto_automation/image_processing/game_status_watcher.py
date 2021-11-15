from configparser import ConfigParser
import cv2
import numpy as np
import time
import threading
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.action_chains import ActionChains
from web_manipulation.connect_to_wallet import ConnectWallet
from .helper import ImageHelper
from ..shared.thread_helper import Thread

class GameStatusWatcher:
    def __init__(self, webdriver: WebDriver, config: ConfigParser, wallethelper: ConnectWallet):
        self.webdriver = webdriver
        self.__config = config
        self.image_helper = ImageHelper()
        self.wallet_helper = wallethelper
        self.lock = threading.Lock()


    def start_game(self):
        self.wallet_helper.configure_wallet()

        self.webdriver.get(self.__config['URL']['BombCrypto'])  

        self.__connect_wallet_and_start()

        error_handling = Thread(self.__thread_safe, [self.__verify_and_handle_game_error, self.__config['RETRY'].getint('VerifyError')])
        newmap_handling = Thread(self.__thread_safe, [self.__verify_and_handle_newmap, self.__config['RETRY'].getint('VerifyNewMap')])


    def __connect_wallet_and_start(self):
        self.__find_and_click_by_template(self.__config['TEMPLATES']['ConnectWalletButton'])

        self.__security_check()

        self.wallet_helper.connect_wallet_to_game()

        self.__find_and_click_by_template(self.__config['TEMPLATES']['MapMode'])


    def __security_check(self):
        assert self.webdriver.current_url == self.__config['URL']['BombCrypto']


    def __verify_and_handle_game_error(self):
        error = self.__wait_until_match_is_found( self.__config['TEMPLATES']['ErrorMessage'], 2 )
        if error:
            self.__find_and_click_by_template(self.__config['TEMPLATES']['OkButton' ])
            self.__connect_wallet_and_start()


    def __verify_and_handle_newmap(self):
        newmap = self.__wait_until_match_is_found( self.__config['TEMPLATES']['NewMapButton'], 2 )
        if newmap:
            self.__find_and_click_by_template(self.__config['TEMPLATES']['NewMapButton'])


#region Util
    def __find_and_click_by_template(self, template_path):
        result_match = self.__wait_until_match_is_found(template_path, self.__config['TIMEOUT'].getint('ImageMatching'))

        if result_match:
            self.__click_element_by_position(result_match.x, result_match.y)


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