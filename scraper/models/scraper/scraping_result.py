from pydantic import BaseModel

from scraper.models.scraper.domain import Domain
from scraper.models.scraper.website_data import WebsiteData
from scraper.models.scraper.screenshots import Screenshots

class ScrapingResult(BaseModel):
    website_data: WebsiteData
    screenshots: Screenshots = None

class ScrapingWebsiteRedirect(BaseModel):
    domain: Domain
    destination: str

