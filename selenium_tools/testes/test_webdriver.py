from selenium_tools.selenium_driver import SeleniumDriver
from selenium.webdriver.chrome.webdriver import WebDriver


def test_se_selenium_driver_retorna_um_webdriver():
    selenium_driver = SeleniumDriver()
    esperado = WebDriver
    assert isinstance(selenium_driver, esperado)

def test_se_options_passa_a_pasta_certa():
    download = r'C:\Users\rodri\Documents\League of Legends'
    selenium_driver = SeleniumDriver(download_path=download)
    assert selenium_driver.caps["options"] == download