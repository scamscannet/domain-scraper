import os

from scraper.models.node import Node

from dotenv import load_dotenv

load_dotenv()

class Config:
    API = os.getenv("API")
    FIREFOX_PATH = os.getenv("FIREFOX_PATH")

    NODE = Node(
        nodeid="test123",
        ip="127.0.0.1"
    )