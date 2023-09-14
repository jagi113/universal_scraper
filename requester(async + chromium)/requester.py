import random
import asyncio
import aiohttp
import async_timeout
from utils.logger import logger
from aiohttp import ClientSession

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_5_8; en-US) AppleWebKit/534.1 (KHTML, like Gecko) Chrome/6.0.422.0 Safari/534.1",
    "Upgrade-Insecure-Requests": "1",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "DNT": "1",
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "it-IT,",
    "Cookie": "CONSENT=YES+cb.20210418-17-p0.it+FX+917; ",
}


async def fetch_page(
    session: ClientSession,
    url: str,
    page: str,
    click_func=None,
) -> tuple[str, str, str]:
    delay = random.uniform(2.0, 10.0)  # Add a random delay between 2.0 and 10.0 seconds
    logger.debug(f"Delaying for {delay:.2f} seconds before scraping page: << {page} >>")
    await asyncio.sleep(delay)

    async with async_timeout.timeout(120):
        async with session.get(url, headers=headers) as response:  # fetches the url
            logger.info(f"Scraping page: << {page} >>")

            if click_func is not None:
                response, url, page = await click_func(
                    response, session, url, headers, page
                )

            return (await response.text(), url, page)  # We must also await response


async def get_multiple_pages(
    loop: asyncio.AbstractEventLoop,
    urls: list[tuple[str, str]],
    click_func=None,
) -> list[tuple[str, str, str]]:
    connector = aiohttp.TCPConnector(
        force_close=True
    )  # for closing connection after request to avoid Server to disconnect

    async with aiohttp.ClientSession(
        loop=loop, connector=connector
    ) as session:  # creates a session in which loop will be executed
        tasks = [fetch_page(session, url, page, click_func) for url, page in urls]
        # print([(url, page) for url, page in urls])
        grouped_tasks = asyncio.gather(*tasks)
        return await grouped_tasks
