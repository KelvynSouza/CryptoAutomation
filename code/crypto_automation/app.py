from commands.web_manipulation.helper import SeleniumHelper
from commands.game_watcher.connect_to_wallet import ConnectWallet
from commands.game_watcher.game_status_watcher import GameStatusWatcher
import configparser
import logging
import traceback
from commands.shared.os_helper import create_log_folder

config_filename = "settings.ini"

config = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
config.read(config_filename)

create_log_folder(config['COMMON']['log_path'])

logging.basicConfig(format='[%(asctime)s] %(message)s', filename=config['COMMON']['log_path'], encoding='utf-8', level=logging.WARNING)


def run():   
    logging.warning('Starting automation.')

    error = False

    try:
        if config['COMMON'].getint('automation_type') == 1:
            selenium_helper = SeleniumHelper(config)

            driver = selenium_helper.setup_driver()

            wallet_helper = ConnectWallet(driver, config)

            game_status_watcher = GameStatusWatcher(driver, config, wallet_helper)

            game_status_watcher.start_game()
        else:
            print()

    except BaseException as ex:
        error = True
        logging.error('Error:' + traceback.format_exc())
        logging.warning('Restarting automation:')
        if driver:
            driver.quit()
        run()        

    if error == False:
        logging.warning('Automation started.')
    


    
