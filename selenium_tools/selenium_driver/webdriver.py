import logging
import os
from typing import Optional

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.remote.remote_connection import LOGGER
from urllib3.connectionpool import log as urllib_log
from webdriver_manager.chrome import ChromeDriverManager


def running_in_docker() -> bool:
    if os.path.exists("/.dockerenv"):
        return True

    cgroup_path = "/proc/1/cgroup"

    if not os.path.isfile(cgroup_path):
        return False

    with open(cgroup_path) as file:
        return any(
            container in line
            for line in file
            for container in (
                "docker",
                "kubepods",
                "containerd",
            )
        )


class SeleniumDriver:

    def __init__(
        self,
        download_path: Optional[str] = None,
        read_pdf: bool = True,
        log: bool = True,
        headless: bool = False,
        show_notifications: bool = False,
        escala_tela: float = 1.0,
        window_size: tuple[int, int] | None = None,
        proxy: Optional[str] = None,
    ) -> None:

        self.download_path = download_path
        self.read_pdf = read_pdf
        self.log = log
        self.headless = headless
        self.show_notifications = show_notifications
        self.escala_tela = escala_tela
        self.window_size = window_size
        self.proxy = proxy

        self.driver: WebDriver | None = None

    def _create_options(self) -> Options:
        options = Options()

        options.add_argument("--log-level=3")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")

        options.add_argument(
            f"--force-device-scale-factor={self.escala_tela}"
        )
        
        if self.proxy:
            options.add_argument(f"--proxy-server={self.proxy}")

        if self.window_size:
            options.add_argument(
                f"--window-size="
                f"{self.window_size[0]},"
                f"{self.window_size[1]}"
            )

        if not self.show_notifications:
            options.add_argument(
                "--disable-notifications"
            )

        if self.headless or running_in_docker():
            options.add_argument("--headless=new")

        if not self.log:
            LOGGER.setLevel(logging.ERROR)
            urllib_log.setLevel(logging.ERROR)

        prefs = {
            "plugins.always_open_pdf_externally": self.read_pdf,
        }

        if self.download_path:
            prefs["download.default_directory"] = (
                self.download_path
            )

        options.add_experimental_option(
            "prefs",
            prefs,
        )

        return options

    def get_driver(self) -> WebDriver:

        if self.driver is not None:
            return self.driver

        options = self._create_options()

        self.driver = webdriver.Chrome(
            options=options,
        )

        return self.driver

    def quit(self) -> None:

        if self.driver is None:
            return

        try:
            self.driver.quit()
        finally:
            self.driver = None

    def __enter__(self) -> WebDriver:
        return self.get_driver()

    def __exit__(
        self,
        exc_type,
        exc_value,
        traceback,
    ) -> None:
        self.quit()