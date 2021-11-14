from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By


driver: WebDriver

#region Helpers
def setup_driver():
    chrome_options = Options()
    chrome_options.add_extension('browser_driver\extensions\MetaMask.crx')
    driver = webdriver.Chrome("browser_driver\chromedriver.exe", options=chrome_options)
    driver.implicitly_wait(10)   
    return driver  
    

def change_tab():
    p = driver.current_window_handle
    chwd = driver.window_handles
    for w in chwd:
        if(w!=p):
            driver.switch_to.window(w)            
        break


def find_and_click_bytext(text):
    start_button = driver.find_element(By.XPATH, f"//*[contains(text(),'{text}')]")
    start_button.click()


def find_and_click_bylocator(by, locator):
    start_button = driver.find_element(by, locator)
    start_button.click()


def find_and_write_input(by, locator, input_text):
    elem = driver.find_element(by, locator)
    elem.send_keys(input_text)
#endregion

#region Examples
def commands_examples():
    assert "Python" in driver.title
    elem = driver.find_element(By.NAME, "q")
    elem.clear()
    elem.send_keys("pycon")
    elem.send_keys(Keys.RETURN)
    assert "No results found." not in driver.page_source
#endregion

def configure_metamask():
    change_tab()

    find_and_click_bytext("Comece agora")
    find_and_click_bytext("Importar carteira")
    find_and_click_bytext("Concordo")

    find_and_write_input(By.XPATH, "//input[contains(@placeholder,'Frase de recuperação')]", "height carpet cabin broken snap dress market coil like tube success intact")
    find_and_write_input(By.ID, "password", "12340987")
    find_and_write_input(By.ID, "confirm-password", "12340987")

    find_and_click_bylocator(By.XPATH, "//span[text()='Eu li e concordo com ']")

    find_and_click_bytext("Importar")
    find_and_click_bytext("Tudo pronto")

    configure_wallet()


def configure_wallet():
    find_and_click_bylocator(By.CSS_SELECTOR, ".network-display.chip")

    find_and_click_bytext("RPC personalizada")

    find_and_write_input(By.ID, "network-name", "Smart Chain")
    find_and_write_input(By.ID, "rpc-url", "https://bsc-dataseed.binance.org/")
    find_and_write_input(By.ID, "chainId", "56")
    find_and_write_input(By.ID, "network-ticker", "BNB")
    find_and_write_input(By.ID, "block-explorer-url", "https://bscscan.com")

    find_and_click_bytext("Salvar")


driver = setup_driver()
configure_metamask()

change_tab()

driver.get("https://app.bombcrypto.io")

driver.close()

