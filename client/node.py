import os

import httpx

from scraper.models.scraper.node import Node


def get_node(api, secret) -> Node:
    headers = {
        "X-NODE-SECRET": secret
    }
    r = httpx.get(url=api + '/nodes/dispatcher/me', headers=headers)
    r.raise_for_status()
    node_id = r.text.strip()
    ip = os.getenv("IP")

    if not ip:
        ip = httpx.get('https://myip.octobyte.workers.dev').text

    return Node(node_id=node_id, ip=ip)
