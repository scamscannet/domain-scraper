from scraper.models.domain import url_to_domain
from scraper.modules.implementations.google import ModuleImplementation

impl = ModuleImplementation()
tlds_to_test = ["de", "com", "fr", "ca", "ae"]
urls_to_test = {
    "google.de": False,
    "google.com": False,
    "www.google.ae": False,
    "https://google.com": False,
    "https://www.google.ae/search?q=wwd&ei=YTLIY-GpM9eB9u8PnYWk2AU&ved=0ahUKEwih3pWW2NH8AhXXgP0HHZ0CCVsQ4dUDCBk&uact=5&oq=wwd&gs_lcp=Cgxnd3Mtd2l6LXNlcnAQAzIKCAAQsQMQgwEQQzIECAAQQzILCAAQgAQQsQMQgwEyBQguEIAEMgUIABCABDILCC4QgAQQxwEQrwEyBQgAEIAEMgQIABBDMgQIABBDMgUIABCABDoOCAAQgAQQsQMQgwEQsAM6DQgAELEDEIMBELADEEM6BwgAELADEEM6BwguELADEEM6CAgAEIAEELADOgoIABCxAxCwAxBDOg0IABDkAhDWBBCwAxgBOhAILhCABBCxAxDIAxCwAxgCOg8ILhDUAhDIAxCwAxBDGAI6EwguELEDEIMBEMcBENEDENQCEEM6DQguELEDEIMBENQCEEM6CAguELEDEIMBOggIABCxAxCDAToOCC4QgAQQxwEQrwEQ1AJKBAhBGAFKBAhGGAFQwAZYkgdg0wpoAXAAeACAAU6IAZABkgEBMpgBAKABAcgBEcABAdoBBggBEAEYCdoBBggCEAEYCA&sclient=gws-wiz-serp": True,
    "https://www.google.com/search?q=hello": True,
}


def test_tld_loading():
    loaded_tlds = impl.tlds
    assert any([x in loaded_tlds for x in tlds_to_test])

def test_implementation_eligibty():
    for url, result in urls_to_test.items():
        furl = url_to_domain(url)
        assert result == impl.check_if_eligible(furl)