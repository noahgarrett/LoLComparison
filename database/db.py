import supabase
from common import singletons
from scraping.objects import ChampionStats


async def update_champions(client: supabase.Client):
    # Update the database with current data for OP.GG Champions
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

            # Update the champion obj within the database
            client.table('champions').update(champ_obj)\
                .eq('name', champ_obj['name'])\
                .eq('location_id', champ_obj['location_id'])\
                .eq('position', champ_obj['position'])\
                .execute()

            # client.table('champions').insert(champ_obj).execute()


async def update_builds(client: supabase.Client):
    # Update the database with the current build data
    for build in singletons.OP_GG_BUILDS:
        build_obj = build.to_dict()
        data = client.table('builds').insert(build_obj).execute()
        if len(data.data) > 0:
            print(f'Added {build_obj["champ_id"]} to db')
