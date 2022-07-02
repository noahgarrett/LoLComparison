from dataclasses import dataclass


@dataclass
class ChampionStats:
    rank: int
    img: str
    name: str
    tier: int
    win_rate: float
    pick_rate: float
    ban_rate: float


@dataclass
class ChampionBuild:
    # Runes
    primary_tree: str
    primary_tree_img: str
    keystone: str
    keystone_img: str
    p_1: str
    p_1_img: str
    p_2: str
    p_2_img: str
    p_3: str
    p_3_img: str
    secondary_tree: str
    secondary_tree_img: str
    s_1: str
    s_1_img: str
    s_2: str
    s_2_img: str
    stat_1: str
    stat_1_img: str
    stat_2: str
    stat_2_img: str
    stat_3: str
    stat_3_img: str
    runes_pick_rate: float
    runes_win_rate: float
    runes_games: int

    # Starting Items
    starter_1: str
    starter_1_img: str
    starter_2: str
    starter_2_img: str
    starter_pick_rate: float
    starter_win_rate: float
    starter_games: int

    # Boots
    boots: str
    boots_img: str
    boots_pick_rate: float
    boots_win_rate: float
    boots_games: int

    # Highest pick-rate core build
    item_1: str
    item_1_img: str
    item_2: str
    item_2_img: str
    item_3: str
    item_3_img: str
    items_pick_rate: float
    items_win_rate: float
    items_games: int
