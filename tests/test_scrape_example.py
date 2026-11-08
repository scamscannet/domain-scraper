# The mock API (incl. /nodes/dispatcher/me) is started in tests/conftest.py before config gets imported;
# the `api` fixture comes from there too.
from client.data import upload_website_data
from client.jobs import get_or_wait_for_new_scraping_job
from scraper.scraper import Scraper


def test_scrape_example_com(api):
    scraper = Scraper()

    try:
        job = get_or_wait_for_new_scraping_job()
        result = scraper.scrape_website(job.domain)
        upload_website_data(result, job.id)
    finally:
        scraper.terminate()

    report = api["scrapes"][job.id]
    assert report["status"] == "online"
    assert report["domain"]["domain"] == "example"
    assert report["domain"]["tld"] == "com"
    assert "Example Domain" in report["code"]["title"]
