from commands.web_manipulation.helper import SeleniumHelper
from commands.game_watcher_selenium.connect_to_wallet import ConnectWallet
from commands.game_watcher_selenium.game_status_watcher import GameStatusWatcherSelenium
from commands.game_watcher_windows_actions.game_status_watcher import GameStatusWatcherActions
import configparser
import logging
import traceback
import keyring
from commands.shared.os_helper import create_log_folder
from crypto_automation.commands.windows_actions.helper import WindowsActionsHelper

config_filename = "settings.ini"

config = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
config.read(config_filename)

create_log_folder(config['COMMON']['log_path'])

logging.basicConfig(format='[%(asctime)s] %(message)s', filename=config['COMMON']['log_path'], encoding='utf-8', level=logging.WARNING)

error = 0


def run():   
    logging.warning('Starting automation.')

    secure_passwords()

    driver = None

    try:
        if config['COMMON'].getint('automation_type') == 1:
            selenium_helper = SeleniumHelper(config)

            driver = selenium_helper.setup_driver()

            wallet_helper = ConnectWallet(driver, config)

            game_status_watcher = GameStatusWatcherSelenium(driver, config, wallet_helper)

            game_status_watcher.start_game()
        else:
            game_watcher = GameStatusWatcherActions(config)

            game_watcher.start_game()

    except BaseException as ex:
        global error
        error += 1
        logging.error('Error:' + traceback.format_exc())
        logging.warning('Restarting automation:')
        if driver :
            driver.quit()

        windows_helper = WindowsActionsHelper(config)

        is_browser_open = windows_helper.process_exists("chrome")

        if is_browser_open:
            windows_helper.kill_process("chrome.exe")

        if error < 5:
            run()        

    if error == 0:
        logging.warning('Automation started.')
    

def secure_passwords():
        if config['SECURITY'].getboolean('ispasswordsecured') == False:
            keyring.set_password(config['SECURITY']['serviceid'], "secret_phrase", config['LOGIN']['secretphrase'])
            keyring.set_password(config['SECURITY']['serviceid'], "secret_password", config['LOGIN']['newpassword'])

            config['LOGIN']['secretphrase'] = "Secured"
            config['LOGIN']['newpassword'] = "Secured"
            config['SECURITY']['ispasswordsecured'] = "True"

            with open(config['COMMON']['settings_name'], 'w') as configfile:
                config.write(configfile)
    
