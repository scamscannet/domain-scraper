import asyncio
import socket
import httpx

from scraper.models.domain import Domain
from config import Config

cfg = Config()


async def check_for_http_or_https_and_return_url(url: str) -> (bool, str):
    """Checks whether a page uses a redirect. If the first value is True then the page is redirecting to the second
    string. If the bool is False then the second value represents the prefixed url """
    raw_url = url.replace("https://", "").replace("http://", "")
    async with httpx.AsyncClient() as client:
        tasks = [
            client.get("https://" + raw_url, timeout=cfg.TIMEOUT),
            client.get("http://" + raw_url, timeout=cfg.TIMEOUT)
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)
    if not isinstance(results[0], Exception) and 200 <= results[0].status_code < 400:
        if results[0].status_code < 300:
            return False, "https://" + raw_url
        else:
            return "https://" + raw_url not in results[0].headers['Location'], results[0].headers['Location']
    elif not isinstance(results[1], Exception) and 200 <= results[1].status_code < 300:
        if results[1].status_code < 300:
            return False, "http://" + raw_url
        else:
            return "http://" + raw_url not in results[1].headers['Location'], results[1].headers['Location']

    else:
        raise Exception("Unavailable")


def get_ip_for_website(domain: Domain):
    ping_domain = ""
    if domain.subdomain:
        ping_domain = domain.subdomain + "."

    ping_domain += domain.domain + "." + domain.tld
    try:
        ip = socket.gethostbyname(ping_domain)
        return ip
    except Exception:
        return ""
