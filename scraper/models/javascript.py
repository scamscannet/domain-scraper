from pydantic import BaseModel


class JavaScript(BaseModel):
    local: list = []  # local code
    internal: list = []  # local/internal links
    external: list = []  # extternal links
