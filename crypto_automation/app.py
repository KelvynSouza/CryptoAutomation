from web_manipulation.helper import SeleniumHelper
from web_manipulation.connect_to_wallet import ConnectWallet
from image_processing.game_status_watcher import GameStatusWatcher

def run():
    driver = SeleniumHelper.setup_driver()
    wallet_helper = ConnectWallet(driver)
    game_status_watcher = GameStatusWatcher(driver)

    wallet_helper.configure_wallet()

    driver.get("https://app.bombcrypto.io")

    game_status_watcher.connect_wallet_button()

    wallet_helper.connect_wallet_to_game()

    game_status_watcher.start_map_mode()
    
    driver.close()