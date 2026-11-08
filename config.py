import os

from client.node import get_node
from functools import cache

from dotenv import load_dotenv

load_dotenv()






class Config:
    API = os.getenv("API")
    TIMEOUT = int(os.getenv("TIMEOUT")) if os.getenv("TIMEOUT") else 2500
    HEADLESS = os.getenv("HEADLESS", 'False').lower() in ('true', '1', 't', 'yes', 'y')
    TOKEN = os.getenv("TOKEN")
    DEVELOPMENT = os.getenv("DEVELOPMENT", 'False').lower() in ('true', '1', 't', 'yes', 'y')

    def __init__(self):
        if not os.getenv("API") or not os.getenv("TOKEN"):
            raise Exception("Please set environment variables")
        self.NODE = get_node(os.getenv("API"), os.getenv("TOKEN"))

    @staticmethod
    def check_env() -> bool:
        mandatory_params = ["API", "TOKEN"]
        for param in mandatory_params:
            if not os.getenv(param):
                return False
        return True

@cache
def get_config() -> Config:
    return Config()