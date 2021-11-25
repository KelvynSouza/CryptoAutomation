from os import times
import time
import threading
import logging
import traceback
import datetime
import keyring
from win32con import *
from configparser import ConfigParser
from crypto_automation.commands.image_processing.helper import ImageHelper
from crypto_automation.commands.shared.thread_helper import Thread
from crypto_automation.commands.windows_actions.helper import WindowsActionsHelper
from crypto_automation.commands.shared.numbers_helper import random_waitable_number, random_number_between


class GameStatusWatcherActions:
    def __init__(self, config: ConfigParser):
        self.__config = config
        self.lock = threading.Lock()
        self.__image_helper = ImageHelper()
        self.__windows_action_helper = WindowsActionsHelper(config, self.__image_helper)
        self.__error_count = 0
        self.__error_time = None


    def start_game(self):
        try:
            self.__open_chrome_and_goto_game()
        except BaseException:
            self.__check_possible_server_error()
        
        error_handling = Thread(self.__thread_safe, self.__verify_and_handle_game_error, self.__config['RETRY'].getint('verify_error'))
        connection_error_handling = Thread(self.__thread_safe, self.__validate_game_connection, self.__config['RETRY'].getint('verify_zero_coins'))
        newmap_handling = Thread(self.__thread_safe, self.__verify_and_handle_newmap, self.__config['RETRY'].getint('verify_newmap'))
        hero_handling = Thread(self.__thread_safe, self.__verify_and_handle_heroes_status, self.__config['RETRY'].getint('verify_heroes_status'))


    def __open_chrome_and_goto_game(self):
            self.__windows_action_helper.open_and_maximise_front_window(self.__config["WEBDRIVER"]["chrome_path"], 
                                                                        self.__config['TEMPLATES']['incognito_icon'], 
                                                                        self.__config["WEBDRIVER"]["chrome_args"])

            self.__open_game_website()

            self.__security_check()

            self.__enter_game()


    def __open_game_website(self):
        self.__find_and_click_by_template(self.__config['TEMPLATES']['incognito_icon'], 0.05)

        self.__find_and_write_by_template(self.__config['TEMPLATES']['url_input'], self.__config['COMMON']['bomb_crypto_url'], 0.05)

        self.__windows_action_helper.press_special_buttons("enter")

        self.__image_helper.wait_until_match_is_found(self.__windows_action_helper.take_screenshot, 
                                                     [], self.__config['TEMPLATES']['connect_wallet_button'],
                                                         self.__config['TIMEOUT'].getint('imagematching'), 0.05, True)

    
    def __enter_game(self):
        self.__find_and_click_by_template(self.__config['TEMPLATES']['connect_wallet_button'])

        self.__find_and_click_by_template(self.__config['TEMPLATES']['metamask_connect_button'])

        self.__find_and_click_by_template(self.__config['TEMPLATES']['metamask_welcome_text'], 0.02, should_thrown=False)
        
        self.__find_and_write_by_template(self.__config['TEMPLATES']['metamask_password_input_inactive'], 
                                        keyring.get_password(self.__config['SECURITY']['serviceid'], "secret_password"), 0.02, should_thrown=False)

        self.__find_and_click_by_template(self.__config['TEMPLATES']['metamask_unlock_button'], 0.02, should_thrown=False)

        self.__find_and_click_by_template(self.__config['TEMPLATES']['metamask_sign_button'])

        self.__find_and_click_by_template(self.__config['TEMPLATES']['MapMode'])

        self.__image_helper.wait_until_match_is_found(self.__windows_action_helper.take_screenshot, 
                                                [], self.__config['TEMPLATES']['map_screen_validator'], 
                                                    self.__config['TIMEOUT'].getint('imagematching') , 
                                                    0.05, True)


    def __verify_and_handle_game_error(self):
        error = self.__image_helper.wait_until_match_is_found(self.__windows_action_helper.take_screenshot, [], self.__config['TEMPLATES']['error_message'], 2 , 0.05)
        if error:
            logging.error('Error on game, refreshing page.')
            self.__windows_action_helper.save_screenshot_log()
            self.__check_possible_server_error()
            self.__restart_game()

        expected_screen = self.__image_helper.wait_until_match_is_found(self.__windows_action_helper.take_screenshot, [], self.__config['TEMPLATES']['map_screen_validator'], 2 , 0.05)
        if expected_screen == None:
            logging.error('game on wrong page, refreshing page.')
            self.__windows_action_helper.save_screenshot_log()
            self.__restart_game()
        

    def __validate_game_connection(self):
        self.__find_and_click_by_template(self.__config['TEMPLATES']['treasure_chest_icon'], 0.01, should_grayscale = False)
        time.sleep(5)
        self.__windows_action_helper.save_screenshot_log()
        error = self.__image_helper.wait_until_match_is_found(self.__windows_action_helper.take_screenshot, [], self.__config['TEMPLATES']['zero_coins_validator'], 2 , 0.001, should_grayscale=False)
        if error:
            logging.error('Error on game connection, refreshing page.')            
            self.__check_possible_server_error()
            self.__restart_game()
        else:
            self.__find_and_click_by_template(self.__config['TEMPLATES']['exit_button'], 0.03, should_grayscale = False)


    def __verify_and_handle_newmap(self):
        newmap = self.__image_helper.wait_until_match_is_found(self.__windows_action_helper.take_screenshot, [], self.__config['TEMPLATES']['newmap_button'], 2 , 0.05)
        if newmap:
            logging.warning('entering new map')
            self.__windows_action_helper.save_screenshot_log()
            self.__find_and_click_by_template(self.__config['TEMPLATES']['newmap_button'])


    def __verify_and_handle_heroes_status(self):
            logging.warning('Checking heroes status')        
            self.__find_and_click_by_template(self.__config['TEMPLATES']['back_button'])
            self.__find_and_click_by_template(self.__config['TEMPLATES']['heroes_icon'])
            
            timeout = self.__config['TIMEOUT'].getint('imagematching')

            if(self.__image_helper.wait_until_match_is_found(self.__windows_action_helper.take_screenshot, [], self.__config['TEMPLATES']['work_active_button'], timeout, 0.02) 
            or self.__image_helper.wait_until_match_is_found(self.__windows_action_helper.take_screenshot, [], self.__config['TEMPLATES']['work_button'], timeout, 0.02)):
                self.__windows_action_helper.save_screenshot_log()
                self.__click_all_work_buttons()
    
            self.__find_and_click_by_template(self.__config['TEMPLATES']['exit_button'])
            self.__find_and_click_by_template(self.__config['TEMPLATES']['MapMode'])
            self.__image_helper.wait_until_match_is_found(self.__windows_action_helper.take_screenshot, [], self.__config['TEMPLATES']['map_screen_validator'], 2 , 0.05, True)


    def __click_all_work_buttons(self):
        result_match = self.__image_helper.wait_all_until_match_is_found(self.__windows_action_helper.take_screenshot, [], self.__config['TEMPLATES']['work_button'], 2, 0.02)

        count = 0
        while len(result_match) == 0 and count <= 5:
            result_active_match = self.__image_helper.wait_all_until_match_is_found(self.__windows_action_helper.take_screenshot, [], self.__config['TEMPLATES']['work_active_button'], 25, 0.02)
            if result_active_match:
                last_active_button_x, last_active_button_y  = result_active_match[len(result_active_match)-1]
                self.__windows_action_helper.click_and_scroll_down(last_active_button_x, last_active_button_y)
                result_match = self.__image_helper.wait_all_until_match_is_found(self.__windows_action_helper.take_screenshot, [], self.__config['TEMPLATES']['work_button'], 25, 0.02)
            count += 1

        count = 0
        while len(result_match) > 0 and count <= 5:                    
            for (x, y) in result_match:
                self.__windows_action_helper.click_on(x, y)
                time.sleep(random_waitable_number(self.__config))            
            last_button_x, last_button_y = result_match[len(result_match)-1]            
            self.__windows_action_helper.click_and_scroll_down(last_button_x, last_button_y)
            result_match = self.__image_helper.wait_all_until_match_is_found(self.__windows_action_helper.take_screenshot, [], self.__config['TEMPLATES']['work_button'], 25, 0.02)
            count +=1


#region Util
    
    def __find_and_click_by_template(self, template_path, confidence_level = 0.05, should_thrown = True, should_grayscale = True):
        result_match = self.__image_helper.wait_until_match_is_found(self.__windows_action_helper.take_screenshot, [], template_path, self.__config['TIMEOUT'].getint('imagematching'), confidence_level, should_thrown, should_grayscale)

        if result_match:
            self.__windows_action_helper.click_on(result_match.x, result_match.y)
    

    def __find_and_write_by_template(self, template_path, to_write, confidence_level = 0.05, should_thrown = True):
        result_match = self.__image_helper.wait_until_match_is_found(self.__windows_action_helper.take_screenshot, [], template_path, self.__config['TIMEOUT'].getint('imagematching'), confidence_level, should_thrown)

        if result_match:
            self.__windows_action_helper.write_at(result_match.x, result_match.y, to_write)            


    def __security_check(self):
        self.__image_helper.wait_until_match_is_found(self.__windows_action_helper.take_screenshot, 
                                                                [], self.__config['TEMPLATES']['url_validate'], 
                                                                    self.__config['TIMEOUT'].getint('imagematching') , 
                                                                    0.02, True)


    def __thread_safe(self, method, retrytime, positional_arguments = None, keyword_arguments = None):
        error = False                
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
                    self.__windows_action_helper.save_screenshot_log()
                    self.__check_possible_server_error() 
                    error = True     
                finally:           
                    try:
                        if error:
                            self.__reload_page()
                            error = False 
                    except:
                        self.__restart_game()
                        error = False 
            time.sleep(retrytime) 


    def __check_possible_server_error(self):
        if self.__error_time:
            time_difference = (datetime.datetime.now() - self.__error_time)
            time_difference_minutes = time_difference.total_seconds() / 60            
            if time_difference_minutes <= 3:
                self.__error_count +=1
            else:
                self.__error_count = 0

        if self.__error_count > 6:
            logging.error("Error on server supected, waiting setted time to try again.")
            time.sleep(self.__config['TIMEOUT'].getint('server_error'))
            self.__restart_game()
            self.__error_count = 0

        self.__error_time = datetime.datetime.now()
        

    def __restart_game(self):
        logging.warning('Restarting automation')
        self.__windows_action_helper.kill_process(self.__config['WEBDRIVER']['chrome_exe_name'])
        self.__open_chrome_and_goto_game()


    def __reload_page(self):
        self.__find_and_click_by_template(self.__config['TEMPLATES']['restart_button'])
        self.__security_check()
        self.__enter_game()
#endregion