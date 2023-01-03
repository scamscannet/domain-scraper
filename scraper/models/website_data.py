import datetime

from pydantic import BaseModel

from scraper.models.code import Code
from scraper.models.links import Links
from scraper.models.node import Node
from scraper.models.server import Server




class WebsiteData(BaseModel):
    domain: str
    url: str
    code: Code
    links: Links
    server: Server
    node: Node
    modules: dict = {}
    timestamp: str
