from scraping.objects import ChampionStats
import operator


def sort_by_win_rate(champions: list[ChampionStats]) -> list[ChampionStats]:
    sorted_champs = sorted(champions, key=operator.attrgetter('win_rate'), reverse=True)
    return sorted_champs
