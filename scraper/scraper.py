from bs4 import BeautifulSoup

from config import get_config
from scraper.engine.pwright import PlaywrightBrowser
from scraper.exceptions import FailedScrape, ScraperError, EngineError, WebsiteError
from scraper.models.scraper.scraping_result import ScrapingResult, RawScrapingResult
from scraper.models.scraper.website_data import WebsiteData
from scraper.models.scraper.url import Url
from scraper.modules.modules import get_module_for_url
from log import logging


class Scraper:
    _browser: PlaywrightBrowser

    def __init__(self):
        self._browser = PlaywrightBrowser()

    def _scrape_protocol_agnostic(self, url) -> RawScrapingResult:
        # Try HTTPS
        try:
            scraping_result = self._browser.scrape("https://" + url.to_url_without_protocol())
            return scraping_result

        except WebsiteError:
            pass
        except EngineError as e:
            raise ScraperError(f"Scraper failed with {e}")
        except Exception as e:
            raise ScraperError(f"Scraper failed due to an unhandled error {e}")


        logging.warning(f"Scraping HTTPS failed. Retrying with http....")

        try:
            scraping_result = self._browser.scrape("http://" + url.to_url_without_protocol())
            return scraping_result

        except WebsiteError:
            pass
        except EngineError as e:
            raise ScraperError(f"Scraper failed with {e}")
        except Exception as e:
            raise ScraperError(f"Scraper failed due to an unhandled error {e}")

        raise FailedScrape()

    def scrape_website(self, url: Url) -> ScrapingResult:
        website_data = WebsiteData(
            status="online",
            url=url,
            node=get_config().NODE
        )
        redirect_data = None

        try:
            scraping_result = self._scrape_protocol_agnostic(url)
        except FailedScrape:
            logging.warning(f"The website cannot be scraped. Nothing indicates a code failure so reporting it as offline.")
            website_data.status = "offline"
            return ScrapingResult(
                website_data=website_data,
            )
        # parse soup source code
        site_soup = BeautifulSoup(scraping_result.sourcecode, features="lxml")

        # Detect if it got redirected
        is_redirect = not url.is_same_page(scraping_result.url)

        if is_redirect:
            redirect_data = WebsiteData(
                url=url,
                status="redirect",
                redirect_to=scraping_result.url,
                node=get_config().NODE
            )
            website_data.url = scraping_result.url


        modules = get_module_for_url(website_data.url if website_data.url else url) # Selects all eligible modules
        for module in modules:
            website_data.modules[module.name] = module.parse(
                website_data.url,
                site_soup,
                scraping_result,
            ) if module else {}


        return ScrapingResult(
            website_data=website_data,
            redirect_data=redirect_data,
            screenshots=scraping_result.screenshots,
        )

    def terminate(self):
        self._browser.terminate()


if __name__ == "__main__":
    s = Scraper()
    s.scrape_website(Url(domain="cosmoshield", tld="org"))
