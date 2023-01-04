import os
import uuid
import time
import httpx

from scraper.models.node import Node

from dotenv import load_dotenv

load_dotenv()


class Config:
    time = time.time()
    API = os.getenv("API")
    FIREFOX_PATH = os.getenv("FIREFOX_PATH")
    NODE = Node(
        nodeid=os.getenv("NODEID"),
        ip=os.getenv("IP") if os.getenv("IP") else httpx.get('https://api.ipify.org').text
    )
    TIMEOUT = int(os.getenv("TIMEOUT")) if os.getenv("TIMEOUT") else 25
    HEADLESS = os.getenv("HEADLESS", 'False').lower() in ('true', '1', 't', 'yes', 'y')