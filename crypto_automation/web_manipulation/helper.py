from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By


class SeleniumHelper:    

    def setup_driver():
        chrome_options = Options()
        chrome_options.add_extension('browser_driver\extensions\MetaMask.crx')
        chrome_options.add_experimental_option("useAutomationExtension", False)
        chrome_options.add_experimental_option("excludeSwitches",["enable-automation"])
        driver = webdriver.Chrome("browser_driver\chromedriver.exe", options=chrome_options)
        driver.implicitly_wait(10)  
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
