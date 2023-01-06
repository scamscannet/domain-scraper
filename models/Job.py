from pydantic import BaseModel

from scraper.models.domain import Domain


class Job(BaseModel):
    domain: Domain
    id: str
