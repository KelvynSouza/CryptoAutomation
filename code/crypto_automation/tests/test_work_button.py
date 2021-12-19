import configparser
import threading
import time
from app.commands.game_status_manager import GameStatusManager
from app.shared.image_processing_helper import ImageHelper
from app.shared.numbers_helper import random_waitable_number
from app.shared.os_helper import create_folder
from app.shared.windows_action_helper import WindowsActionsHelper

class test:
    def __init__(self, config: configparser.ConfigParser):
        self.__config = config
        self.lock = threading.Lock()
        self.__image_helper = ImageHelper()
        self.__windows_action_helper = WindowsActionsHelper(
            config, self.__image_helper)

    def run(self):
        time.sleep(5)

        result_match = self.__image_helper.wait_all_until_match_is_found(self.__windows_action_helper.take_screenshot, [
        ], self.__config['TEMPLATES']['work_button'], 2, 0.01, should_grayscale=False)

        count = 0
        while len(result_match) == 0 and count <= 5:
            result_active_match = self.__image_helper.wait_all_until_match_is_found(self.__windows_action_helper.take_screenshot, [
            ], self.__config['TEMPLATES']['work_active_button'], 25, 0.005, should_grayscale=False)
            if result_active_match:
                x_offset = -50
                last_active_button_x, last_active_button_y = result_active_match[len(
                    result_active_match)-1]
                self.__windows_action_helper.click_and_scroll_down(
                    last_active_button_x + x_offset, last_active_button_y)
                result_match = self.__image_helper.wait_all_until_match_is_found(self.__windows_action_helper.take_screenshot, [
                ], self.__config['TEMPLATES']['work_button'], 25, 0.005, should_grayscale=False)
            count += 1

        count = 0
        while len(result_match) > 0 and count <= 5:
            print(
                f'result_match count BEFORE clicking: {str(len(result_match))}')
            for (x, y) in result_match:
                self.__windows_action_helper.click_on(x, y)
                time.sleep(random_waitable_number(self.__config))
            last_button_x, last_button_y = result_match[len(result_match)-1]
            self.__windows_action_helper.click_and_scroll_down(
                last_button_x, last_button_y)
            result_match = self.__image_helper.wait_all_until_match_is_found(self.__windows_action_helper.take_screenshot, [
            ], self.__config['TEMPLATES']['work_button'], 25, 0.005, should_grayscale=False)
            print(
                f"result_match count AFTER clicking: {str(len(result_match))}")
            count += 1

        print('Finished')

config_filename = "D:\Git\CryptoOcrAutomation\code\crypto_automation\settings.ini"

config = configparser.ConfigParser(
    interpolation=configparser.ExtendedInterpolation())
config.read(config_filename)
config['TEMPLATES']['game_images_path'] = '..\\resources\\images\\game'

create_folder(config['COMMON']['log_folder_path'])
create_folder(config['COMMON']['screenshots_path'])

asd = test(config)
asd.run()