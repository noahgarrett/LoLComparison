import bs4
from common import constants, singletons, league_sites
from scraping import scrape
import asyncio
import aiohttp
import time
from dotenv import load_dotenv
import os
from supabase import create_client, Client
from database import db


async def get_page(session: aiohttp.ClientSession, url: str, key: str) -> tuple[str, bytes]:
    async with session.get(url) as resp:
        text = await resp.read()
        return key, text


async def get_soup(key: str, text: bytes) -> None:
    soup: bs4.BeautifulSoup = bs4.BeautifulSoup(text.decode('utf-8'), 'lxml')

    singletons.OP_GG_OBJECT.soups.append(soup)


async def main(supabase_client: Client) -> None:
    # Make the requests and set the soups to the corresponding classes
    async with aiohttp.ClientSession() as session:

        tasks = []
        # Get the page data for NA-TOP-PlatPlus
        for key in constants.LOL_OP_GG_NA_PLAT_PLUS_URLS:
            url: str = constants.LOL_OP_GG_NA_PLAT_PLUS_URLS[key]
            tasks.append(asyncio.ensure_future(get_page(session, url, key)))

        pages = await asyncio.gather(*tasks)
        for page in pages:
            await get_soup(page[0], page[1])

    # Start the scrape logic
    await scrape.start()

    # Update the database
    await db.update_champions(supabase_client)


if __name__ == '__main__':
    start_time = time.time()

    # Load the .env file
    load_dotenv()

    # Set the Supabase connection
    supabase_url: str = os.getenv('SUPABASE_URL')
    supabase_key: str = os.getenv('SUPABASE_KEY')
    client: Client = create_client(supabase_url, supabase_key)

    # Set the event loop policy and run the main function async
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main(supabase_client=client))

    print("--- %s seconds ---" % (time.time() - start_time))
