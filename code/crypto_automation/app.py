from web_manipulation.helper import SeleniumHelper
from web_manipulation.connect_to_wallet import ConnectWallet
from image_processing.game_status_watcher import GameStatusWatcher
import configparser
from passlib.context import CryptContext

config = configparser.ConfigParser()
config.read('settings.ini')




def run():
    selenium_helper = SeleniumHelper(config)

    driver = selenium_helper.setup_driver()

    wallet_helper = ConnectWallet(driver, config)
    
    game_status_watcher = GameStatusWatcher(driver, config, wallet_helper)

    game_status_watcher.start_game()
    