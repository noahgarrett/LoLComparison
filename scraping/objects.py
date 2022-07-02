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
