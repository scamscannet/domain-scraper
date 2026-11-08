
class ScraperError(Exception):
    pass

class InternalError(ScraperError):
    """Internal Error when scraping. This can indicate a bug."""
    pass

class EngineErrorBase(ScraperError):
    """Engine error. Something with the scraping engine went wrong."""

class FailedScrape(ScraperError):
    """The scrape failed. Most likely this is due to http/https or the website being not reachable."""

class EngineError(EngineErrorBase):
    """An error that is due to the engine and does not indicate a page problem. This should not be treated as offline page"""
    pass

class WebsiteError(EngineErrorBase):
    "An error that is due to the website and indicates it's malfunctioning."
