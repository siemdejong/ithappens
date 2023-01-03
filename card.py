from dataclasses import dataclass, field
from matplotlib.figure import Figure

@dataclass
class Card:
    desc: str
    misery_index: float
    fig: Figure  = field(init=False)