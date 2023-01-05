from urllib.parse import urlparse

import tldextract
from pydantic import BaseModel


class Domain(BaseModel):
    subdomain: str = ""
    domain: str = None
    tld: str = None
    path: str = ""
    query: dict = {}
    fragment: str = ""
    parameters: list = []

    def to_url_without_protocol(self):
        url = ""

        if self.subdomain:
            url += self.subdomain + "."

        url += self.domain
        url += "." + self.tld

        if self.path:
            url += "/" + self.path

        if self.fragment:
            url += ";" + ";".join(self.parameters)

        if self.query.keys():
            url += "?" + '&'.join([f"{k}={v}" if v else k for k, v in self.query.items()])

        if self.fragment:
            url += "#" + self.fragment

        return url


def url_to_domain(url) -> Domain:
    domain_data = tldextract.extract(url)
    tld = domain_data.suffix
    domain = domain_data.domain
    subdomain = domain_data.subdomain
    url_data = urlparse(url)

    # parse query params
    query = {}
    for q in ([kv_pair for kv_pair in url_data.query.split("&")]):
        if not q:
            continue
        if "=" in q and len(q.split("=")) == 2:
            key, value = q.split("=")
            query[key] = value
        else:
            query[q] = ""

    # parse parameters
    parameters = [p for p in url_data.params.split(';') if p]

    return Domain(
        domain=domain,
        tld=tld,
        subdomain=subdomain,
        path=url_data.path[1:] if url_data.path and url_data.path[0] == "/" else url_data.path,
        query=query,
        fragment=url_data.fragment,
        parameters=parameters
    )