from pydantic import BaseModel


class Links(BaseModel):
    internal: list
    external: list
