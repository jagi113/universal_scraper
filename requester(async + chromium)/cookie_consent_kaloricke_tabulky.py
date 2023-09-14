import asyncio
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from aiohttp import ClientSession, ClientResponse


async def click_agreement_button(driver: webdriver.Chrome):
    # Using appropriate Selenium code to locate and click the agreement button
    agreement_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Súhlas')]"))
    )
    agreement_button.click()
    await asyncio.sleep(2)  # Wait for the page to load after clicking agreement


async def cookie_consent_check(
    response: ClientResponse, session: ClientSession, url: str, headers: str, page: str
) -> ClientResponse:
    # Checking for cookie consent in Kalorické tabuľky
    if (
        "Kalorické Tabuľky vás žiada o súhlas s používaním vašich údajov na nasledujúce účely"
        in await response.text()
    ):
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run Chrome in headless mode
        driver = webdriver.Chrome(options=chrome_options)
        await click_agreement_button(driver)
        driver.get(url)  # Open the URL in Selenium WebDriver
        response = await session.get(url, headers=headers)

    return response, url, page
