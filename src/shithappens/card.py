from dataclasses import dataclass, field

from matplotlib.figure import Figure


@dataclass
class Card:
    desc: str
    misery_index: float
    expansion_name: str
    fig_front: Figure = field(init=False)
    fig_back: Figure = field(init=False)
