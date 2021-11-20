from crypto_automation.web_manipulation.helper import SeleniumHelper
from crypto_automation.shared.web_extension_helper import update_extension
import configparser

config_filename = "settings.ini"
config = configparser.ConfigParser()
config.read(config_filename)

update_extension(config['WEBDRIVER']['metamaskextension'],config['WEBDRIVER']['extension_url_download'])

selenium_helper = SeleniumHelper(config)
driver = selenium_helper.setup_driver()

selenium_helper.change_tab(driver)

driver.get("http://stubhub.com")

selenium_helper.find_and_click_bytext(driver,"Gift Cards")

selenium_helper.find_and_click_bytext(driver,"About Us")

selenium_helper.find_and_click_bytext(driver,"Sell Tickets")

print()

