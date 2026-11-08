from typing import Literal, Optional

from pydantic import BaseModel

from scraper.models.scraper.url import Url
from scraper.models.scraper.node import Node


class WebsiteData(BaseModel):
    status: Literal["online", "offline", "error", "redirect"] = "online"
    url: Optional[Url] = None
    node: Node
    source_code: Optional[str] = None

    # Optional, only for redirects
    redirect_to: Optional[Url] = None
    modules: dict = {}
