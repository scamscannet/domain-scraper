import asyncio
import time

import pytest
from scraper.engine.checks import check_for_http_or_https_and_return_url
from scraper.engine.browser import Browser


def test_checks():
    domain = "google.de"
    c1 = asyncio.run(check_for_http_or_https_and_return_url(domain))

    assert c1.startswith('https')

    # Check whether for excpetion when providing unavailable webpage
    unavailable_domain = "thisIsNotExistingAndSurelyNoOneWillEverRegisterIt.ng"
    with pytest.raises(Exception):
        asyncio.run(check_for_http_or_https_and_return_url(unavailable_domain))


def test_browser():
    browser = Browser()
    assert browser.isBrowserAlive()

    sourcecode, _ = browser.get_website_sourcecode_and_screenshot('https://example.com/')

    assert "https://www.iana.org/domains/example" in sourcecode

    browser.close()
    time.sleep(1)
    print(browser.isBrowserAlive())
    assert not browser.isBrowserAlive()
