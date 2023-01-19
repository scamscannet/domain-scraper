from selenium import webdriver

from scraper.models.domain import Domain


class Module:
    name: str
    def check_if_eligible(self, url: Domain) -> bool:
        return False

    def pre_save(self, browser: webdriver.Firefox):
        pass

    def parse(self, site_soup) -> dict:
        return {}

