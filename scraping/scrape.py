from common import singletons, helpers
from scraping.objects import ChampionStats


async def scrape_op_gg():
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


async def start():
    await scrape_op_gg()
