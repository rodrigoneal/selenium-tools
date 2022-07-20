"""
Modulo com Page Objects pronto.
"""

from abc import ABC
from contextlib import contextmanager
from typing import Callable, List

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement


class SeleniumObject:
    """Classe com os elementos do selenium."""
    def find_element(self, element: tuple,
                     condition: Callable = EC.presence_of_element_located,
                     time: float = 10) -> WebElement:
        """Procura um elemento na página e retorna o elemento."""
        return WebDriverWait(self.driver, time).until(condition(element))

    def find_elements(self, element: tuple,
                      condition: Callable = EC.presence_of_all_elements_located,
                      time: float = 10) -> List[WebElement]:
        """Prcura N elementos na pagina e retorna uma lista de elementos."""
        return WebDriverWait(self.driver, time).until(condition(element))

    def change_frame(self, frame):
        """Altera entre o frame da pagina"""
        self.driver.switch_to.frame(frame)

    def change_window(self, index: int = 1):
        """Altera entre a janela da pagina."""
        self.driver.switch_to.window(self.driver.window_handles[index])


class Page(ABC, SeleniumObject):
    """Pagina onde ficam os elementos."""

    def __init__(self, driver: webdriver, url=None):
        self.driver = driver
        self.url = url
        self._reflection()

    def _reflection(self):
        """Essa função faz com que não seja necessário ficar passando o driver para todos os elementos.
        Basta passar para a pagina e todos as suas dependencias terão o driver."""
        for atributo in dir(self):
            atributo_real = getattr(self, atributo)
            if isinstance(atributo_real, Element):
                atributo_real.driver = self.driver
    @contextmanager
    def open(self):
        """Navega para o url passado."""
        exc = None
        try:
            self.driver.maximize_window()
            self.driver.get(self.url)
            yield
        except Exception as _exc:
            exc = _exc
        finally:
            self.driver.close()
            if exc: raise exc
    
    def close(self):
        self.driver.close()


class Element(ABC, SeleniumObject):
    """Elementos da pagina."""

    def __init__(self, driver: webdriver = None):
        self.driver = driver
