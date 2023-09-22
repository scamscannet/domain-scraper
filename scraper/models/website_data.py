import datetime
from typing import Literal, Optional

from pydantic import BaseModel

from scraper.models.code import Code
from scraper.models.domain import Domain
from scraper.models.links import Links
from scraper.models.node import Node
from scraper.models.server import Server


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
