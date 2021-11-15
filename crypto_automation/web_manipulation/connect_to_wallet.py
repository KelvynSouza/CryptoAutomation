from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from .helper import SeleniumHelper


class ConnectWallet:

    def __init__(self, driver):
        self.__driver = driver
        self.__selenium_helper =  SeleniumHelper()


    def configure_wallet(self):
        self.__selenium_helper.change_tab(self.__driver)

        self.__selenium_helper.find_and_click_bytext(self.__driver, "Comece agora")
        self.__selenium_helper.find_and_click_bytext(self.__driver, "Importar carteira")
        self.__selenium_helper.find_and_click_bytext(self.__driver, "Concordo")

        self.__selenium_helper.find_and_write_input(self.__driver, By.XPATH, "//input[contains(@placeholder,'Frase de recuperação')]", "height carpet cabin broken snap dress market coil like tube success intact")
        self.__selenium_helper.find_and_write_input(self.__driver, By.ID, "password", "12340987")
        self.__selenium_helper.find_and_write_input(self.__driver, By.ID, "confirm-password", "12340987")

        self.__selenium_helper.find_and_click_bylocator(self.__driver, By.XPATH, "//span[text()='Eu li e concordo com ']")

        self.__selenium_helper.find_and_click_bytext(self.__driver, "Importar")
        self.__selenium_helper.find_and_click_bytext(self.__driver, "Tudo pronto")

        self.__configure_wallet_network()        
    
        self.__driver.close()

        self.__selenium_helper.change_tab(self.__driver, True)


    def __configure_wallet_network(self):
        self.__selenium_helper.find_and_click_bylocator(self.__driver, By.CSS_SELECTOR, ".network-display.chip")

        self.__selenium_helper.find_and_click_bytext(self.__driver, "RPC personalizada")

        self.__selenium_helper.find_and_write_input(self.__driver, By.ID, "network-name", "Smart Chain")
        self.__selenium_helper.find_and_write_input(self.__driver, By.ID, "rpc-url", "https://bsc-dataseed.binance.org/")
        self.__selenium_helper.find_and_write_input(self.__driver, By.ID, "chainId", "56")
        self.__selenium_helper.find_and_write_input(self.__driver, By.ID, "network-ticker", "BNB")
        self.__selenium_helper.find_and_write_input(self.__driver, By.ID, "block-explorer-url", "https://bscscan.com")

        self.__selenium_helper.find_and_click_bytext(self.__driver, "Salvar")

        element = WebDriverWait(self.__driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//span[@class='currency-display-component__suffix' and contains(text(),'BNB')]"))
        )

        assert "BNB" in element.text


    def connect_wallet_to_game(self):
        self.__driver.switch_to.frame(self.__driver.find_element(By.XPATH, "//iframe"))

        self.__selenium_helper.find_and_click_bytext(self.__driver, "MetaMask")

        self.__driver.switch_to.default_content()    

        WebDriverWait(self.__driver, 10).until(
            EC.number_of_windows_to_be(2)
        )

        self.__selenium_helper.change_tab(self.__driver)

        self.__selenium_helper.find_and_click_bytext(self.__driver, "Próximo")

        self.__selenium_helper.find_and_click_bylocator(self.__driver, By.XPATH, "//button[contains(text(),'Conectar')]")

        WebDriverWait(self.__driver, 10).until(
            self.__selenium_helper.validate_closed_window
        )      

        WebDriverWait(self.__driver, 10).until(
            EC.number_of_windows_to_be(2)
        )

        self.__selenium_helper.change_tab(self.__driver, True)  

        self.__selenium_helper.change_tab(self.__driver)

        self.__selenium_helper.find_and_click_bytext(self.__driver, "Assinar")

        self.__selenium_helper.change_tab(self.__driver, True)