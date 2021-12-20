import configparser
import logging
import threading
import traceback
import keyring
from app.commands.game_status_manager import GameStatusManager
from app.shared.os_helper import create_folder
from app.shared.windows_action_helper import WindowsActionsHelper
from app.commands.chat_bot_manager import ChatBotManager
import crypto_automation.app.shared.log_helper as log 

def run():   
    log.warning('Starting automation.', chat)
    
    secure_passwords()
    lock = threading.Lock()
    start_browser('chrome', lock)    
    

def secure_passwords():
    if config['SECURITY'].getboolean('ispasswordsecured') == False:
        keyring.set_password(config['SECURITY']['serviceid'], "secret_password_chrome", config['LOGIN']['password_chrome'])
        keyring.set_password(config['SECURITY']['serviceid'], "secret_password_edge", config['LOGIN']['password_edge'])
        config['LOGIN']['password_chrome'] = "Secured"
        config['LOGIN']['password_edge'] = "Secured"
        config['SECURITY']['ispasswordsecured'] = "True"
        with open(config['COMMON']['settings_name'], 'w') as configfile:
            config.write(configfile)
    

def start_browser(browser: str, lock: threading.Lock):
    try:
        config['TEMPLATES']['browser_images_path'] = config['TEMPLATES'][f'{browser}_images_path'] 
        config['WEBDRIVER'] = config[f'{browser.upper()}_DRIVER']
        game_watcher = GameStatusManager(config, f"secret_password_{browser}", chat, lock)
        game_watcher.start_game()

    except BaseException:
        global error
        error += 1
        log.error('Error:' + traceback.format_exc())
        log.warning('Restarting automation:', chat)        

        windows_helper = WindowsActionsHelper(config)

        is_browser_open = windows_helper.process_exists(config['WEBDRIVER']['exe_name'])

        if is_browser_open:
            windows_helper.kill_process(config['WEBDRIVER']['exe_name'])

        if error < 10:
            start_browser() 


config = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
config.read( "settings.ini")

create_folder(config['COMMON']['log_folder_path'])
create_folder(config['COMMON']['screenshots_path'])

logging.basicConfig(format='[%(asctime)s] %(message)s', filename=config['COMMON']['log_file'], encoding='utf-8', level=logging.WARNING)

chat = None
if config['TELEGRAM'].getboolean('integration'):
    chat = ChatBotManager(config)
    chat.start()

error = 0


