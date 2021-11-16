from web_manipulation.helper import SeleniumHelper
from web_manipulation.connect_to_wallet import ConnectWallet
from image_processing.game_status_watcher import GameStatusWatcher
from  shared.web_extension_helper import update_extension
import configparser
import keyring

config_filename = "settings.ini"

config = configparser.ConfigParser()
config.read(config_filename)


def run():
    update_extension(config['WEBDRIVER']['metamaskextension'],config['WEBDRIVER']['extension_url_download'])

    secure_passwords()

    selenium_helper = SeleniumHelper(config)

    driver = selenium_helper.setup_driver()

    wallet_helper = ConnectWallet(driver, config)
    
    game_status_watcher = GameStatusWatcher(driver, config, wallet_helper)

    game_status_watcher.start_game()
    

def secure_passwords():
    if config['SECURITY'].getboolean('ispasswordsecured') == False:
        keyring.set_password(config['SECURITY']['serviceid'], "secret_phrase", config['LOGIN']['secretphrase'])
        keyring.set_password(config['SECURITY']['serviceid'], "secret_password", config['LOGIN']['newpassword'])

        config['LOGIN']['secretphrase'] = "Secured"
        config['LOGIN']['newpassword'] = "Secured"
        config['SECURITY']['ispasswordsecured'] = "True"

        with open(config_filename, 'w') as configfile:
            config.write(configfile)
    