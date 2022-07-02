from scraping.objects import ChampionBuild
from common.league_sites import OPDotGG

# Holds a list of class objects for league analytic sits
OP_GG_OBJECT: OPDotGG = OPDotGG(soups=[], build_soups=[])

# Holds a list of OP.GG Champion Stat Objects
OP_GG_CHAMPIONS: dict = {
    'top': [],
    'jungle': [],
    'middle': [],
    'bottom': [],
    'support': []
}

OP_GG_BUILDS: list[ChampionBuild] = []
