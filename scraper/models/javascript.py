from pydantic import BaseModel


class JavaScript(BaseModel):
    local: list
    internal: list
    external: list
