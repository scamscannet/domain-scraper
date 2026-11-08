import base64
import codecs
import json

import mmh3
from bs4 import BeautifulSoup

from scraper.models.scraper.scraping_result import RawScrapingResult
from scraper.models.scraper.screenshots import Screenshots
from scraper.models.scraper.url import parse_url
from scraper.modules.implementations import javascript, metadata, text

ICON_BYTES = b"\x89PNG\r\n\x1a\nfake-icon"
ICON_DATA_URI = "data:image/png;base64," + base64.b64encode(ICON_BYTES).decode()

HTML = f"""<!doctype html>
<html lang="de">
<head>
  <meta charset="utf-8">
  <title>  Shop   Example </title>
  <meta name="description" content="Best   deals">
  <meta name="robots" content="noindex, noai">
  <meta property="og:title" content="OG Shop">
  <meta property="og:description" content="OG deals">
  <meta name="twitter:card" content="summary">
  <meta name="google-site-verification" content="abc123">
  <link rel="canonical" href="/home/">
  <link rel="alternate" hreflang="en" href="https://shop.example.com/en/">
  <link rel="icon" href="{ICON_DATA_URI}">
  <link rel="apple-touch-icon" href="/apple.png">
  <link rel="manifest" href="/site.webmanifest">
  <link rel="modulepreload" href="/assets/app.mjs">
  <link rel="preload" as="script" href="https://cdn.other.net/lib.js">
  <link rel="preload" as="style" href="/style.css">
  <script src="/static/main.js"></script>
  <script src="vendor/jquery.js"></script>
  <script src="//www.googletagmanager.com/gtm.js?id=GTM-1"></script>
  <script src="https://cdn.example.com/bundle.js"></script>
  <script src="/static/main.js"></script>
  <script>var tracking = "do not keep me";</script>
  <script type="application/ld+json">{{"@type": "Organization", "name": "Shop GmbH"}}</script>
  <style>.x {{ color: red }}</style>
</head>
<body>
  <h1>Welcome   to the shop</h1>
  <div><p>First <b>paragraph</b>.</p><p>First <b>paragraph</b>.</p></div>
  <ul><li>Item one</li><li>Item two</li></ul>
  <a href="/login">Log in</a>
  <noscript>Enable JS</noscript>
</body>
</html>"""

HAR = {"log": {"entries": [
    {"request": {"url": "https://shop.example.com/static/main.js"},
     "response": {"content": {"mimeType": "application/javascript"}}},
    {"request": {"url": "https://shop.example.com/chunk-42"},  # dynamic import() without .js extension
     "response": {"content": {"mimeType": "text/javascript; charset=utf-8"}}},
    {"request": {"url": "https://tracker.evil.io/t.js"}, "response": {"content": {"mimeType": ""}}},
    {"request": {"url": "https://shop.example.com/style.css"}, "response": {"content": {"mimeType": "text/css"}}},
]}}

FINAL_URL = "https://shop.example.com/de/index.html"


def _scrape() -> RawScrapingResult:
    return RawScrapingResult(
        sourcecode=HTML,
        screenshots=Screenshots(full=b"", visible=b""),
        har_bytes=json.dumps(HAR).encode(),
        url=parse_url(FINAL_URL),
        final_url=FINAL_URL,
    )


def _run(module):
    scrape = _scrape()
    soup = BeautifulSoup(scrape.sourcecode, "html.parser")
    result = module.ModuleImplementation().parse(scrape.url, soup, scrape)
    json.dumps(result)  # has to be uploadable
    return result, soup


def test_javascript_collects_script_urls_only():
    result, _ = _run(javascript)

    assert result["internal"] == [
        "https://shop.example.com/static/main.js",
        "https://shop.example.com/de/vendor/jquery.js",  # relative to the page's directory
        "https://cdn.example.com/bundle.js",  # other subdomain, same site
        "https://shop.example.com/assets/app.mjs",
        "https://shop.example.com/chunk-42",  # only known from the HAR
    ]
    assert result["external"] == [
        "https://www.googletagmanager.com/gtm.js?id=GTM-1",  # protocol-relative takes the page's https
        "https://cdn.other.net/lib.js",
        "https://tracker.evil.io/t.js",
    ]
    assert result["inline_count"] == 2  # the inline script and the JSON-LD block
    assert "do not keep me" not in json.dumps(result)


def test_text_is_visible_text_only():
    result, soup = _run(text)

    assert result["text"].splitlines()[0] == "Welcome to the shop"
    for hidden in ("do not keep me", "color: red", "Enable JS", "Shop Example", "Shop GmbH"):
        assert hidden not in result["text"]
    assert result["categorised_text"]["h1"] == ["Welcome to the shop"]
    assert result["categorised_text"]["p"] == ["First paragraph ."]  # duplicate removed
    assert result["categorised_text"]["li"] == ["Item one", "Item two"]
    assert result["categorised_text"]["a"] == ["Log in"]
    assert "div" not in result["categorised_text"]
    # The shared soup must be untouched for the other modules
    assert soup.find("script") is not None and soup.find("head") is not None


def test_metadata_fields():
    result, _ = _run(metadata)

    assert result["title"] == "Shop Example"
    assert result["description"] == "Best deals"
    assert result["og_description"] == "OG deals"
    assert result["robots"] == "noindex, noai"
    assert result["canonical"] == "https://shop.example.com/home/"
    assert result["language"] == "de"
    assert result["charset"] == "utf-8"
    assert result["open_graph"] == {"og:title": "OG Shop", "og:description": "OG deals"}
    assert result["twitter"] == {"twitter:card": "summary"}
    assert result["alternates"] == {"en": "https://shop.example.com/en/"}
    assert result["manifest"] == "https://shop.example.com/site.webmanifest"
    assert [i["rel"] for i in result["icons"]] == ["icon", "apple-touch-icon"]
    assert result["structured_data"] == [{"@type": "Organization", "name": "Shop GmbH"}]
    assert result["meta"]["google-site-verification"] == "abc123"


def test_metadata_favicon_hash_is_shodan_compatible():
    result, _ = _run(metadata)

    assert result["favicon"]["url"] == "data:"
    assert result["favicon"]["mmh3"] == mmh3.hash(codecs.encode(ICON_BYTES, "base64"))
    assert len(result["favicon"]["sha256"]) == 64
