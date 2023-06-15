from typing import Any

from pydantic import BaseModel

class Screenshots(BaseModel):
    full: bytes
    visible: bytes
