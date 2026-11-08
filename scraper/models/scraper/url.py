from urllib.parse import urlparse, unquote

import tldextract
from pydantic import BaseModel


class Url(BaseModel):
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
            url += "/" + self.path if not self.path.startswith("/") else "" + self.path

        if self.parameters:
            url += ";" + ";".join(self.parameters)

        if self.query.keys():
            url += "?" + '&'.join([f"{k}={v}" if v else k for k, v in self.query.items()])

        if self.fragment:
            url += "#" + self.fragment

        return url

    @staticmethod
    def _normalize_path(path: str) -> str:
        """'' , '/', '/home/' and 'home' style paths all reduce to the same form ('' or 'home')."""
        return unquote(path or "").strip("/")

    def is_same_page(self, other: "Url", ignore_www: bool = True) -> bool:
        """Checks whether two Domains point to the same page, ignoring differences that don't count as a redirect:
        protocol (not stored on Url), letter case of the host, trailing/leading slashes, percent-encoding of the
        path, query parameter order and the fragment (#...), which never leaves the browser.

        a.tld == https://a.tld/ == A.TLD/#top, but a.tld != a.tld/home and a.tld != a.tld/?lang=en.
        With ignore_www (default), www.a.tld is treated as the same page as a.tld."""
        if other is None:
            return False

        def host(d: "Url") -> tuple[str, str, str]:
            subdomain = (d.subdomain or "").lower()
            if ignore_www and subdomain == "www":
                subdomain = ""
            return subdomain, (d.domain or "").lower(), (d.tld or "").lower()

        return (
            host(self) == host(other)
            and self._normalize_path(self.path) == self._normalize_path(other.path)
            and self.query == other.query
            and self.parameters == other.parameters
        )


def parse_url(url) -> Url:
    domain_data = tldextract.extract(url)
    tld = domain_data.suffix
    domain = domain_data.domain
    subdomain = domain_data.subdomain
    # Without a scheme urlparse treats the whole input ("a.com/home") as the path, so mark the host explicitly
    url_data = urlparse(url if "://" in url or url.startswith("//") else "//" + url)

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

    return Url(
        domain=domain,
        tld=tld,
        subdomain=subdomain,
        path=url_data.path[1:] if url_data.path and url_data.path[0] == "/" else url_data.path,
        query=query,
        fragment=url_data.fragment,
        parameters=parameters
    )