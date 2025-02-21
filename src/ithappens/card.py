from dataclasses import dataclass, field
from pathlib import Path

from matplotlib.figure import Figure


@dataclass
class Card:
    desc: str
    misery_index: float
    expansion_name: str
    image_path: Path | None
    fig_front: Figure = field(init=False)
    fig_back: Figure = field(init=False)
    front_save_fn: Path = field(init=False)
    back_save_fn: Path = field(init=False)
    misery_index_desc: str = "misery index"
