from scraping.scrape import ChampionStats
from common.league_sites import OPDotGG

# Holds a list of class objects for league analytic sits
OP_GG_OBJECT: OPDotGG = OPDotGG(soups=[])

# Holds a list of OP.GG Champion Stat Objects
OP_GG_CHAMPIONS: dict = {
    'top': [],
    'jungle': [],
    'middle': [],
    'bottom': [],
    'support': []
}
