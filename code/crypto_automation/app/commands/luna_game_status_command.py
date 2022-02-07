from ast import Str
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
        

    def start_game(self):   
        self.__luna_thread = Job(self.__commands_helper.thread_safe, self.__config['LUNA_CONFIG'].getint('hunt_timer'), False, False, self.__hunt_bosses)

        self.__luna_thread.start()

        log.warning(f"Automation from {self.__config['WEBDRIVER']['name']} started succefully.", self.__chat_bot)
        

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

        self.__image_helper.wait_until_match_is_found(self.__windows_action_helper.take_screenshot,
                                                      [], self.__config['TEMPLATES']['luna_boss_button'],
                                                      self.__config['TIMEOUT'].getint(
                                                          'imagematching'),
                                                      0.05, True)


    def __hunt_bosses(self):
        self.__open_chrome_and_goto_game()

        self.__commands_helper.find_and_click_by_template(self.__config['TEMPLATES']['luna_boss_button'])

        self.__image_helper.wait_until_match_is_found(self.__windows_action_helper.take_screenshot,
                                                     [], self.__config['TEMPLATES']['luna_hunt_boss_button'],
                                                     self.__config['TIMEOUT'].getint(
                                                         'imagematching'),
                                                     0.05, True)        

        total_played_heroes = 0
        teams = self.__config['LUNA_CONFIG']['team_members'].split('|')
        for team in teams:
            total_played_heroes += len(team)
            team_members = team.split(",")

            self.__uncheck_all_heroes()                           
            self.__check_team_heroes(team_members)

            playing_team = True
            tries = 0
            while(playing_team): 
                tries += 1
                self.__commands_helper.find_and_click_by_template(self.__config['TEMPLATES']['luna_hunt_boss_button'], confidence_level=0.02)

                self.__commands_helper.find_and_click_by_template(self.__config['TEMPLATES']['luna_touch_to_start_phrase'])

                time.sleep(30)

                if self.__image_helper.wait_until_match_is_found(self.__windows_action_helper.take_screenshot, [], self.__config['TEMPLATES']['luna_defeat_message'], 20, 0.05):
                    self.__commands_helper.find_and_click_by_template(self.__config['TEMPLATES']['luna_touch_to_continue_phrase'])
                else:
                    self.__commands_helper.find_and_click_by_template(self.__config['TEMPLATES']['luna_open_chest_button'])
                    self.__commands_helper.find_and_click_by_template(self.__config['TEMPLATES']['luna_touch_to_continue_phrase'])
                
                empty_heroes = self.__image_helper.wait_all_until_match_is_found(self.__windows_action_helper.take_screenshot, [], self.__config['TEMPLATES']['luna_low_energy_bar'], 5, 0.02)
                if len(empty_heroes) == total_played_heroes:
                    playing_team = False
                    break

                if tries > 5:
                    playing_team = False
                    log.error(f"Error Trying to play with heroes in Luna Rush.", self.__chat_bot)
                    break
        self.__close_browser()
                

            

        
    def __uncheck_all_heroes(self):
        for i in range(1, self.__config['LUNA_CONFIG'].getint('number_of_heroes')):
            checked_hero_image_path = f"{self.__config['TEMPLATES']['luna_heroes_path']}\\checked_hero_{i}.png"
            hero_image_path = f"{self.__config['TEMPLATES']['luna_heroes_path']}\\hero_{i}.png"

            if self.__image_helper.wait_until_match_is_found(self.__windows_action_helper.take_screenshot, [], checked_hero_image_path, 3, 0.02):
                self.__commands_helper.find_and_click_by_template(checked_hero_image_path)
                self.__image_helper.wait_until_match_is_found(self.__windows_action_helper.take_screenshot, [], hero_image_path, 10, 0.02, True)


    def __check_team_heroes(self, team_members: list[str]):
        for i in team_members:
            checked_hero_image_path = f"{self.__config['TEMPLATES']['luna_heroes_path']}\\checked_hero_{i}.png"
            hero_image_path = f"{self.__config['TEMPLATES']['luna_heroes_path']}\\hero_{i}.png"
            
            self.__commands_helper.find_and_click_by_template(hero_image_path)
            self.__image_helper.wait_until_match_is_found(self.__windows_action_helper.take_screenshot, [], checked_hero_image_path, 10, 0.05, True)


# region Util
    def __restart_game(self):
        log.warning(f"Restarting automation in {self.__config['WEBDRIVER']['name']}", self.__chat_bot)
        self.__windows_action_helper.kill_process(self.__config['WEBDRIVER']['exe_name'])
        self.__open_chrome_and_goto_game()
        log.warning(f"Restarted successfully in {self.__config['WEBDRIVER']['name']}", self.__chat_bot)

    def __close_browser(self):
        log.warning(f"Closing browser {self.__config['WEBDRIVER']['name']} for Luna Rush", self.__chat_bot)
        self.__windows_action_helper.kill_process(self.__config['WEBDRIVER']['exe_name'])
        log.warning(f"Closed browser {self.__config['WEBDRIVER']['name']} successfully", self.__chat_bot)
# endregion
