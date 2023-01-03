from pydantic import BaseModel


class Server(BaseModel):
    ip: str