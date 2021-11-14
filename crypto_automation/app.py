from web_manipulation.helper import SeleniumHelper
from web_manipulation.connect_to_wallet import ConnectWallet

def run():
    driver = SeleniumHelper.setup_driver()
    wallet_helper = ConnectWallet(driver)

    wallet_helper.configure_wallet()

    driver.get("https://app.bombcrypto.io")

    wallet_helper.connect_wallet_to_game()
    
    driver.close()