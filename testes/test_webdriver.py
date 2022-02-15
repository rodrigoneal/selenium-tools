from selenium_tools.selenium_driver import SeleniumDriver,options
from selenium.webdriver.chrome.webdriver import WebDriver


def test_se_selenium_driver_retorna_um_webdriver():
    selenium_driver = SeleniumDriver()
    esperado = WebDriver
    assert isinstance(selenium_driver, esperado)

def test_se_options_passa_a_pasta_certa():
    download = r'C:\Users\rodri\Documents\League of Legends'
    selenium_driver = SeleniumDriver(download_path=download)
    assert selenium_driver.caps["options"] == download

def test_se_tem_como_passar_option():
    download_path = r'C:\Users\rodri\Documents\League of Legends'
    prefs = {}
    prefs["download.default_directory"] = download_path
    options.add_argument
    driver = SeleniumDriver()
    assert driver.caps["options"] == download_path
    