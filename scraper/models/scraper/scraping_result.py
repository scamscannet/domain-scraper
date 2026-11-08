from pydantic import BaseModel

from scraper.models.scraper.url import Url
from scraper.models.scraper.website_data import WebsiteData
from scraper.models.scraper.screenshots import Screenshots


class ScrapingResult(BaseModel):
    website_data: WebsiteData
    screenshots: Screenshots = None
    redirect_data: WebsiteData | None = None

    def to_dict_without_screenshots(self) -> dict:
        return {
            "website_data": self.website_data.dict(),
            "redirect_data": self.redirect_data.dict() if self.redirect_data else None,
        }

class RawScrapingResult(BaseModel):
    sourcecode: str
    screenshots: Screenshots
    har_bytes: bytes
    url: Url
    final_url: str  # page URL after redirects, with scheme; base for resolving relative links
