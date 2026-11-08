import pytest

from scraper.models.scraper.url import Url
from scraper.scraper import Scraper


@pytest.fixture(scope="module")
def scraper():
    s = Scraper()
    yield s
    s.terminate()


def test_offline(scraper):
    # .invalid is reserved and never resolves
    result = scraper.scrape_website(Url(domain="scamscan-offline-test", tld="invalid"))

    assert result.website_data.status == "offline"


def test_redirect(scraper):
    # fb.com redirects to facebook.com
    result = scraper.scrape_website(Url(domain="fb", tld="com"))

    assert result.redirect_data is not None
    assert result.redirect_data.redirect_to.domain == "facebook"


def test_http_only_is_no_redirect(scraper):
    # httpforever.com has no https; falling back to http must not count as a redirect
    result = scraper.scrape_website(Url(domain="httpforever", tld="com"))

    assert result.website_data.status == "online"
    assert result.redirect_data is None


def test_no_redirect(scraper):
    result = scraper.scrape_website(Url(domain="example", tld="com"))

    assert result.website_data.status == "online"
    assert result.redirect_data is None
