import asyncio
import aiohttp
import async_timeout
import time
from bs4 import BeautifulSoup
import requests


from utils.logger import logger

# from page.page_scraper import PageScraper


async def fetch_page(
    session, url, page
):  # This is coroutine function (it must be wraped to await)
    async with async_timeout.timeout(120):
        async with session.get(url) as response:  # fetches the url
            logger.info(f"Reading element data from page: << {page} >>")
            return await response.text()  # we must also await response


async def get_multiple_pages(loop, *urls):  # Main function
    async with aiohttp.ClientSession(
        loop=loop
    ) as session:  # creates a session in which loop will be executed
        tasks = [fetch_page(session, url, page) for url, page in urls]
        grouped_tasks = asyncio.gather(
            *tasks
        )  # gathers all fetch requests and calls them
        return await grouped_tasks


def get_elements(url, start_page: int, end_page: int):
    """Scrapes page content from start_page to end_page and creates Book objects"""
    logger.info(f'Loading elements from url: "{url}" pages "{start_page} - {end_page}"')

    urls = [(f"{url}{page}", page) for page in range(start_page, end_page)]

    loop = asyncio.get_event_loop()
    start_time = time.time()
    pages: list[str] = loop.run_until_complete(get_multiple_pages(loop, *urls))
    loading_time = time.time()
    logger.info(f"Pages loaded in {loading_time - start_time}")

    logger.debug("Reading elements data from loaded pages.")
    elements = []
    for page in pages:
        page_elements = PageScraper(page)
        elements.extend(page_elements.elements)

    logger.info(f"Elements read in {time.time() - loading_time}")
    return elements


if __name__ == "__main__":
    # Basic page input

    # mutliple pages check
    while True:
        single_page_input = input(
            "Do you want to scrape elements only from one page? (Y/n): "
        ).lower()
        if single_page_input == "y":
            url = input("What website do you want to scrape? ")
            end_page = 0
            break
        elif single_page_input == "n":
            url = input(
                "What website do you want to scrape? (It is the webpage with numuerous elements you want to scrape usualy ending as '/p=' or '/page/' without the last number): "
            )
            end_page = int(
                input("From how many pages do you want to scrape elements? ")
            )
            break
        else:
            print("You must type Y for 'yes' or n for 'no'!")

    with open("locators/pageLocator.py", "w") as file:
        file.write(f'class PageLocator:\n    PAGE = "{url}"\n')

    elementLocator = input("Provide html tags as locator for a tag of element: ")
    with open("locators/pageLocator.py", "a") as file:
        file.write(f'ELEMENT = "{elementLocator}"\n')

    # getting preview
    response = requests.get(url + "0" if end_page != 0 else url)
    page = BeautifulSoup(response.content, "html.parser")
    elementUrl = page.select(elementLocator)
    url = elementUrl[0]["href"]
    print(url)

    """
    elements = get_elements(url, start_page=0, end_page=5)
    for element in elements:
        print(element)
    """
