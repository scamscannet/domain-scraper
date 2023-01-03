from pydantic import BaseModel


class Job(BaseModel):
    domain: str
    id: str
