from _typeshed import Self
from typing import Text
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class SeleniumHelper:

    def setup_driver(self):
        chrome_options = Options()
        chrome_options.add_extension('browser_driver\extensions\MetaMask.crx')
        driver = webdriver.Chrome("browser_driver\chromedriver.exe", options=chrome_options)
        driver.implicitly_wait(10) 
        self.__driver = driver  
        return driver  


    def change_tab(self, from_closed=False):
        if(from_closed):
            self.__driver.switch_to.window(self.__driver.window_handles[0])  
            return    

        p = self.__driver.current_window_handle
        chwd = self.__driver.window_handles
        for w in chwd:
            if(w!=p):
                self.__driver.switch_to.window(w)            
                break


    def find_and_click_bytext(self, text):
        start_button = self.__driver.find_element(By.XPATH, f"//*[contains(text(),'{text}')]")
        start_button.click()


    def find_and_click_bylocator(self, by, locator):
        start_button = self.__driver.find_element(by, locator)
        start_button.click()


    def find_and_write_input(self, by, locator, input_text):
        elem = self.__driver.find_element(by, locator)
        elem.send_keys(input_text)


    def validate_closed_window(self):
        try:
            self.__driver.current_window_handle
            return False
        except:
            return True
