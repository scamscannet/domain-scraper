import time
import uuid

from bs4 import BeautifulSoup
from selenium import webdriver

from config import Config

cfg = Config()

class Browser:
    def __init__(self):
        option = webdriver.FirefoxOptions()
        option.binary_location = cfg.FIREFOX_PATH
        self._browser = webdriver.Firefox(options=option)

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
