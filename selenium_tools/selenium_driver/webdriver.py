import logging
import os
from typing import Optional

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.remote.remote_connection import LOGGER
from urllib3.connectionpool import log as urllib_log
from webdriver_manager.chrome import ChromeDriverManager

options = webdriver.ChromeOptions()

def running_in_docker() -> bool:
    path = "/proc/1/cgroup"
    if os.path.exists("/.dockerenv"):
        return True
    if os.path.isfile(path):
        with open(path) as f:
            return any("docker" in line or "kubepods" in line or "containerd" in line for line in f)
    return False


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
        escala_tela: float = 1.0,
        window_size: tuple[int, int] = False,
    ) -> None:
        self.download_path = download_path
        self.read_pdf = read_pdf
        self.log = log
        self.headless = headless
        self.show_notifications = show_notifications
        self.escala_tela = escala_tela
        self.window_size = window_size
        self._prime()
        self.driver = None

    def _prime(self):
        options.add_argument("--log-level=3")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        if self.window_size:
            options.add_argument(f"--window-size={self.window_size[0]},{self.window_size[1]}")
        options.add_argument(f"--force-device-scale-factor={self.escala_tela}")
        if not self.show_notifications:
            options.add_argument("--disable-notifications")

        if self.download_path:
            self.prefs["download.default_directory"] = self.download_path
        self.prefs["plugins.always_open_pdf_externally"] = self.read_pdf
        if not self.log:
            LOGGER.setLevel(logging.ERROR)
            urllib_log.setLevel(logging.ERROR)
            options.add_argument("--log-level=3")
        if self.headless or running_in_docker():
            options.add_argument("--headless=new")

    def get_driver(self) -> WebDriver:
        driver = webdriver.Chrome(options=options)
        driver.caps["options"] = self.download_path or options._caps.get(
            "goog:chromeOptions"
        ).get("prefs").get("download.default_directory")
        return driver

    def __enter__(self):
        self.driver = self.get_driver()
        return self.driver

    def __exit__(self, type, value, traceback):
        self.driver.quit()
