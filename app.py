import asyncio
import aiohttp
import async_timeout
import time
from bs4 import BeautifulSoup
import requests


from utils.logger import logger

# from page.page_scraper import PageScraper


def get_webpage_info():
    """Input dialog for getting info on webpage, start_page and end_page to scrape.
    Returns:
        single_page: bool
        webpage: str
        start_page: int
        end_page: int
    """
    # mutliple pages check
    while True:
        single_page_input = input(
            "Do you want to scrape elements only from one page? [Y/n] "
        ).lower()
        if single_page_input == "y":
            single_page = True
            webpage = input("What website do you want to scrape? (enter whole url) ")
            start_page = 0
            end_page = 0
            break
        elif single_page_input == "n":
            single_page = False
            webpage = input(
                "What website do you want to scrape? Enter url of the webpage with numuerous elements you want to scrape usualy ending as '/p=' or '/page/' WITHOUT the last number): "
            )

            while True:
                try:
                    start_page = int(
                        input("From what page number you want to scrape? ")
                    )
                    end_page = int(
                        input(
                            "What is the number of the last page page you want to scrape elements from? "
                        )
                    )
                    break
                except TypeError:
                    print("Starting and ending page must be number!")
            break
        else:
            print("You must type Y for 'yes' or n for 'no'!")
    return single_page, webpage, start_page, end_page


def get_element_locator_interactive():
    elementLocator = input("Provide html tags as locator for 'a' tag of element: ")
    return elementLocator


def property_check_interactive():
    while True:
        property_check = input(
            "Will you need to scrape from the element a tag specific property? [Y/n] "
        ).lower()
        if property_check == "y":
            property = input("What property do you need? ")
            break
        elif property_check == "n":
            property = None
            break
        else:
            print("You must type Y for 'yes' or n for 'no'!")
    return property


def url_check(url):
    # Execute JavaScript to get the HTTP status code
    response = requests.get(url)
    http_status_code = response.status_code
    if http_status_code >= 200 and http_status_code < 300:
        logger.info(f"Request for {url} was successful")
        return True
    else:
        logger.error(
            f"Request failed with status code: {http_status_code}\n Make sure that that you have correct url address and website is working on your browser!"
        )
        return False


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
    # imports:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.chrome.service import Service as ChromeService

    import os

    os.chmod("chromedriver-linux64/chromedriver", 0o755)

    service = ChromeService(executable_path="chromedriver-linux64/chromedriver")

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(service=service, options=options)

    while True:
        # Basic page input
        single_page, webpage, start_page, end_page = get_webpage_info()
        # Preview check
        if single_page == True:
            url = webpage
        else:
            url = webpage + start_page
        if url_check(url):
            break

    with open("locators/pageLocator.py", "w") as file:
        file.write(
            f'class PageLocator:\n    SINGLE_PAGE = {single_page}\n    PAGE = "{webpage}"\n    START_PAGE = {start_page}\n    END_PAGE = {end_page}\n'
        )

    driver.get(url)

    # Getting elements and checking it
    while True:
        elementLocator = get_element_locator_interactive()

        elements = driver.find_elements(By.CSS_SELECTOR, elementLocator)
        if not elements:
            logger.error(
                "No elements were found based on this locator of the element. Try it again!"
            )
        else:
            logger.info(
                f"Elements were found! Example: {elements[0].get_attribute('outerHTML')}"
            )
            break

    # Getting property for extracting url link of element and checking it
    while True:
        url_property = property_check_interactive()
        if url_property:
            elementUrls = [element.get_attribute(url_property) for element in elements]
        else:
            elementUrls = elements

        if not elementUrls:
            logger.error(
                "Urls of the elements were not found! Check the element tags and where to find its url link and try again!"
            )
        else:
            break

    with open("locators/pageLocator.py", "a") as file:
        file.write(
            f'    ELEMENT = "{elementLocator}"\n    URL_PROPERTY = "{url_property}"\n'
        )

    logger.info("Following urls of elements were found:\n" + "\n".join(elementUrls))

    """
    elements = get_elements(url, start_page=0, end_page=5)
    for element in elements:
        print(element)
    """

    print("done")
    driver.quit()
