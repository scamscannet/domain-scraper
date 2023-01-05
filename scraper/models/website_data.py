import datetime

from pydantic import BaseModel

from scraper.models.code import Code
from scraper.models.domain import Domain
from scraper.models.links import Links
from scraper.models.node import Node
from scraper.models.server import Server


class WebsiteData(BaseModel):
    domain: Domain
    code: Code
    links: Links
    server: Server
    node: Node
    modules: dict = {}
    timestamp: str
