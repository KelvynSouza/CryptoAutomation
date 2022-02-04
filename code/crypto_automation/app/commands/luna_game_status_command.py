import threading
import time
import traceback
import keyring
from win32con import *
from configparser import ConfigParser
from crypto_automation.app.commands.captcha_solver import CaptchaSolver
from crypto_automation.app.commands.chat_bot_command import ChatBotCommand
from crypto_automation.app.shared.command_actions_helper import CommandActionsHelper
from crypto_automation.app.shared.image_processing_helper import ImageHelper
from crypto_automation.app.shared.thread_helper import Job
from crypto_automation.app.shared.windows_action_helper import WindowsActionsHelper
import crypto_automation.app.shared.log_helper as log 

class LunaGameStatusCommand:
    def __init__(self, config: ConfigParser, password_access: str, chat_bot: ChatBotCommand , lock: threading.Lock = None):
        self.__config = config  
        self.__password_access = password_access
        self.__chat_bot = chat_bot  
        self.__lock = threading.Lock() if lock == None else lock                
        self.__image_helper = ImageHelper()
        self.__windows_action_helper = WindowsActionsHelper(config, self.__image_helper)               
        self.__commands_helper = CommandActionsHelper(config, self.__windows_action_helper, self.__image_helper, self.__lock, None, self.__restart_game)
        self.__idle = False
        

    def start_game(self):         
        with self.__lock:
            try:
                self.__open_chrome_and_goto_game()
                log.warning(f"Automation from {self.__config['WEBDRIVER']['name']} started succefully.", self.__chat_bot)
            except BaseException:
                log.error('Error:' + traceback.format_exc(), self.__chat_bot)
                log.image(self.__windows_action_helper, self.__chat_bot)
                self.__commands_helper.check_possible_server_error()

        self.__status_handling = Job(self.__commands_helper.thread_safe, self.__config['LUNA_CONFIG'].getint('hunt_timer'), False, False, self.__hunt_bosses)

        self.__status_handling.start()
        

    def __open_chrome_and_goto_game(self):
        self.__windows_action_helper.open_and_maximise_front_window(self.__config["WEBDRIVER"]["browser_path"],
                                                                    self.__config['TEMPLATES']['incognito_icon'],
                                                                    self.__config["WEBDRIVER"]["browser_args"])

        self.__open_game_website()

        self.__security_check()

        self.__enter_game()


    def __open_game_website(self):
        self.__commands_helper.find_and_click_by_template(self.__config['TEMPLATES']['incognito_icon'], 0.05)

        self.__commands_helper.find_and_write_by_template(self.__config['TEMPLATES']['url_input'], self.__config['COMMON']['luna_url'], 0.05)

        self.__windows_action_helper.press_special_buttons("enter")

        self.__image_helper.wait_until_match_is_found(self.__windows_action_helper.take_screenshot,
                                                      [], self.__config['TEMPLATES']['luna_connect_wallet_button'],
                                                      self.__config['TIMEOUT'].getint('imagematching'), 0.05, True)


    def __security_check(self):
        self.__image_helper.wait_until_match_is_found(self.__windows_action_helper.take_screenshot, 
                                                                [], self.__config['TEMPLATES']['url_validate'], 
                                                                    self.__config['TIMEOUT'].getint('imagematching') , 
                                                                    0.02, True)


    def __enter_game(self):
        self.__commands_helper.find_and_click_by_template(self.__config['TEMPLATES']['luna_connect_wallet_button'])

        self.__commands_helper.find_and_click_by_template(self.__config['TEMPLATES']['metamask_welcome_text'], 0.02)

        self.__commands_helper.find_and_write_by_template(self.__config['TEMPLATES']['metamask_password_input_inactive'],
                                          keyring.get_password(self.__config['SECURITY']['serviceid'], self.__password_access), 0.02)

        self.__commands_helper.find_and_click_by_template(self.__config['TEMPLATES']['metamask_unlock_button'], 0.02)

        if self.__image_helper.wait_until_match_is_found(self.__windows_action_helper.take_screenshot, [], self.__config['TEMPLATES']['metamask_sign_button'], 20, 0.05):
            self.__commands_helper.find_and_click_by_template(self.__config['TEMPLATES']['metamask_sign_button']) 
           
        elif self.__image_helper.wait_until_match_is_found(self.__windows_action_helper.take_screenshot, [], self.__config['TEMPLATES']['metamask_pending'], 20, 0.05):
                self.__commands_helper.find_and_click_by_template(self.__config['TEMPLATES']['metamask_pending'])
            
                self.__commands_helper.find_and_click_by_template(self.__config['TEMPLATES']['metamask_sign_button'])
        else:
                self.__commands_helper.find_and_click_by_template(self.__config['TEMPLATES']['restart_button'])

                self.__commands_helper.find_and_click_by_template(self.__config['TEMPLATES']['connect_wallet_button'])

                time.sleep(5)

                self.__commands_helper.find_and_click_by_template(self.__config['TEMPLATES']['metamask_sign_button'])
                    
        self.__commands_helper.find_and_click_by_template(self.__config['TEMPLATES']['luna_boss_button'])

        self.__image_helper.wait_until_match_is_found(self.__windows_action_helper.take_screenshot,
                                                      [], self.__config['TEMPLATES']['luna_hunt_boss_button'],
                                                      self.__config['TIMEOUT'].getint(
                                                          'imagematching'),
                                                      0.05, True)


    def __hunt_bosses(self):
        newmap = self.__image_helper.wait_until_match_is_found(self.__windows_action_helper.take_screenshot, [], self.__config['TEMPLATES']['newmap_button'], 1, 0.05)
        if newmap:
            log.warning(f"entering new map in {self.__config['WEBDRIVER']['name']}", self.__chat_bot)
            time.sleep(15)
            log.image(self.__windows_action_helper, self.__chat_bot)


        idle = self.__image_helper.wait_until_match_is_found(self.__windows_action_helper.take_screenshot, [], self.__config['TEMPLATES']['idle_error_message'], 1, 0.02)
        if idle:
            log.error(f"Detected idle message in {self.__config['WEBDRIVER']['name']}, pausing automation until its time to put the heroes to work again.", self.__chat_bot)
            self.__status_handling.pause()
            self.__connection_error_handling.pause()
            log.image(self.__windows_action_helper, self.__chat_bot)
            self.__idle = True
            return

        error = self.__image_helper.wait_until_match_is_found(self.__windows_action_helper.take_screenshot, [], self.__config['TEMPLATES']['error_message'], 1, 0.05)
        if error:
            log.error(f"Error on game in {self.__config['WEBDRIVER']['name']}, refreshing page.", self.__chat_bot)
            log.image(self.__windows_action_helper, self.__chat_bot)
            self.__commands_helper.check_possible_server_error()
            self.__restart_game()

        expected_screen = self.__image_helper.wait_until_match_is_found(self.__windows_action_helper.take_screenshot, [], self.__config['TEMPLATES']['map_screen_validator'], 1, 0.05)
        if expected_screen == None:
            log.error(f"game on wrong page in {self.__config['WEBDRIVER']['name']}, refreshing page.", self.__chat_bot)
            log.image(self.__windows_action_helper, self.__chat_bot)
            self.__restart_game()


# region Util
    def __restart_game(self):
        log.warning(f"Restarting automation in {self.__config['WEBDRIVER']['name']}", self.__chat_bot)
        self.__windows_action_helper.kill_process(self.__config['WEBDRIVER']['exe_name'])
        self.__open_chrome_and_goto_game()
        log.warning(f"Restarted successfully in {self.__config['WEBDRIVER']['name']}", self.__chat_bot)
# endregion