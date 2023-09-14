from fuzzywuzzy import process
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from aiohttp import ClientSession, ClientResponse

from utils.logger import logger

# from requester.cookie_consent_kaloricke_tabulky import click_agreement_button


import re
from unidecode import unidecode

import asyncio
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys


async def click_agreement_button(driver: webdriver.Chrome):
    agreement_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable(
            (
                By.XPATH,
                "//div[contains(@class, 'fc-footer-buttons')]//button//p[contains(text(), 'Súhlas')]",
            )
        )
    )
    agreement_button.click()
    logger.debug(f"Agreement button clicked!")
    await asyncio.sleep(2)


async def cookie_consent_check(
    response: str, driver: webdriver, url: str
) -> ClientResponse:
    # Checking for cookie consent in Kalorické tabuľky

    if (
        "Kalorické Tabuľky vás žiada o súhlas s používaním vašich údajov na nasledujúce účely"
        in response
    ):
        logger.debug(f"Found requested cookie consent on >>{url}<< !")
        await click_agreement_button(driver)
        driver.get(url)  # Open the URL in Selenium WebDriver
    return driver


async def search_for_ingredient_in_kaloricke_tabulky(
    response: ClientResponse,
    session: ClientSession,
    url: str,
    headers: str,
    ingredient: str,
) -> ClientResponse:
    # Initialize Selenium driver
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()), options=options
    )

    try:
        driver.get(url)
        response = driver.page_source
        driver = await cookie_consent_check(
            response.replace("&nbsp;", " ").replace("&#160;", " "), driver, url
        )

        # Find and enter search query
        input_element = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located(
                (By.CSS_SELECTOR, "input[placeholder='Hľadaj v názve potraviny']")
            )
        )

        input_element.send_keys(ingredient)

        # Wait for the page to load after submitting the search
        await asyncio.sleep(2)

        # Wait for search results to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "tr.p-table-bg-hover.md-row")
            )
        )

        # Extract and process search results
        results = driver.find_elements(By.CSS_SELECTOR, "tr.p-table-bg-hover.md-row")
        if results == None:
            logger.error(
                f"Ingredient '{ingredient}' was not found among kaloricke tabulky ingredients."
            )
            return None, None, None

        results_data = []
        for result in results:
            element_text_element = result.find_element(By.CSS_SELECTOR, "a.p-link")
            element_text = element_text_element.text
            results_data.append(element_text)
        logger.debug(
            f"Search results for ingredient >>{ingredient}<< are: {['-'+result+'- ' for result in results_data]}"
        )

        best_match, ratio = process.extractOne(ingredient, results_data)
        logger.info(
            f"Best match for ingredient '{ingredient}' is: >>{best_match}<< with ratio '{ratio}'"
        )
        slugified_best_match = unidecode(best_match)
        slugified_best_match = re.sub(r"\W+", "-", slugified_best_match.lower())
        slugified_best_match.strip("-")

        # Click on the best match option
        best_match_url = (
            "https://www.kaloricketabulky.sk/potraviny/" + slugified_best_match
        )

        new_response = await session.get(best_match_url, headers=headers)
        # driver.get(best_match_url)
        # response = driver.page_source
        print(best_match_url + " - " + slugified_best_match)
        logger.debug(
            f"Ingredient {ingredient} was found on kaloricke tabulky as {best_match}."
        )

        return new_response, best_match_url, slugified_best_match

    except Exception as e:
        print(e)

    finally:
        driver.close()
