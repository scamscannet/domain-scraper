import logging
import uuid
from pathlib import Path
from tempfile import TemporaryDirectory

from playwright.sync_api import sync_playwright

from config import get_config
from scraper.exceptions import EngineError, WebsiteError
from scraper.models.scraper.url import parse_url
from scraper.models.scraper.scraping_result import RawScrapingResult
from scraper.models.scraper.screenshots import Screenshots


# Errors that are caused by the engine and not by the website
ENGINE_ERRORS = (
    "has been closed",               # page, context or browser closed / crashed
    "Target crashed",
    "Connection closed",             # lost the connection to the browser process
    "is not a valid URL",            # URL we built is broken
    "net::ERR_INVALID_URL",
    "net::ERR_INTERNET_DISCONNECTED",
    "net::ERR_NETWORK_CHANGED",
    "net::ERR_NETWORK_ACCESS_DENIED",
    "net::ERR_NAME_RESOLUTION_FAILED",  # our DNS resolver failed (unknown domain is ERR_NAME_NOT_RESOLVED)
    "net::ERR_PROXY_",
    "net::ERR_INSUFFICIENT_RESOURCES",
    "net::ERR_OUT_OF_MEMORY",
)


class PlaywrightBrowser:

    def __init__(self):
        self._launch_browser()

    def _launch_browser(self):
        self.p = sync_playwright().start()
        self._browser = self.p.chromium.launch(
            headless=get_config().HEADLESS,
            timeout=get_config().TIMEOUT,

        )

    def terminate(self):
        try:
            self._browser.close()
        except Exception:
            pass
        try:
            self.p.stop()
        except Exception:
            pass

    def scrape(self, url: str) -> RawScrapingResult:
        if not self.is_browser_alive():
            logging.warning("Browser died, restarting")
            try:
                self.terminate()
            except Exception:
                pass
            self._launch_browser()

        with TemporaryDirectory() as tmp:
            har_path = Path(tmp) / f"{uuid.uuid4()}.har"

            # Set up new browser
            try:
                ctx = self._browser.new_context(
                    locale="en-US",
                    extra_http_headers={"Accept-Language": "en-US,en;q=0.9"},
                    ignore_https_errors=True,  # scrape sites with expired/self-signed certs instead of failing on https
                    record_har_content="omit",
                    record_har_path=har_path
                )
            except:
                raise EngineError("Error while setting up browser")

            try:
                page = ctx.new_page()
            except:
                ctx.close()
                raise EngineError("Error while opening new page context")

            try:
                page.goto(url)
            except Exception as e:
                page.close()
                ctx.close()
                if any(err in str(e) for err in ENGINE_ERRORS):
                    raise EngineError(f"Error while opening page: {e}") from e
                raise WebsiteError(f"Error while opening page: {e}") from e

            try:
                sourcecode = page.content()
                final_url = page.url
                url = parse_url(final_url)
                screenshots = Screenshots(
                    full=page.screenshot(full_page=True),
                    visible=page.screenshot()
                )
            except Exception as e:
                raise EngineError(f"Error while parsing page: {e}")
            finally: # Runs even on except when it returns
                page.close()
                ctx.close()

            return RawScrapingResult(
                har_bytes=har_path.read_bytes(),
                sourcecode=sourcecode,
                screenshots=screenshots,
                url=url,
                final_url=final_url,
            )

    def is_browser_alive(self):
        try:
            return self._browser.is_connected()
        except Exception:
            return False
