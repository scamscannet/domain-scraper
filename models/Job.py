from pydantic import BaseModel

from scraper.models.scraper.url import Url


class Job(BaseModel):
    domain: Url
    id: str
