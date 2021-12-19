import configparser
import threading
import time
from app.commands.game_status_manager import GameStatusManager
from app.shared.image_processing_helper import ImageHelper
from app.shared.numbers_helper import random_waitable_number
from app.shared.os_helper import create_log_folder
from app.shared.windows_action_helper import WindowsActionsHelper


class test:
    def __init__(self, config: configparser.ConfigParser):
        self.__config = config
        self.lock = threading.Lock()
        self.__image_helper = ImageHelper()
        self.__windows_action_helper = WindowsActionsHelper(
            config, self.__image_helper)

    def __find_and_click_by_template(self, template_path, confidence_level=0.05, should_thrown=True, should_grayscale=True):
        result_match = self.__image_helper.wait_until_match_is_found(self.__windows_action_helper.take_screenshot, [
        ], template_path, self.__config['TIMEOUT'].getint('imagematching'), confidence_level, should_thrown, should_grayscale)

        if result_match:
            self.__windows_action_helper.click_on(
                result_match.x, result_match.y)

    def run(self):
        time.sleep(5)

        newmap = self.__image_helper.wait_until_match_is_found(
            self.__windows_action_helper.take_screenshot, [], self.__config['TEMPLATES']['newmap_button'], 2, 0.05)
        if newmap:
            print('entering new map')
            self.__windows_action_helper.save_screenshot_log()
            self.__find_and_click_by_template(
                self.__config['TEMPLATES']['newmap_button'])

        print('Finished')


config_filename = "D:\Git\CryptoOcrAutomation\code\crypto_automation\settings.ini"

config = configparser.ConfigParser(
    interpolation=configparser.ExtendedInterpolation())
config.read(config_filename)
config['TEMPLATES']['game_images_path'] = '..\\resources\\images\\game'

create_log_folder(config['COMMON']['log_path'],
                  config['COMMON']['screenshots_path'])

asd = test(config)
asd.run()
