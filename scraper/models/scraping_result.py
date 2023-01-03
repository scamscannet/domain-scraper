from pydantic import BaseModel

from scraper.models.website_data import WebsiteData


class ScrapingResult(BaseModel):
    website_data: WebsiteData
    image_path: str
