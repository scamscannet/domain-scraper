from pydantic import BaseModel


class Node(BaseModel):
    ip: str
    nodeid: str