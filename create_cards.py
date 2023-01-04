import pandas as pd
from pathlib import Path
from card import Card
from matplotlib.axes import Axes
import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from typing import Optional
from tqdm import tqdm
from utils import slugify


def parse_excel(input_path: Path, desc_col: int, misery_index_col: int):
    df = pd.read_excel(input_path, usecols=[desc_col, misery_index_col])
    return df


def plot_card(card: Card) -> Axes:

    # 128x89 cm for typical playing cards.
    x_total = 128  # cm front and back
    y_total = 89  # cm top to bottom

    # To be able to convert between centimeters and inches.
    cm_per_inch = 2.54

    # Add margin on all sides.
    margin = 0.5

    x_size = (x_total + margin) / cm_per_inch
    y_size = (y_total + margin) / cm_per_inch
    xy_size = (x_size, y_size)

    fig, ax = plt.subplots()

    fig.set_size_inches(xy_size)
    fig.set_facecolor("black")
    fig.subplots_adjust(left=0, bottom=0, right=1, top=1, wspace=None, hspace=None)

    ax.axis("off")

    text_kwargs = dict(
        wrap=True,
        weight="extra bold",
        horizontalalignment="center",
        fontfamily="Open Sans",
    )

    # Front.
    mi_desc = "misery index"

    ax.text(
        x_size / 4,
        0.8 * (y_size - margin) / 2,
        card.desc.upper(),
        **text_kwargs,
        color="yellow",
        fontsize=130,
        verticalalignment="top",
    )

    ax.text(
        x_size / 4,
        0.0 - 0.6 * (y_size - margin) / 2,
        mi_desc.upper(),
        **text_kwargs,
        color="yellow",
        fontsize=130,
        verticalalignment="center",
    )

    ax.text(
        x_size / 4,
        -0.9 * (y_size) / 2,
        str(card.misery_index).upper(),
        **text_kwargs,
        color="black",
        fontsize=230,
        verticalalignment="center",
    )

    mi_block = Rectangle(
        (x_size / 8, -1 * y_size / 2), 2 * x_size / 8, y_size / 8, fc="yellow",
    )
    ax.add_patch(mi_block)

    for pos, text in zip([0.8, -0.7, -0.8], [desc, mi_desc, mi]):
        ax.text(
            x_size / 4, pos * (y_size - margin) / 2, str(text).upper(), **text_kwargs,
        )

    ax.set_xlim(-x_size / 2, x_size / 2)
    ax.set_ylim(-y_size / 2, y_size / 2)

    plt.close(fig)

    return fig


def save_card(
    card: Card,
    output_path: Path,
    dpi: Optional[int] = 300,
    format: Optional[str] = ".pdf",
) -> None:
    fn = f"{card.misery_index}-{card.desc}"
    fn = slugify(fn)
    save_fn = (output_path / fn).with_suffix(format)

    card.fig.savefig(save_fn, format=save_fn.suffix[1:], pad_inches=0, dpi=dpi)


def create_cards(df: pd.DataFrame, output_path: Path):
    for i, row in tqdm(df.iterrows(), total=df.shape[0]):
        card = Card(row["desc"], row["misery_index"])
        card.fig = plot_card(card)
        save_card(card, output_path)


df = parse_excel("lol.xlsx", 0, 1)

create_cards(df, Path("outputs"))

