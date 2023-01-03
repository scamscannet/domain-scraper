from scraper.models.node import Node

from dotenv import load_dotenv

load_dotenv()

class Config:
    API = "http://127.0.0.1:8000"

    NODE = Node(
        nodeid="test123",
        ip="127.0.0.1"
    )