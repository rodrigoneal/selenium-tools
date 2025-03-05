import logging
from typing import Optional

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.remote.remote_connection import LOGGER
from urllib3.connectionpool import log as urllib_log
from webdriver_manager.chrome import ChromeDriverManager

options = webdriver.ChromeOptions()


class SeleniumDriver:
    prefs = {}
    options.add_experimental_option("prefs", prefs)
    s = Service(ChromeDriverManager().install())

    def __init__(
        self,
        download_path: Optional[str] = None,
        read_pdf: bool = True,
        log: bool = True,
        headless: bool = False,
        show_notifications: bool = False,
    ) -> None:
        self.download_path = download_path
        self.read_pdf = read_pdf
        self.log = log
        self.headless = headless
        self.show_notifications = show_notifications
        self._prime()

    def _prime(self):
        options.add_argument("--log-level=3")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        if not self.show_notifications:
            options.add_argument("--disable-notifications")

        if self.download_path:
            self.prefs["download.default_directory"] = self.download_path
        self.prefs["plugins.always_open_pdf_externally"] = self.read_pdf
        if not self.log:
            LOGGER.setLevel(logging.ERROR)
            urllib_log.setLevel(logging.ERROR)
            options.add_argument("--log-level=3")
        if self.headless:
            options.add_argument("--headless=new")

    def get_driver(self) -> WebDriver:
        driver = webdriver.Chrome(options=options)
        driver.caps["options"] = self.download_path or options._caps.get(
            "goog:chromeOptions"
        ).get("prefs").get("download.default_directory")
        return driver

    def __enter__(self):
        return self.get_driver()

    def __exit__(self, type, value, traceback):
        self.get_driver().quit()
