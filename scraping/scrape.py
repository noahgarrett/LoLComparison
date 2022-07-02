import bs4
from common import singletons, helpers
from scraping.objects import ChampionStats
import supabase
import aiohttp
import asyncio


async def scrape_op_gg_champions():
    soups = singletons.OP_GG_OBJECT.soups

    i = 0
    for soup in soups:
        tbody = soup.tbody
        rows = tbody.contents

        # Iterate through the list of champions on the table.
        # Initialize a ChampionStats object, add it to a list
        # and sort the list by win_rate.
        champs: list = []
        for j in range(len(rows)):
            champ_row = rows[j].findAll('td')

            rank = champ_row[0].find('span').text
            img = champ_row[1].find('a').find('img').attrs['src']
            name = champ_row[1].find('a').text
            tier = champ_row[2].text
            win_rate = champ_row[3].text.replace("%", "")
            pick_rate = champ_row[4].text.replace("%", "")
            ban_rate = champ_row[5].text.replace("%", "")

            champion = ChampionStats(
                rank=int(rank),
                img=img,
                name=name,
                tier=int(tier),
                win_rate=float(win_rate),
                pick_rate=float(pick_rate),
                ban_rate=float(ban_rate)
            )

            champs.append(champion)

        # Set the singleton to the sorted value
        if i == 0:
            singletons.OP_GG_CHAMPIONS['top'] = helpers.sort_by_win_rate(champs)
        elif i == 1:
            singletons.OP_GG_CHAMPIONS['jungle'] = helpers.sort_by_win_rate(champs)
        elif i == 2:
            singletons.OP_GG_CHAMPIONS['middle'] = helpers.sort_by_win_rate(champs)
        elif i == 3:
            singletons.OP_GG_CHAMPIONS['bottom'] = helpers.sort_by_win_rate(champs)
        elif i == 4:
            singletons.OP_GG_CHAMPIONS['support'] = helpers.sort_by_win_rate(champs)
        i += 1


async def get_build_soup(text: bytes):
    soup: bs4.BeautifulSoup = bs4.BeautifulSoup(text.decode('utf-8'), 'lxml')
    singletons.OP_GG_OBJECT.build_soups.append(soup)


async def get_build_page(session: aiohttp.ClientSession, url: str):
    async with session.get(url) as resp:
        text = await resp.read()
        return text


async def generate_soups(champions: list):
    async with aiohttp.ClientSession() as session:
        tasks: list = []
        for champ in champions:
            formatted_name = champ['name'].lower().replace(' ', '').replace("'", "")
            url: str = f"https://na.op.gg/champions/{formatted_name}/{champ['position']}/build?region=na&tier" \
                       f"=platinum_plus"
            tasks.append(asyncio.ensure_future(get_build_page(session, url)))
            break  # REMOVE THIS

        pages = await asyncio.gather(*tasks)
        for page in pages:
            await get_build_soup(page)


async def scrape_op_gg_builds(client: supabase.Client):
    # Get the list of champion objects in the database
    champions = client.table('champions').select("*").execute().data

    # Generate all the soups for parsing
    await generate_soups(champions)

    # Get all the soups from the OP.GG Class
    soups: list[bs4.BeautifulSoup] = singletons.OP_GG_OBJECT.build_soups

    for soup in soups:
        champ_name = soup.find('span', {'class': 'name'}).text
        champ_pos = soup.find('span', {'class': 'build-position'}).text.split()[2].lower()
        champion = client.table('champions').select("*") \
            .eq('name', champ_name) \
            .eq('position', champ_pos) \
            .execute().data

        # region Runes
        rune_tree = soup.find('div', {'class': 'css-1nomhew e1o8f102'})

        primary_tree_name = rune_tree.find('h5').text
        primary_tree_img = rune_tree.find('img').attrs['src']

        primary_rows: list = rune_tree.findAll('div', {'class': 'row'})

        keystone_items: list = primary_rows[1].findAll('div', {'class': 'item'})
        keystone_name = ""
        keystone_img = ""
        for item in keystone_items:
            img_url = item.find('img')
            if not len(img_url.attrs['src'].split('grayscale')) > 1:
                keystone_img = img_url.attrs['src']
                keystone_name = img_url.attrs['alt']
                break

        perk_1_items: list = primary_rows[2].findAll('div', {'class': 'item'})
        p_1_name = ""
        p_1_img = ""
        for item in perk_1_items:
            img_url = item.find('img')
            if not len(img_url.attrs['src'].split('grayscale')) > 1:
                p_1_img = img_url.attrs['src']
                p_1_name = img_url.attrs['alt']
                break

        perk_2_items: list = primary_rows[3].findAll('div', {'class': 'item'})
        p_2_name = ""
        p_2_img = ""
        for item in perk_2_items:
            img_url = item.find('img')
            if not len(img_url.attrs['src'].split('grayscale')) > 1:
                p_2_img = img_url.attrs['src']
                p_2_name = img_url.attrs['alt']
                break

        perk_3_items: list = primary_rows[4].findAll('div', {'class': 'item'})
        p_3_name = ""
        p_3_img = ""
        for item in perk_3_items:
            img_url = item.find('img')
            if not len(img_url.attrs['src'].split('grayscale')) > 1:
                p_3_img = img_url.attrs['src']
                p_3_name = img_url.attrs['alt']
                break

        print(p_3_name, p_3_img)
        # endregion
        break
