import bs4
from common import singletons, helpers
from scraping.objects import ChampionStats, ChampionBuild
import supabase
import aiohttp
import asyncio
import time


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
        i = 0
        for champ in champions:
            formatted_name = champ['name'].lower().replace(' ', '').replace("'", "").replace(".", "")

            if formatted_name == 'wukong':
                formatted_name = 'monkeyking'
            elif formatted_name == 'nunu&willump':
                formatted_name = 'nunu'

            if champ['position'] == 'middle':
                champ['position'] = 'mid'
            elif champ['position'] == 'bottom':
                champ['position'] == 'adc'

            url: str = f"https://na.op.gg/champions/{formatted_name}/{champ['position']}/build?region=na&tier" \
                       f"=platinum_plus"
            tasks.append(asyncio.ensure_future(get_build_page(session, url)))

            i += 1
            if i == 10:
                i = 0
                print("Sleeping 1 second to avoid the 429 monster")
                time.sleep(1)

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
        champ_name = soup.find('div', {'class': 'info-box'}).find('span', {'class': 'name'}).text
        champ_pos = soup.find('span', {'class': 'build-position'}).text.split()[2].lower()
        champion = client.table('champions').select("*") \
            .eq('name', champ_name) \
            .eq('position', champ_pos) \
            .execute().data[0]

        # region Primary Rune Tree
        primary_rune_tree = soup.find('div', {'class': 'css-1nomhew e1o8f102'})

        primary_tree_name = primary_rune_tree.find('h5').text
        primary_tree_img = primary_rune_tree.find('img').attrs['src']

        primary_rows: list = primary_rune_tree.findAll('div', {'class': 'row'})

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
        # endregion

        # region Secondary Rune Tree
        secondary_rune_tree = soup.findAll('div', {'class': 'css-1nomhew e1o8f102'})[1]

        secondary_tree_name = secondary_rune_tree.find('h5').text
        secondary_tree_img = secondary_rune_tree.find('img').attrs['src']

        secondary_rows: list = secondary_rune_tree.findAll('div', {'class': 'row'})

        secondary_1_items: list = secondary_rows[1].findAll('div', {'class': 'item'})
        s_1_name = None
        s_1_img = None
        for item in secondary_1_items:
            img_url = item.find('img')
            if not len(img_url.attrs['src'].split('grayscale')) > 1:
                s_1_img = img_url.attrs['src']
                s_1_name = img_url.attrs['alt']
                break

        secondary_2_items: list = secondary_rows[2].findAll('div', {'class': 'item'})
        s_2_name = None
        s_2_img = None
        for item in secondary_2_items:
            img_url = item.find('img')
            if not len(img_url.attrs['src'].split('grayscale')) > 1:
                if s_1_name is None or s_1_img is None:
                    s_1_img = img_url.attrs['src']
                    s_1_name = img_url.attrs['alt']
                else:
                    s_2_img = img_url.attrs['src']
                    s_2_name = img_url.attrs['alt']
                break

        secondary_3_items: list = secondary_rows[3].findAll('div', {'class': 'item'})
        for item in secondary_3_items:
            img_url = item.find('img')
            if not len(img_url.attrs['src'].split('grayscale')) > 1:
                if s_1_name is None or s_1_img is None:
                    s_1_img = img_url.attrs['src']
                    s_1_name = img_url.attrs['alt']
                else:
                    s_2_img = img_url.attrs['src']
                    s_2_name = img_url.attrs['alt']
                break
        # endregion

        # region 3 Minor stat selection
        stat_tree = soup.find('div', {'class': 'css-1ooi192 e1gtrici3'})

        stat_rows = stat_tree.findAll('div', {'class': 'row'})

        stat_1_items = stat_rows[0].findAll('div')
        stat_1_name = ""
        stat_1_img = ""
        for item in stat_1_items:
            img_url = item.find('img')
            if not len(img_url.attrs['src'].split('grayscale')) > 1:
                stat_1_img = img_url.attrs['src']
                stat_1_name = img_url.attrs['alt']

        stat_2_items = stat_rows[1].findAll('div')
        stat_2_name = ""
        stat_2_img = ""
        for item in stat_2_items:
            img_url = item.find('img')
            if not len(img_url.attrs['src'].split('grayscale')) > 1:
                stat_2_img = img_url.attrs['src']
                stat_2_name = img_url.attrs['alt']

        stat_3_items = stat_rows[2].findAll('div')
        stat_3_name = ""
        stat_3_img = ""
        for item in stat_3_items:
            img_url = item.find('img')
            if not len(img_url.attrs['src'].split('grayscale')) > 1:
                stat_3_img = img_url.attrs['src']
                stat_3_name = img_url.attrs['alt']
        # endregion

        # region Runes Pick/Win rate
        rune_data = soup.find('div', {'class': 'css-zyi49u e1jxk9el3'}).findAll('li')[0]

        runes_pick_rate = rune_data.find('span', {'class': 'pick-rate'}).text.split("%")[0]
        runes_games = rune_data.find('span', {'class': 'pick-rate'}).text.split("%")[1].replace('  Games', '').replace(',', '')
        runes_win_rate = rune_data.find('span', {'class': 'win-rate'}).text.replace('%', '')
        # endregion

        # region Starter Items
        starter_table_row = soup.find('div', {'class': 'css-11msl8b e1f5dr6w2'}).find('table').find('tbody').findAll('tr')[0]

        starter_1_name = starter_table_row.findAll('img')[0].attrs['alt']
        starter_1_img = starter_table_row.findAll('img')[0].attrs['src']

        try:
            starter_2_name = starter_table_row.findAll('img')[1].attrs['alt']
            starter_2_img = starter_table_row.findAll('img')[1].attrs['src']
        except:
            starter_2_name = ""
            starter_2_img = ""

        starter_pick_rate = starter_table_row.findAll('td')[1].find('strong').text.replace('%', '')
        starter_games = starter_table_row.findAll('td')[1].find('small').text.replace(' Games', '').replace(',', '')
        starter_win_rate = starter_table_row.findAll('td')[2].text.replace('%', '')
        # endregion

        # region Boots
        if champ_name == "Cassiopeia":
            boots_name = ""
            boots_img = ""
            boots_pick_rate = 0
            boots_win_rate = 0
            boots_games = 0
        else:
            boots_table_row = soup.find('div', {'class': 'css-11msl8b e1f5dr6w2'}).findAll('table')[1].find('tbody').findAll('tr')[0]

            boots_name = boots_table_row.find('img').attrs['alt']
            boots_img = boots_table_row.find('img').attrs['src']

            boots_pick_rate = boots_table_row.findAll('td')[1].find('strong').text.replace('%', '')
            boots_games = boots_table_row.findAll('td')[1].find('small').text.replace(' Games', '').replace(',', '')
            boots_win_rate = boots_table_row.findAll('td')[2].text.replace('%', '')
        # endregion

        # region Core Build
        core_table_body = soup.find('div', {'class': 'css-kygzsj e1f5dr6w1'}).find('table').find('tbody')

        core_table_row = core_table_body.findAll('tr')[0]

        item_1_name = core_table_row.findAll('img')[0].attrs['alt']
        item_1_img = core_table_row.findAll('img')[0].attrs['src']

        item_2_name = core_table_row.findAll('img')[1].attrs['alt']
        item_2_img = core_table_row.findAll('img')[1].attrs['src']

        item_3_name = core_table_row.findAll('img')[2].attrs['alt']
        item_3_img = core_table_row.findAll('img')[2].attrs['src']

        items_pick_rate = core_table_row.findAll('td')[1].find('strong').text.replace('%', '')
        items_games = core_table_row.findAll('td')[1].find('small').text.replace(' Games', '').replace(',', '')
        items_win_rate = core_table_row.findAll('td')[2].find('strong').text.replace('%', '')
        # endregion

        # region Create and Append ChampionBuild Object
        champ_build: ChampionBuild = ChampionBuild(
            champ_id=champion['id'],
            location_id=champion['location_id'],
            primary_tree=primary_tree_name,
            primary_tree_img=primary_tree_img,
            keystone=keystone_name,
            keystone_img=keystone_img,
            p_1=p_1_name,
            p_1_img=p_1_img,
            p_2=p_2_name,
            p_2_img=p_2_img,
            p_3=p_3_name,
            p_3_img=p_3_img,
            secondary_tree=secondary_tree_name,
            secondary_tree_img=secondary_tree_img,
            s_1=s_1_name,
            s_1_img=s_1_img,
            s_2=s_2_name,
            s_2_img=s_2_img,
            stat_1=stat_1_name,
            stat_1_img=stat_1_img,
            stat_2=stat_2_name,
            stat_2_img=stat_2_img,
            stat_3=stat_3_name,
            stat_3_img=stat_3_img,
            runes_pick_rate=float(runes_pick_rate),
            runes_win_rate=float(runes_win_rate),
            runes_games=int(runes_games),
            starter_1=starter_1_name,
            starter_1_img=starter_1_img,
            starter_2=starter_2_name,
            starter_2_img=starter_2_img,
            starter_pick_rate=float(starter_pick_rate),
            starter_win_rate=float(starter_win_rate),
            starter_games=int(starter_games),
            boots=boots_name,
            boots_img=boots_img,
            boots_pick_rate=float(boots_pick_rate),
            boots_win_rate=float(boots_win_rate),
            boots_games=int(boots_games),
            item_1=item_1_name,
            item_1_img=item_1_img,
            item_2=item_2_name,
            item_2_img=item_2_img,
            item_3=item_3_name,
            item_3_img=item_3_img,
            items_pick_rate=float(items_pick_rate),
            items_win_rate=float(items_win_rate),
            items_games=int(items_games)
        )

        singletons.OP_GG_BUILDS.append(champ_build)
        print(f"Appended {champion['name']}'s build at {champion['position']}")
        # endregion

