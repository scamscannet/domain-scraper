from pydantic import BaseModel


class Node(BaseModel):
    ip: str
    node_id: str