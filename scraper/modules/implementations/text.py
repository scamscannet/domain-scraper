import copy
import re

from bs4 import BeautifulSoup

from scraper.models.scraper.scraping_result import RawScrapingResult
from scraper.models.scraper.url import Url
from scraper.modules.base_module import Module

# Never visible text, only code/markup
_NON_TEXT_TAGS = ["script", "style", "noscript", "template", "svg", "canvas", "iframe", "head"]

# Leaf-ish tags whose text is meaningful on its own. Containers like div/span/main/article are left out on purpose:
# their text is the text of everything inside them, so the old version stored the same text many times over.
_CATEGORIES = ["h1", "h2", "h3", "h4", "h5", "h6", "p", "li", "a", "button", "label", "td", "th", "blockquote"]

_WHITESPACE = re.compile(r"\s+")


def _clean(text: str) -> str:
    return _WHITESPACE.sub(" ", text).strip()


class ModuleImplementation(Module):
    """All visible text of the page.

    text: the whole page text, one line per block, whitespace collapsed.
    categorised_text: text per tag type (headings, paragraphs, list items, links, buttons, ...), duplicates removed."""
    name = "text"

    def check_if_eligible(self, url: Url) -> bool:
        return True

    def parse(self, url: Url, site_soup: BeautifulSoup, scrape: RawScrapingResult, **kwargs) -> dict:
        # Work on a copy: the soup is shared with the other modules, which still need <script>, <head> etc.
        soup = copy.copy(site_soup)
        for tag in soup.find_all(_NON_TEXT_TAGS):
            tag.decompose()

        lines = [_clean(line) for line in soup.get_text(separator="\n").split("\n")]
        text = "\n".join(line for line in lines if line)

        categorised = {}
        for tag_name in _CATEGORIES:
            texts = [_clean(tag.get_text(separator=" ")) for tag in soup.find_all(tag_name)]
            texts = list(dict.fromkeys(t for t in texts if t))
            if texts:
                categorised[tag_name] = texts

        return {
            "text": text,
            "categorised_text": categorised,
            "word_count": len(text.split()),
        }
