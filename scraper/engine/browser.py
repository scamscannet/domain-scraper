import time
import uuid

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common import WebDriverException

from config import Config

cfg = Config()


class Browser:
    def __init__(self):
        self._browser = None
        self.create_browser_instance()

    def create_browser_instance(self):
        options = webdriver.FirefoxOptions()
        if cfg.HEADLESS:
            options.headless = True
        options.binary_location = cfg.FIREFOX_PATH

        # Check if browser exists and if so try to close
        if self._browser:
            try:
                self._browser.close()
            except Exception:
                pass


        self._browser = webdriver.Firefox(options=options)
        self._browser.set_page_load_timeout(cfg.TIMEOUT)

    def get_website_sourcecode_and_screenshot(self, url) -> [str, str]:
        try:
            self._browser.get(url)
        except Exception as exc:
            if "Tried to run command without establishing a connection" in str(exc) or "is not a valid URL" in str(exc):
                return None
        sourcecode = self._browser.page_source
        image_id = str(uuid.uuid4())
        image_path = f'scraper/images/{image_id}.png'
        self._browser.save_screenshot(image_path)
        return sourcecode, image_path

    def get_website_soup(self, url: str) -> BeautifulSoup:
        html, = self.get_website_sourcecode_and_screenshot(url)
        return BeautifulSoup(html, "html.parser")

    def sourcecode_to_soup(self, source: str) -> BeautifulSoup:
        return BeautifulSoup(source, "html.parser")

    def close(self):
        self._browser.close()

    def isBrowserAlive(self):
        try:
            assert (self._browser.service.process.poll() == None)  # Returns an int if dead and None if alive
            self._browser.service.assert_process_still_running()  # Throws a WebDriverException if dead
            return True
        except (WebDriverException, AssertionError):
            return False
        except Exception as ex:
            return False