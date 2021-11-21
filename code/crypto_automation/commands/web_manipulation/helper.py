from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import undetected_chromedriver as uc
from fake_useragent import UserAgent, FakeUserAgentError 
from  crypto_automation.commands.shared.web_extension_helper import update_extension
import time
import cv2
import numpy as np

class SeleniumHelper:  
    def __init__(self, config):
        self.__config = config


    def setup_driver(self):
        if(self.__config['WEBDRIVER'].getboolean('always_update')):
            update_extension(self.__config['WEBDRIVER']['metamaskextension'],self.__config['WEBDRIVER']['extension_url_download'])
        
        chrome_options = Options()  

        try:
            ua = UserAgent()
            userAgent = ua.random
            chrome_options.add_argument(f'user-agent={userAgent}') 
        except FakeUserAgentError:
            pass         
        
        chrome_options.add_argument("--disable-plugins-discovery")
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_experimental_option("excludeSwitches",["enable-automation"])
        chrome_options.add_experimental_option("useAutomationExtension", False)
        chrome_options.add_extension(self.__config['WEBDRIVER']['metamaskextension'])
        driver = uc.Chrome(options=chrome_options)
        
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
        time.sleep(0.5)
        start_button.click()


    def find_and_click_bylocator(self, driver, by, locator):
        start_button = driver.find_element(by, locator)
        time.sleep(0.5)
        start_button.click()


    def find_and_write_input(self, driver, by, locator, input_text):
        elem = driver.find_element(by, locator)
        time.sleep(0.5)
        elem.send_keys(input_text)


    def click_element_by_position(self, driver, x_position, y_position):
        zero_elem = driver.find_element_by_tag_name('body')

        x_body_offset = -(zero_elem.size['width']/2)
        #caso ocorra algum problema com click baseado em image, esta pode ser a 
        #causa, por algum motivo bizarro ele tem uns 130px da borda, para 
        #validar a posição do cursor usar click_perform()
        y_body_offset = -(zero_elem.size['height']/2)+self.__config['IMAGEDETECTION'].getint('click_y_offset')

        actions = ActionChains(driver)
        actions.move_to_element(zero_elem)
        actions.move_by_offset(x_body_offset, y_body_offset).perform()
        actions.move_by_offset(x_position, y_position).click().perform()


    def validate_closed_window(self, driver):
        try:
            driver.current_window_handle
            return False
        except:
            return True


    def selenium_screenshot_to_opencv(self, driver):
        png = driver.get_screenshot_as_png()

        nparr = np.frombuffer(png, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        return img
