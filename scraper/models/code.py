from pydantic import BaseModel


class Code(BaseModel):
    title: str
    text: str
    html: str
    javascript: list
