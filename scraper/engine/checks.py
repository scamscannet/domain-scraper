import asyncio
import socket
import httpx

from scraper.models.domain import Domain, url_to_domain
from config import Config

cfg = Config()


async def check_for_http_or_https_and_return_url(url: str) -> (bool, str, dict):
    """Checks whether a page uses a redirect. If the first value is True then the page is redirecting to the second
    string. If the bool is False then the second value represents the prefixed url """
    raw_url = url.replace("https://", "").replace("http://", "")
    orig_domain_obj = url_to_domain(raw_url)

    async with httpx.AsyncClient() as client:
        tasks = [
            client.get("https://" + raw_url, timeout=cfg.TIMEOUT),
            client.get("http://" + raw_url, timeout=cfg.TIMEOUT)
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)
    url, redirect, headers = None, False, {}
    for id, protocol in enumerate(('https://', 'http://')):
        response = results[id]
        if (isinstance(response, Exception)):
            continue

        if 200 <= response.status_code < 400:
            url = protocol + raw_url
        if response.status_code > 300:
            new_url = response.headers['Location']
            if new_url:
                new_domain_obj = url_to_domain(new_url)
                if new_domain_obj.domain == orig_domain_obj.domain and new_domain_obj.subdomain == orig_domain_obj.subdomain and orig_domain_obj.tld == new_domain_obj.tld:
                    # raise Exception("Redirecting to same Page. That won't work yet.")
                    pass
                else:
                    redirect = True
                    url = new_url
        if url:
            return redirect, url, headers
    raise Exception("Neither https nor http were accessible.")


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

async def get_ip_whois_and_domain_whois(ip: str, domain: str) -> (dict, dict):
    async with httpx.AsyncClient() as client:
        tasks = [
            client.get(f"https://whois.scamscan.net/whois/{domain}", timeout=cfg.TIMEOUT),
            client.get(f"https://whois.scamscan.net/ip-whois/{ip}", timeout=cfg.TIMEOUT)
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

    domain_whois = results[0].json() if results[0].status_code == 200 else {}
    ip_whois = results[1].json() if results[1].status_code == 200 else {}

    return domain_whois, ip_whois
