from configparser import ConfigParser
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from crypto_automation.commands.web_manipulation.helper import SeleniumHelper
import keyring  

class ConnectWallet:
    def __init__(self, driver: WebDriver, config: ConfigParser):
        self.__driver = driver
        self.__config = config
        self.__selenium_helper =  SeleniumHelper(config)        


    def configure_wallet(self):
        self.__selenium_helper.change_tab(self.__driver)

        self.__selenium_helper.find_and_click_bytext(self.__driver, "Comece agora")
        self.__selenium_helper.find_and_click_bytext(self.__driver, "Importar carteira")
        self.__selenium_helper.find_and_click_bytext(self.__driver, "Concordo")

        self.__selenium_helper.find_and_write_input(self.__driver, By.XPATH, "//input[contains(@placeholder,'Frase de recuperação')]", keyring.get_password(self.__config['SECURITY']['serviceid'], "secret_phrase"))
        self.__selenium_helper.find_and_write_input(self.__driver, By.ID, "password", keyring.get_password(self.__config['SECURITY']['serviceid'], "secret_password"))
        self.__selenium_helper.find_and_write_input(self.__driver, By.ID, "confirm-password", keyring.get_password(self.__config['SECURITY']['serviceid'], "secret_password"))

        self.__selenium_helper.find_and_click_bylocator(self.__driver, By.XPATH, "//span[text()='Eu li e concordo com ']")

        self.__selenium_helper.find_and_click_bytext(self.__driver, "Importar")
        self.__selenium_helper.find_and_click_bytext(self.__driver, "Tudo pronto")

        self.__configure_wallet_network()   

        self.__configure_idle_deactivation_timeout()     
    
        self.__driver.close()

        self.__selenium_helper.change_tab(self.__driver, True)


    def __configure_wallet_network(self):
        self.__selenium_helper.find_and_click_bylocator(self.__driver, By.CSS_SELECTOR, ".network-display.chip")

        self.__selenium_helper.find_and_click_bytext(self.__driver, "Adicionar rede")

        self.__selenium_helper.find_and_write_input(self.__driver, By.XPATH, self.__network_wallet_xpath("Nome da rede"), self.__config['WALLETNETWORK']['networkname'])
        self.__selenium_helper.find_and_write_input(self.__driver, By.XPATH, self.__network_wallet_xpath("Novo URL da RPC"), self.__config['WALLETNETWORK']['newrpcurl'])
        self.__selenium_helper.find_and_write_input(self.__driver, By.XPATH, self.__network_wallet_xpath("ID da chain"), self.__config['WALLETNETWORK']['chainid'])
        self.__selenium_helper.find_and_write_input(self.__driver, By.XPATH, self.__network_wallet_xpath("Símbolo da moeda"), self.__config['WALLETNETWORK']['symbol'])
        self.__selenium_helper.find_and_write_input(self.__driver, By.XPATH, self.__network_wallet_xpath("URL do Block Explorer"), self.__config['WALLETNETWORK']['blockexplorerurl'])

        self.__selenium_helper.find_and_click_bytext(self.__driver, "Salvar")

        element = WebDriverWait(self.__driver, self.__config['TIMEOUT'].getint('webscraping')).until(
            EC.presence_of_element_located((By.XPATH, "//span[@class='currency-display-component__suffix' and contains(text(),'BNB')]"))
        )

        assert "BNB" in element.text
        

    def __configure_idle_deactivation_timeout(self):
        self.__selenium_helper.find_and_click_bylocator(self.__driver, By.CSS_SELECTOR, ".network-display.chip")

        self.__selenium_helper.find_and_click_bytext(self.__driver, "Adicionar rede")

        self.__selenium_helper.find_and_click_bytext(self.__driver, "Avançadas")

        self.__selenium_helper.find_and_write_input(self.__driver, By.ID, "autoTimeout", "9999")

        self.__selenium_helper.find_and_click_bylocator(self.__driver, By.XPATH, "//*[@id='autoTimeout']//ancestor::div[position()=3]//button")        


    def connect_wallet_to_game(self, reconnect  = False):
        self.__driver.switch_to.frame(self.__driver.find_element(By.XPATH, "//iframe"))

        self.__selenium_helper.find_and_click_bytext(self.__driver, "MetaMask")

        self.__driver.switch_to.default_content()    

        WebDriverWait(self.__driver, self.__config['TIMEOUT'].getint('webscraping')).until(
            EC.number_of_windows_to_be(2)
        )

        if reconnect  == False:
            self.__selenium_helper.change_tab(self.__driver)    

            self.__selenium_helper.find_and_click_bytext(self.__driver, "Próximo")

            self.__selenium_helper.find_and_click_bylocator(self.__driver, By.XPATH, "//button[contains(text(),'Conectar')]")

            WebDriverWait(self.__driver, self.__config['TIMEOUT'].getint('webscraping')).until(
                self.__selenium_helper.validate_closed_window
            )      

            WebDriverWait(self.__driver, self.__config['TIMEOUT'].getint('webscraping')).until(
                EC.number_of_windows_to_be(2)
            )

            self.__selenium_helper.change_tab(self.__driver, True)  

        self.__selenium_helper.change_tab(self.__driver)

        self.__selenium_helper.find_and_click_bytext(self.__driver, "Assinar")

        self.__selenium_helper.change_tab(self.__driver, True)


    def __network_wallet_xpath(self, name):
        return f"//*[contains(text(), '{name}')]//ancestor::div[@class='form-field']//input"
