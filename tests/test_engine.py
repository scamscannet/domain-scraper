import pytest
from scraper.engine.checks import check_for_http_or_https_and_return_url


def test_checks():
    domain = "google.de"
    redirect, c1 = check_for_http_or_https_and_return_url(domain)

    assert c1.startswith('https')

    # Check whether for excpetion when providing unavailable webpage
    unavailable_domain = "thisIsNotExistingAndSurelyNoOneWillEverRegisterIt.ng"
    with pytest.raises(Exception):
        check_for_http_or_https_and_return_url(unavailable_domain)
