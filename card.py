from dataclasses import dataclass, field
from matplotlib.figure import Figure

@dataclass
class Card:
    desc: str
    misery_index: float
    expansion_name: str
    fig: Figure  = field(init=False)