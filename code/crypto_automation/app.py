from commands.web_manipulation.helper import SeleniumHelper
from commands.game_watcher.connect_to_wallet import ConnectWallet
from commands.game_watcher.game_status_watcher import GameStatusWatcher
from  commands.shared.web_extension_helper import update_extension
import configparser
import keyring
import logging
import traceback
from commands.shared.os_helper import create_log_folder

config_filename = "settings.ini"

config = configparser.ConfigParser()
config.read(config_filename)

create_log_folder(config['LOG']['log_path'])

logging.basicConfig(format='[%(asctime)s] %(message)s', filename=config['LOG']['log_path'], encoding='utf-8', level=logging.WARNING)

def run():   
    logging.warning('Starting automation.')

    error = False

    try:
        update_extension(config['WEBDRIVER']['metamaskextension'],config['WEBDRIVER']['extension_url_download'])

        secure_passwords()

        selenium_helper = SeleniumHelper(config)

        driver = selenium_helper.setup_driver()

        wallet_helper = ConnectWallet(driver, config)

        game_status_watcher = GameStatusWatcher(driver, config, wallet_helper)

        game_status_watcher.start_game()

    except BaseException as ex:
        error = True
        logging.error('Error:' + traceback.format_exc())
        logging.warning('Restarting automation:')
        if driver:
            driver.quit()
        run()        

    if error == False:
        logging.warning('Automation started.')
    

def secure_passwords():
    if config['SECURITY'].getboolean('ispasswordsecured') == False:
        keyring.set_password(config['SECURITY']['serviceid'], "secret_phrase", config['LOGIN']['secretphrase'])
        keyring.set_password(config['SECURITY']['serviceid'], "secret_password", config['LOGIN']['newpassword'])

        config['LOGIN']['secretphrase'] = "Secured"
        config['LOGIN']['newpassword'] = "Secured"
        config['SECURITY']['ispasswordsecured'] = "True"

        with open(config_filename, 'w') as configfile:
            config.write(configfile)
    
