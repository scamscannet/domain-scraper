from pydantic import BaseModel

from scraper.models.scraper.domain import Domain


class Job(BaseModel):
    domain: Domain
    id: str
