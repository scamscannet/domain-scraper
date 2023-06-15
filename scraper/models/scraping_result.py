from pydantic import BaseModel

from scraper.models.domain import Domain
from scraper.models.website_data import WebsiteData
from scraper.models.screenshots import Screenshots

class ScrapingResult(BaseModel):
    website_data: WebsiteData
    screenshots: Screenshots = None

class ScrapingWebsiteRedirect(BaseModel):
    domain: Domain
    destination: str

