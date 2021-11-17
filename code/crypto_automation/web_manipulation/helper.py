from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import undetected_chromedriver as uc

class SeleniumHelper:  
    def __init__(self, config):
        self.__config = config


    def setup_driver(self):
        chrome_options = Options()
        chrome_options.add_argument('--profile-directory=Default')
        chrome_options.add_argument("--incognito")
        chrome_options.add_argument("--disable-plugins-discovery")
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_extension(self.__config['WEBDRIVER']['metamaskextension'])
        chrome_options.add_experimental_option("useAutomationExtension", False)
        chrome_options.add_experimental_option("excludeSwitches",["enable-automation"])
        driver = uc.Chrome(options=chrome_options)

        driver = webdriver.Chrome(self.__config['WEBDRIVER']['chromedriver'], options=chrome_options)
        driver.delete_all_cookies()
        driver.implicitly_wait(self.__config['TIMEOUT'].getint('webscraping'))  
        driver.maximize_window()
        return driver  


    def change_tab(self, driver, from_closed=False):
        if(from_closed):
            driver.switch_to.window(driver.window_handles[0])  
            return    

        p = driver.current_window_handle
        chwd = driver.window_handles
        for w in chwd:
            if(w!=p):
                driver.switch_to.window(w)            
                break


    def find_and_click_bytext(self, driver, text):
        start_button = driver.find_element(By.XPATH, f"//*[contains(text(),'{text}')]")
        start_button.click()


    def find_and_click_bylocator(self, driver, by, locator):
        start_button = driver.find_element(by, locator)
        start_button.click()


    def find_and_write_input(self, driver, by, locator, input_text):
        elem = driver.find_element(by, locator)
        elem.send_keys(input_text)


    def validate_closed_window(self, driver):
        try:
            driver.current_window_handle
            return False
        except:
            return True
