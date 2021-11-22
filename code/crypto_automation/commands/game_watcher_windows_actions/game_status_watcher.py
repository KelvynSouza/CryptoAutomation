import numpy as np
import time
import threading
import logging
import traceback
from win32con import *
from configparser import ConfigParser
from crypto_automation.commands.image_processing.helper import ImageHelper
from crypto_automation.commands.shared.thread_helper import Thread
from crypto_automation.commands.windows_actions.helper import WindowsActionsHelper


class GameStatusWatcherActions:
    def __init__(self, config: ConfigParser):
        self.__config = config
        self.lock = threading.Lock()
        self.__image_helper = ImageHelper()
        self.__windows_action_helper = WindowsActionsHelper(config, self.__image_helper)
        

    def start_game(self):
        self.__open_chrome_and_goto_game()
        print()


    def __open_chrome_and_goto_game(self):
            self.__windows_action_helper.open_and_maximise_front_window(self.__config["WEBDRIVER"]["chrome_path"], 
                                                                        self.__config['TEMPLATES']['incognito_icon'], 
                                                                        self.__config["WEBDRIVER"]["chrome_args"])

            self.__find_and_click_by_template(self.__config['TEMPLATES']['incognito_icon'], 0.05)

            self.__find_and_write_by_template(self.__config['TEMPLATES']['url_input'], self.__config['COMMON']['bomb_crypto_url'], 0.05)

            self.__windows_action_helper.press_special_buttons("enter")

            self.__image_helper.wait_until_match_is_found(self.__windows_action_helper.take_screenshot, 
                                                     [], self.__config['COMMON']['bomb_crypto_url'],
                                                         self.__config['TIMEOUT'].getint('imagematching'), 0.05)

            self.security_check()

#region Util
    
    def __find_and_click_by_template(self, template_path, confidence_level = 0.1):
        result_match = self.__image_helper.wait_until_match_is_found(self.__windows_action_helper.take_screenshot, [], template_path, self.__config['TIMEOUT'].getint('imagematching'), confidence_level)

        if result_match:
            self.__windows_action_helper.click_on(result_match.x, result_match.y)
    

    def __find_and_write_by_template(self, template_path, to_write, confidence_level = 0.01):
        result_match = self.__image_helper.wait_until_match_is_found(self.__windows_action_helper.take_screenshot, [], template_path, self.__config['TIMEOUT'].getint('imagematching'), confidence_level)

        if result_match:
            self.__windows_action_helper.write_at(result_match.x, result_match.y, to_write)            


    def security_check(self):
        self.__image_helper.wait_until_match_is_found(self.__windows_action_helper.take_screenshot, 
                                                                [], self.__config['TEMPLATES']['url_validate'], 
                                                                    self.__config['TIMEOUT'].getint('imagematching') , 
                                                                    0.02, True)


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
                    self.restart_browser()
            time.sleep(retrytime) 


    def restart_browser(self):
        self.__windows_action_helper.kill_process(self.__config['WEBDRIVER']['chrome_exe_name'])
        self.__open_chrome_and_goto_game()
#endregion