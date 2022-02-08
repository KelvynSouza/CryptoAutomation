from configparser import ConfigParser
import datetime
import threading
import traceback
import time
from win32con import *
from crypto_automation.app.commands.chat_bot_command import ChatBotCommand
import crypto_automation.app.shared.log_helper as log 
from crypto_automation.app.commands.captcha_solver import CaptchaSolver
from crypto_automation.app.shared.image_processing_helper import ImageHelper
from crypto_automation.app.shared.numbers_helper import random_number_between
from crypto_automation.app.shared.windows_action_helper import WindowsActionsHelper


class CommandActionsHelper:
    def __init__(self, config: ConfigParser, action_helper: WindowsActionsHelper, image_helper: ImageHelper, lock: threading.Lock, captcha_solver: CaptchaSolver, restart_method,  chat_bot: ChatBotCommand ,):
        self.__config = config
        self.__image_helper = image_helper
        self.__windows_action_helper = action_helper
        self.__captcha_solver = captcha_solver
        self.__lock = lock
        self.__error_count = 0
        self.__error_time = None
        self.__restart_game = restart_method
        self.__chat_bot = chat_bot

    def find_and_click_by_template(self, template_path, confidence_level=0.1, should_thrown=True, should_grayscale=True):
        result_match = self.__image_helper.wait_until_match_is_found(self.__windows_action_helper.take_screenshot, [], template_path, self.__config['TIMEOUT'].getint('imagematching'), confidence_level, should_thrown, should_grayscale)

        if result_match:
            self.__windows_action_helper.click_on(result_match.x, result_match.y)

        if self.__captcha_solver:
            captcha_match = self.__image_helper.wait_until_match_is_found(self.__windows_action_helper.take_screenshot, [], self.__config['TEMPLATES']['robot_message'], 2, 0.05, False, False)
            if captcha_match:
                self.__captcha_solver.solve_captcha()
            

    def find_and_write_by_template(self, template_path, to_write, confidence_level=0.05, should_thrown=True):
        result_match = self.__image_helper.wait_until_match_is_found(self.__windows_action_helper.take_screenshot, [], template_path, self.__config['TIMEOUT'].getint('imagematching'), confidence_level, should_thrown)

        if result_match:
            self.__windows_action_helper.write_at(result_match.x, result_match.y, to_write)


    def thread_safe(self, method, bring_foreground = True, positional_arguments = None, keyword_arguments = None):
        error = False 
        with self.__lock:  
            if bring_foreground:
                self.__windows_action_helper.bring_window_foreground(self.__config['WEBDRIVER']['name']) 
            try:   
                self.__execute_method(method, positional_arguments, keyword_arguments)
            except BaseException as ex:
                log.error(f"Error in {self.__config['WEBDRIVER']['name']}:" + traceback.format_exc(), self.__chat_bot)
                log.image(self.__windows_action_helper, self.__chat_bot)
                self.check_possible_server_error()
                error = True
            finally:
                try:
                    if error:
                        self.__restart_game()
                        self.__execute_method(method, positional_arguments, keyword_arguments)
                        error = False 
                except:
                    self.check_possible_server_error()


    def __execute_method(self, method, positional_arguments = None, keyword_arguments = None):
        if positional_arguments:
            method(*positional_arguments)
        elif keyword_arguments:
            method(**keyword_arguments)
        elif positional_arguments and keyword_arguments: 
            method(*positional_arguments, **keyword_arguments)
        else:
            method()


    def check_possible_server_error(self):
        log.error(f"Checking for possible error on server in {self.__config['WEBDRIVER']['name']}.", self.__chat_bot)
        if self.__error_time:
            time_difference = (datetime.datetime.now() - self.__error_time)            
            if time_difference.total_seconds() <= self.__config['TIMEOUT'].getint('errors_time_difference'):
                self.__error_count += 1
            else:
                self.__error_count = 0

        if self.__error_count >= self.__config['TIMEOUT'].getint('errors_count_limit'):
            time_sleep = self.__config['TIMEOUT'].getint('server_error') * random_number_between(1.0,1.5)
            log.error(f"Error on server suspected in {self.__config['WEBDRIVER']['name']}, waiting {time_sleep} seconds to try again.", self.__chat_bot)
            time.sleep(time_sleep)
            self.__error_count = 0

        self.__error_time = datetime.datetime.now()