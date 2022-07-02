import supabase
from common import singletons
from scraping.objects import ChampionStats


async def update_champions(client: supabase.Client):
    # Delete the current values within the database
    data = client.table('champions').delete().eq('location_id', 1).execute()

    # Add the current data to the database
    i = 0
    for key in singletons.OP_GG_CHAMPIONS:
        champ_list: list[ChampionStats] = singletons.OP_GG_CHAMPIONS[key]
        for champ in champ_list:
            champ_obj = {
                "rank": champ.rank,
                "img_url": champ.img,
                "name": champ.name,
                "tier": champ.tier,
                "win_rate": champ.win_rate,
                "pick_rate": champ.pick_rate,
                "ban_rate": champ.ban_rate,
                "location_id": 1,
                "position": key
            }

            data = client.table('champions').insert(champ_obj).execute()
            if not len(data.data) > 0:
                print(f"Failed to insert {champ_obj['name']}")
