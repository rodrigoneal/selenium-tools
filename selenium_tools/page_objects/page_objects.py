"""
Modulo com Page Objects pronto.
"""

from abc import ABC
from pathlib import Path
from tempfile import TemporaryFile
from typing import Callable, List, Tuple

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement

from captcha_breaker import Breakers


class SeleniumObject:
    """Pattern Page Objects
    """

    def find_element(self, element: Tuple[str, str],
                     condition: Callable = EC.presence_of_element_located,
                     time: float = 10) -> WebElement:
        """Encontra um elemento web.

        Args:
            element (Tuple[str, str]): Com elementos que serão buscando na tela ex:(By.XPATH, "//body").
            condition (Callable, optional): Vai aguardar até o status passando na condição. Defaults to EC.presence_of_element_located.
            time (float, optional): Tempo que vai aguardar o elemento aparecer antes de levantar exceção. Defaults to 10.

        Returns:
            WebElement
        """
        return WebDriverWait(self.driver, time).until(condition(element))

    def find_elements(self, element: Tuple[str, str],
                      condition: Callable = EC.presence_of_all_elements_located,
                      time: float = 10) -> List[WebElement]:
        """Encontra n elementos web.

        Args:
            element (Tuple[str, str]): Com elementos que serão buscando na tela ex:(By.XPATH, "//body").
            condition (Callable, optional): Vai aguardar até o status passando na condição. Defaults to EC.presence_of_element_located.
            time (float, optional): Tempo que vai aguardar o elemento aparecer antes de levantar exceção. Defaults to 10.

        Returns:
            List[WebElement]
        """
        return WebDriverWait(self.driver, time).until(condition(element))

    def captcha_breaker(self, element: Tuple[str, str],
                        condition: Callable = EC.presence_of_element_located,
                        time: float = 10):
        """Quebra o captcha por imagem.
        Args:
            element (tuple): Elemento do selenium.
            condition (Callable, optional): Condição para aguardar o elemento. Defaults to EC.presence_of_element_located.
            time (float, optional): Tempo de espera de um elemento na tela. Defaults to 10.

        Returns:
            str: resultado do captcha
        """
        breakers = Breakers()
        img = self.find_element(element, condition, time).screenshot_as_png
        with TemporaryFile("wb+", suffix=".png", delete=False) as tempfile:
            tempfile.write(img)
            img_path = tempfile.name
        result = breakers.image_captcha(img_path)
        try:
            Path(img_path).unlink(missing_ok=True)
        except:
            pass
        return result

    def change_frame(self, frame: WebElement):
        """Muda o frame da pagina.

        Args:
            frame (WebElement): Elemento com os dados do frame.
        """
        self.driver.switch_to.frame(frame)

    def change_window(self, index: int = 1):
        """Alterá a janela que está sendo manipulada

        Args:
            index (int, optional): index da pagina que vai manipular. Defaults to 1.
        """
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

    def open(self):
        """Navega para o url passado."""
        self.driver.maximize_window()
        self.driver.get(self.url)

    def close(self):
        """Fecha o browser.
        """
        self.driver.quit()

    def __enter__(self):
        """Cria um contexto que no final fecha o navegador.

        Returns:
            Self
        """
        self.open()
        return self

    def __exit__(self, type, value, traceback):
        """Cria um contexto que no final fecha o navegador."""
        self.close()
        if traceback:
            raise type(value)


class Element(ABC, SeleniumObject):
    """Elementos da pagina."""

    def __init__(self, driver: webdriver = None):
        self.driver = driver
