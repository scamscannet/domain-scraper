from pydantic import BaseModel

from scraper.models.scraper.javascript import JavaScript


class Code(BaseModel):
    title: str
    text: str
    categorised_text: dict
    html: str
    javascript: JavaScript
