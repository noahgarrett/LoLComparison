import bs4


# Dynamic Sites
class UDotGG:
    def __init__(self):
        self.name = "u.gg"


# Static Sites
class OPDotGG:
    def __init__(self, soups: list[bs4.BeautifulSoup], build_soups: list[bs4.BeautifulSoup]):
        self.name = "op.gg"
        self.soups = soups
        self.build_soups = build_soups
