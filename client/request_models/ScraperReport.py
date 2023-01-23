from typing import Literal

from pydantic import BaseModel


class ScraperReport(BaseModel):
    type: Literal["unreachable", "issue", "redirect"] = "unreachable"
    payload: dict = {}
    jobid: str = ""
    nodeid: str = ""
