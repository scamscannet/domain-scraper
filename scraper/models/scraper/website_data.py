from typing import Literal, Optional

from pydantic import BaseModel

from scraper.models.scraper.code import Code
from scraper.models.scraper.domain import Domain
from scraper.models.scraper.links import Links
from scraper.models.scraper.node import Node
from scraper.models.scraper.server import Server


class WebsiteData(BaseModel):
    status: Literal["online", "offline", "error", "redirect"] = "online"
    domain: Optional[Domain]
    code: Optional[Code]
    links: Optional[Links]
    server: Optional[Server]
    node: Optional[Node]
    redirect: Optional[Domain]
    headers: Optional[dict]

    whois: Optional[dict]

    modules: dict = {}
