"""
Modulo com Page Objects pronto.
"""

from abc import ABC
from contextlib import contextmanager
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Callable, List, Optional, Tuple

from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains


class SeleniumObject:
    """Pattern Page Objects"""

    def find_element_and_clear(
        self,
        element: Tuple[str, str],
        condition: Callable = EC.presence_of_element_located,
        time: float = 10,
    ) -> WebElement:
        """Encontra um elemento web e limpa o valor.

        Args:
            element (Tuple[str, str]): Com elementos que serão buscando na tela ex:(By.XPATH, "//body").
            condition (Callable, optional): Vai aguardar até o status passando na condição. Defaults to EC.presence_of_element_located.
            time (float, optional): Tempo que vai aguardar o elemento aparecer antes de levantar exceção. Defaults to 10.

        Returns:
            WebElement
        """

        element = WebDriverWait(self.driver, time).until(condition(element))
        element.clear()
        return element

    def find_and_scroll(
        self,
        element: Tuple[str, str],
        condition: Callable = EC.presence_of_element_located,
        time: float = 10,
    ) -> WebElement:
        """Encontra um elemento web e rola para ele.

        Args:
            element (Tuple[str, str]): Com elementos que são buscando na tela ex:(By.XPATH, "//body").
            condition (Callable, optional): Vai aguardar até o status passando na condição. Defaults to EC.presence_of_element_located.
            time (float, optional): Tempo que vai aguardar o elemento aparecer antes de levantar exceção. Defaults to 10.

        Returns:
            WebElement
        """

        element = WebDriverWait(self.driver, time).until(condition(element))
        actions = ActionChains(self.driver)
        actions.move_to_element(element).perform()
        return element

    def find_element(
        self,
        element: Optional[Tuple[str, str]] = None,
        condition: Callable = EC.presence_of_element_located,
        time: float = 10,
    ) -> WebElement:
        """Encontra um elemento web.

        Args:
            element (Tuple[str, str]): Com elementos que serão buscando na tela ex:(By.XPATH, "//body").
            condition (Callable, optional): Vai aguardar até o status passando na condição. Defaults to EC.presence_of_element_located.
            time (float, optional): Tempo que vai aguardar o elemento aparecer antes de levantar exceção. Defaults to 10.

        Returns:
            WebElement
        """
        if element:
            return WebDriverWait(self.driver, time).until(condition(element))
        try:
            return WebDriverWait(
                self.driver, time
            ).until(
                condition()
            )  # Caso não tenha passado o elemento, ele vai retornar o driver e deseja esperar um alerta por exemplo.
        except TypeError:
            return WebDriverWait(self.driver, time).until(condition)

    def find_elements(
        self,
        element: Tuple[str, str],
        condition: Callable = EC.presence_of_all_elements_located,
        time: float = 10,
    ) -> List[WebElement]:
        """Encontra n elementos web.

        Args:
            element (Tuple[str, str]): Com elementos que serão buscando na tela ex:(By.XPATH, "//body").
            condition (Callable, optional): Vai aguardar até o status passando na condição. Defaults to EC.presence_of_element_located.
            time (float, optional): Tempo que vai aguardar o elemento aparecer antes de levantar exceção. Defaults to 10.

        Returns:
            List[WebElement]
        """
        return WebDriverWait(self.driver, time).until(condition(element))

    def captcha_breaker(
        self,
        image_captcha_resolve: Callable,
        element: Tuple[str, str],
        writter_element: Tuple[str, str] = None,
        condition: Callable = EC.presence_of_element_located,
        time: float = 10,
    ):
        """Quebra o captcha por imagem.
        Args:
            image_captcha_resolve(Callable): Funcão para resolver o captcha por imagem.
            element (tuple): Elemento do selenium.
            writter_element (tuple): Elemento que você deseja escrever o resultado do captcha.
            condition (Callable, optional): Condição para aguardar o elemento. Defaults to EC.presence_of_element_located.
            time (float, optional): Tempo de espera de um elemento na tela. Defaults to 10.

        Returns:
            str: resultado do captcha
        """
        with NamedTemporaryFile("wb+", suffix=".png", delete=False) as tempfile:
            img_path = tempfile.name
            self.find_element(element, condition, time).screenshot(img_path)
            result = image_captcha_resolve(img_path)
        Path(img_path).unlink(missing_ok=True)

        if writter_element:
            self.find_element(writter_element).send_keys(result)
        return result

    def recaptcha_breaker(
        self,
        recaptcha: Callable,
        element: Tuple[str, str],
        condition: Callable = EC.presence_of_element_located,
        time: float = 10,
    ):
        """Quebra o captcha do recaptcha.
        Args:
            element (tuple): Elemento do selenium.
            condition (Callable, optional): Condição para aguardar o elemento. Defaults to EC.presence_of_element_located.
            time (float, optional): Tempo de espera de um elemento na tela. Defaults to 10.

        """
        element = self.find_element(element, condition, time)
        website_key = element.get_attribute("data-sitekey")
        website_url = self.driver.current_url
        task_id = recaptcha(website_key=website_key, website_url=website_url)
        self.driver.execute_script(
            "document.getElementsByClassName('g-recaptcha-response')[0].innerHTML = "
            f"'{task_id}';"
        )

    def recaptcha_breaker_v2(self, recaptcha: Callable, website_key: str):
        """Metodo menos direto de quebrar captcha, algumas paginas estão escondendo o sitekey dentro de funções do JS

        Args:
            website_key (str): sitekey do site
        """
        website_url = self.driver.current_url
        task_id = recaptcha(website_key=website_key, website_url=website_url)
        self.driver.execute_script(
            "document.getElementsByClassName('g-recaptcha-response')[0].innerHTML = "
            f"'{task_id}';"
        )

    def execute_script(self, element: WebElement, js_script: str):
        """Executa um script.

        Args:
            element (WebElement): Elemento selenium
            js_script (str): script

        Returns:
            str: Retorno do script
        """
        if element:
            return self.driver.execute_script(js_script, element)
        return self.driver.execute_script(js_script)

    @contextmanager
    def change_frame_context(
        self, frame: WebElement, main_frame: Optional[WebElement] = None
    ):
        """Altera o frame que vai ser manipulado.

        Args:
            frame (WebElement): Frame que vai ser manipulado
            main_frame (Optional[WebElement], optional): Frame principal. Defaults to None.
        """
        self.driver.switch_to.frame(frame)
        try:
            yield
        finally:
            if main_frame:
                self.driver.switch_to.frame(main_frame)
            else:
                self.driver.switch_to.default_content()

    def change_frame(self, frame: WebElement):
        """Altera o frame que vai ser manipulado.

        Args:
            frame (WebElement): Frame que vai ser manipulado
            main_frame (Optional[WebElement], optional): Frame principal. Defaults to None.
        """
        self.driver.switch_to.frame(frame)

    def change_window(self, index: int = 1):
        """Alterá a janela que está sendo manipulada

        Args:
            index (int, optional): index da pagina que vai manipular. Defaults to 1.
        """
        self.driver.switch_to.window(self.driver.window_handles[index])

    def wait_text_change(
        self,
        element: Tuple[str, str],
        old_text: str,
        time: float = 10,
    ) -> str:
        """Aguarda até que o texto de um elemento mude.

        Args:
            element (Tuple[str, str]): Localizador do elemento (ex: (By.XPATH, "//div[@id='mensagem']")).
            old_text (str): Texto antigo que será comparado.
            time (float, optional): Tempo máximo de espera em segundos. Defaults to 10.

        Returns:
            str: Novo texto do elemento após mudança.
        """

        def text_changed(driver):
            try:
                el = driver.find_element(*element)
                return el.text != old_text and el.text
            except Exception:
                return False

        WebDriverWait(self.driver, time).until(text_changed)
        return self.driver.find_element(*element).text


class Page(ABC, SeleniumObject):
    """Pagina onde ficam os elementos."""

    def __init__(self, driver: webdriver, url=str | None):
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

    def open(self, maximize_window: bool = True):
        """Navega para o url passado."""
        if maximize_window:
            self.driver.maximize_window()
        self.driver.get(self.url)

    def close(self):
        """Fecha o browser."""
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
