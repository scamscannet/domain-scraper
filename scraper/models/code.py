from pydantic import BaseModel

from scraper.models.javascript import JavaScript


class Code(BaseModel):
    title: str
    text: str
    html: str
    javascript: JavaScript
