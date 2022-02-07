from typing import Optional

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.webdriver import WebDriver
from webdriver_manager.chrome import ChromeDriverManager



options = webdriver.ChromeOptions()

class SeleniumDriver:
    prefs = {}
    options.add_experimental_option("prefs", prefs)
    s = Service(ChromeDriverManager().install())

    def __new__(cls, download_path: Optional[str] = None,read_pdf: bool = True) -> WebDriver:
        if download_path:
            cls.download_path = download_path
            cls.prefs["download.default_directory"] = download_path
        if not read_pdf:
            cls.prefs["plugins.always_open_pdf_externally"] = True
        driver = webdriver.Chrome(service=cls.s, chrome_options=options)
        driver.caps['options']= download_path
        return driver
        


