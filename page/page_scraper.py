from bs4 import BeautifulSoup
from utils.logger import logger

from element.element import Element
from locators.pageLocator import PageLocator


class PageScraper:
    """It parses the page content. Provides as property 'books' - list of Book objects of the page. Second property 'page_count' is number of all available pages for scraping."""

    def __init__(self, page: str) -> BeautifulSoup:
        logger.debug("Parsing page content with BeautifulSoup HTML parser.")
        self.page = BeautifulSoup(page, "html.parser")

    @property
    def elements(self):
        locator = PageLocator.ELEMENT
        logger.debug(f"Finding all elements in the page using locator: `{locator}`.")
        books = [
            book
            for book in self.page.select(locator)
            if "listing-promo" not in book.attrs.get("class")
        ]
        return [Element(element) for element in elements]

    @property
    def page_count(self):
        logger.debug(f"Finding all number of catalogue pages available...")
        locator = PageLocator.PAGE_COUNT
        page_count = int(self.page.select_one(locator).text.strip())
        logger.debug(f"Found number of catalogue pages available: `{page_count}`")
        return page_count
