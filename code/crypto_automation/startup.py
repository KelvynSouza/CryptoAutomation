import configparser
import logging
import traceback
import keyring
from app.commands.game_status_manager import GameStatusManager
from app.shared.os_helper import create_folder
from app.shared.windows_action_helper import WindowsActionsHelper


def run():   
    logging.warning('Starting automation.')

    secure_passwords()

    try:
        game_watcher = GameStatusManager(config)
        game_watcher.start_game()
    except BaseException as ex:
        global error
        error += 1
        logging.error('Error:' + traceback.format_exc())
        logging.warning('Restarting automation:')        

        windows_helper = WindowsActionsHelper(config)

        is_browser_open = windows_helper.process_exists(config['WEBDRIVER']['chrome_exe_name'])

        if is_browser_open:
            windows_helper.kill_process(config['WEBDRIVER']['chrome_exe_name'])

        if error < 10:
            run()    
    

def secure_passwords():
        if config['SECURITY'].getboolean('ispasswordsecured') == False:
            keyring.set_password(config['SECURITY']['serviceid'], "secret_password", config['LOGIN']['newpassword'])

            config['LOGIN']['newpassword'] = "Secured"
            config['SECURITY']['ispasswordsecured'] = "True"

            with open(config['COMMON']['settings_name'], 'w') as configfile:
                config.write(configfile)
    

config = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
config.read( "settings.ini")

create_folder(config['COMMON']['log_folder_path'])
create_folder(config['COMMON']['screenshots_path'])

logging.basicConfig(format='[%(asctime)s] %(message)s', filename=config['COMMON']['log_file'], encoding='utf-8', level=logging.WARNING)

error = 0