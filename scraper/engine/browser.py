import selenium
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common import WebDriverException

from config import Config
from scraper.models.scraper.screenshots import Screenshots

cfg = Config()

parking_domain = "https://example.com"


class Browser:
    _browser: webdriver.Firefox = None

    def __init__(self):
        self.create_browser_instance()

    def create_browser_instance(self):
        # Profile
        profile = webdriver.FirefoxProfile()
        profile.set_preference("browser.cache.disk.enable", False)
        profile.set_preference("browser.cache.memory.enable", False)
        profile.set_preference("browser.cache.offline.enable", False)
        profile.set_preference("network.http.use-cache", False)
        profile.set_preference('intl.accept_languages', 'en-US')

        # Options
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

        self._browser = webdriver.Firefox(options=options, firefox_profile=profile)
        self._browser.set_page_load_timeout(cfg.TIMEOUT)

    def browser_cleanup(self):
        try:
            self._browser.delete_all_cookies()
        except selenium.common.exceptions.NoSuchWindowException:
            self.create_browser_instance()

    def get_website_sourcecode_and_screenshot(self, url) -> [str, str, str]:
        self.browser_cleanup()
        try:
            self._browser.get(url)
        except Exception as exc:
            if "Tried to run command without establishing a connection" in str(exc) or "is not a valid URL" in str(exc):
                return None
            raise exc
        sourcecode = self._browser.page_source

        visible_screenshot_io = self._browser.get_screenshot_as_png()
        full_screenshot_io = self._browser.get_full_page_screenshot_as_png()

        screenshots = Screenshots(
            full=full_screenshot_io,
            visible=visible_screenshot_io
        )
        return sourcecode, screenshots, self._browser.current_url

    def get_website_soup(self, url: str) -> BeautifulSoup:
        html, = self.get_website_sourcecode_and_screenshot(url)
        return BeautifulSoup(html, "html.parser")

    def sourcecode_to_soup(self, source: str) -> BeautifulSoup:
        return BeautifulSoup(source, "html.parser")

    def close(self):
        self._browser.close()

    def isBrowserAlive(self):
        try:
            url = self._browser.current_url
            return True
        except (WebDriverException, AssertionError):
            return False
        except Exception as ex:
            return False

    def park_scraper(self):
        self._browser.get(parking_domain)
