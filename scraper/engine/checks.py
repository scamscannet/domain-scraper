import socket
import httpx

from scraper.models.scraper.url import Url, parse_url
from config import get_config
from log import logging


def check_for_http_or_https_and_return_url(url: str) -> (bool, str, dict):
    """Checks whether a page uses a redirect. If the first value is True then the page is redirecting to the second
    string. If the bool is False then the second value represents the prefixed url """
    raw_url = url.replace("https://", "").replace("http://", "")
    orig_domain_obj = parse_url(raw_url)

    results = []
    with httpx.Client() as client:
        for protocol in ('https://', 'http://'):
            try:
                results.append(client.get(protocol + raw_url, timeout=get_config().TIMEOUT))
            except Exception as e:
                results.append(e)
    url, redirect, headers = None, False, {}
    for id, protocol in enumerate(('https://', 'http://')):
        response = results[id]
        if isinstance(response, Exception):
            continue

        headers = response.headers

        if 200 <= response.status_code < 400:
            url = protocol + raw_url
        if response.status_code > 300:
            new_url = response.headers['Location']
            if new_url:
                new_domain_obj = parse_url(new_url)
                if new_domain_obj.domain == orig_domain_obj.domain and new_domain_obj.subdomain == orig_domain_obj.subdomain and orig_domain_obj.tld == new_domain_obj.tld:
                    # raise Exception("Redirecting to same Page. That won't work yet.")
                    pass
                else:
                    redirect = True
                    url = new_url
        if url:
            return redirect, url, headers
    raise Exception("Neither https nor http were accessible.")


def get_ip_for_website(domain: Url):
    ping_domain = ""
    if domain.subdomain:
        ping_domain = domain.subdomain + "."

    ping_domain += domain.domain + "." + domain.tld
    try:
        ip = socket.gethostbyname(ping_domain)
        return ip
    except Exception:
        return ""

def get_ip_whois_and_domain_whois(ip: str, domain: str) -> (dict, dict):
    results = []
    with httpx.Client() as client:
        for whois_url in (f"https://whois.scamscan.net/whois/{domain}", f"https://whois.scamscan.net/ip-whois/{ip}"):
            try:
                results.append(client.get(whois_url, timeout=get_config().TIMEOUT))
            except Exception as e:
                results.append(e)

    try:
        domain_whois = results[0].json() if results[0].status_code == 200 else {}
    except Exception as e:
        logging.warning(f"Error while parsing whois record: {e}")
        domain_whois = {}

    try:
        ip_whois = results[1].json() if results[1].status_code == 200 else {}
    except Exception as e:
        logging.warning(f"Error while parsing ip whois: {e}")
        ip_whois = {}

    return domain_whois, ip_whois
