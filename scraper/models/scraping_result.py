from pydantic import BaseModel

from scraper.models.domain import Domain
from scraper.models.website_data import WebsiteData


class ScrapingResult(BaseModel):
    website_data: WebsiteData
    image_path: str = None

class ScrapingWebsiteRedirect(BaseModel):
    domain: Domain
    destination: str

