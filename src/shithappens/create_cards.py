import argparse
import textwrap
from glob import glob
from pathlib import Path
from typing import Literal, Optional, Union

import matplotlib.image as mpimage
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.offsetbox import AnchoredOffsetbox, AnchoredText, TextArea
from matplotlib.patches import BoxStyle, Rectangle
from matplotlib.path import Path as mpPath
from matplotlib.text import Annotation, Text
from matplotlib.transforms import Bbox, Transform
try:
    from tqdm import tqdm
except ImportError:
    print("Install tqdm to add a progress bar.")
    def tqdm(iterable, *args, **kwargs):
        del args, kwargs
        return iterable

from .card import Card
from .utils import merge_pdfs, slugify


def text_with_wrap_autofit(
    ax: plt.Axes,
    txt: str,
    xy: tuple[float, float],
    width: float,
    height: float,
    *,
    min_font_size=None,
    transform: Optional[Transform] = None,
    ha: Literal["left", "center", "right"] = "center",
    va: Literal["bottom", "center", "top"] = "center",
    show_rect: bool = False,
    **kwargs,
):
    """Automatically fits the text to some axes"""
    if transform is None:
        transform = ax.transData

    #  Different alignments give different bottom left and top right anchors.
    x, y = xy
    xa0, xa1 = {
        "center": (x - width / 2, x + width / 2),
        "left": (x, x + width),
        "right": (x - width, x),
    }[ha]
    ya0, ya1 = {
        "center": (y - height / 2, y + height / 2),
        "bottom": (y, y + height),
        "top": (y - height, y),
    }[va]
    a0 = xa0, ya0
    a1 = xa1, ya1

    x0, y0 = transform.transform(a0)
    x1, y1 = transform.transform(a1)
    # rectangle region size to constrain the text in pixel
    rect_width = x1 - x0
    rect_height = y1 - y0

    fig: Figure = ax.get_figure()
    dpi = fig.dpi
    rect_height_inch = rect_height / dpi

    # Initial fontsize according to the height of boxes
    fontsize = rect_height_inch * 72

    wrap_lines = 1
    while True:
        wrapped_txt = "\n".join(textwrap.wrap(txt, width=len(txt) // wrap_lines))
        text: Annotation = ax.annotate(
            wrapped_txt, xy, ha=ha, va=va, xycoords=transform, **kwargs
        )
        text.set_fontsize(fontsize)

        # Adjust the fontsize according to the box size.
        bbox: Bbox = text.get_window_extent()
        adjusted_size = fontsize * rect_width / bbox.width
        if min_font_size is None or adjusted_size >= min_font_size:
            break
        text.remove()
        wrap_lines += 1
    text.set_fontsize(adjusted_size)

    if show_rect:
        rect = Rectangle(a0, width, height, fill=False, ls="--")
        ax.add_patch(rect)

    return text


class ShitHappensArgs(argparse.Namespace):
    input_dir: str
    name: str
    merge: bool
    side: Literal["front", "back", "both"]


def parse_excel(input_path: Path, desc_col: int, misery_index_col: int) -> pd.DataFrame:
    """Parse an Excel file.
    It must have two colums: descriptions along with their misery index.

    Args:
        intput_path: path of the Excel file
        desc_col: description column index
        misery_index_col: misery index column index

    Returns:
        Pandas DataFrame with index, description, and misery index.
    """
    df = pd.read_excel(input_path, usecols=[desc_col, misery_index_col])
    return df


def plot_card_front(card: Card) -> Figure:
    # 62x88 cm for typical playing cards.
    x_total = 6.2  # cm front and back
    y_total = 8.8  # cm top to bottom

    # To be able to convert between centimeters and inches.
    cm_per_inch = 2.54

    # Add margin on all sides.
    margin = 0.5  # cm

    x_size = (x_total + margin) / cm_per_inch
    y_size = (y_total + margin) / cm_per_inch
    xy_size = (x_size, y_size)

    fig, ax = plt.subplots()

    fig.set_size_inches(*xy_size)
    fig.set_facecolor("black")
    fig.subplots_adjust(left=0, bottom=0, right=1, top=1)

    ax.axis("off")

    text_kwargs = dict(wrap=True, horizontalalignment="center", fontfamily="Open Sans")

    # Front.

    # desc_ax = ax.inset_axes([0.1, 0.6, 0.8, 0.4])
    text_with_wrap_autofit(
        ax,
        card.desc.upper(),
        (0.5, 0.8),
        0.8,
        0.5,
        **text_kwargs,
        transform=ax.transAxes,
        min_font_size=10,
        verticalalignment="top",
        weight="extra bold",
        color="yellow",
    )
    # desc_ax.axis("off")

    mi_desc = "misery index"
    ax.text(
        x_size / 2,
        0.2 * (y_size - margin),
        mi_desc.upper(),
        **text_kwargs,
        color="yellow",
        fontsize=13,
        weight="extra bold",
        verticalalignment="center",
    )

    ax.text(
        x_size / 2,
        0.05 * y_size,
        str(card.misery_index).upper(),
        **text_kwargs,
        color="black",
        fontsize=23,
        weight="extra bold",
        verticalalignment="center",
    )

    mi_block = Rectangle((x_size / 4, 0), x_size / 2, y_size / 8, fc="yellow")
    ax.add_patch(mi_block)

    ax.set_xlim(0, x_size)
    ax.set_ylim(0, y_size)

    plt.close(fig)

    return fig


def plot_card_back(card: Card, input_dir: Path) -> Figure:

    # 128x89 cm for typical playing cards.
    x_total = 62  # cm front and back
    y_total = 88  # cm top to bottom

    # To be able to convert between centimeters and inches.
    cm_per_inch = 2.54

    # Add margin on all sides.
    margin = 0.5  # cm

    x_size = (x_total + margin) / cm_per_inch
    y_size = (y_total + margin) / cm_per_inch
    xy_size = (x_size, y_size)

    fig, ax = plt.subplots()

    fig.set_size_inches(*xy_size)
    fig.set_facecolor("black")
    fig.subplots_adjust(left=0, bottom=0, right=1, top=1, wspace=0, hspace=0)

    ax.axis("off")

    text_kwargs = dict(
        wrap=True,
        horizontalalignment="center",
        fontfamily="Open Sans",
    )

    game_name = "Shit Happens"
    expansion_text = "expansion"
    expansion_text_full = card.expansion_name + " " + expansion_text

    ax.text(
        -x_size / 4,
        0.7 * (y_size - margin) / 2,
        game_name.upper(),
        **text_kwargs,
        color="yellow",
        fontsize=17,
        weight="regular",
        verticalalignment="center",
    )

    ax.text(
        -x_size / 4,
        0.6 * (y_size - margin) / 2,
        expansion_text_full.upper(),
        **text_kwargs,
        color="yellow",
        fontsize=7,
        fontstyle="italic",
        weight="ultralight",
        verticalalignment="center",
    )

    game_logo_path = Path(f"{input_dir}/images/game-logo.png")
    game_logo = mpimage.imread(str(game_logo_path))[:, :, 0]

    game_logoax = fig.add_axes([0.1, 0.2, 0.3, 0.5])
    game_logoax.imshow(game_logo, cmap="binary")
    game_logoax.axis("off")

    expansion_logo_path = Path(f"{input_dir}/images/expansion-logo.jpg")
    expansion_logo = mpimage.imread(str(expansion_logo_path))

    expansion_logoax = fig.add_axes([0.1, 0.05, 0.3, 0.1])
    expansion_logoax.imshow(expansion_logo)
    expansion_logoax.axis("off")

    ax.set_xlim(-x_size / 2, x_size / 2)
    ax.set_ylim(-y_size / 2, y_size / 2)

    plt.close(fig)

    return fig


def save_card(
    card: Card,
    output_dir: Path,
    side: Literal["front", "back"],
    dpi: int = 300,
    format: str = ".pdf",
) -> None:

    output_dir = output_dir / side

    output_dir.mkdir(parents=True, exist_ok=True)

    fn = f"{card.misery_index}-{card.desc}"
    fn = slugify(fn)
    save_fn = (output_dir / fn).with_suffix(format)

    if side == "front":
        card.fig_front.savefig(
            str(save_fn), format=save_fn.suffix[1:], pad_inches=0, dpi=dpi
        )
    elif side == "back":
        card.fig_back.savefig(
            str(save_fn), format=save_fn.suffix[1:], pad_inches=0, dpi=dpi
        )


def create_cards(
    df: pd.DataFrame,
    expansion_name: str,
    input_dir: Path,
    output_dir: Path,
    merge: bool,
    side: Literal["front", "back", "both"],
) -> None:
    for i, row in tqdm(df.iterrows(), total=df.shape[0]):
        card = Card(row["desc"], row["misery_index"], expansion_name)

        if side == "front" or side == "both":
            card.fig_front = plot_card_front(card)
            save_card(card, output_dir, "front")

        if side == "back" or side == "both":
            card.fig_back = plot_card_back(card, input_dir)
            save_card(card, output_dir, "back")

        # break

    if merge:
        if side == "front" or side == "both":
            merge_pdfs(output_dir / "front")
        if side == "back" or side == "both":
            merge_pdfs(output_dir / "back")


def main() -> None:
    argParser = argparse.ArgumentParser(
        description="Create custom Shit Happens expansion playing cards."
    )
    argParser.add_argument("input_dir", metavar="input_dir", help="Input directory.")
    argParser.add_argument("-n", "--name", help="Expansion name.")
    argParser.add_argument(
        "-m", "--merge", help="Merge output.", action=argparse.BooleanOptionalAction
    )
    argParser.add_argument(
        "-s",
        "--side",
        help="Side(s) to generate.",
        choices=["front", "back", "both"],
        default="both",
    )
    args = argParser.parse_args(namespace=ShitHappensArgs())

    input_dir = Path(args.input_dir)
    output_dir = input_dir / "outputs"

    xlsx_paths = glob(f"{input_dir / '*.xlsx'}")
    xlsx_paths_num = len(xlsx_paths)
    if not xlsx_paths_num:
        raise Exception(f"No Excel file exists in {input_dir}.")
    elif xlsx_paths_num > 1:
        print("More than one input file found.")
        for i, xlsx_path in enumerate(xlsx_paths, 1):
            print(f"[{i}] {xlsx_path}")
        xlsx_index = int(input(f"Select: "))
        xlsx_path = Path(xlsx_paths[xlsx_index - 1])
    else:
        xlsx_path = Path(xlsx_paths[0])

    if args.name:
        expansion_name = args.name
    else:
        expansion_name = input_dir.stem
        print(
            "Argument -n/--name not given. "
            f"Expansion name inferred to be {expansion_name}."
        )

    df = parse_excel(xlsx_path, 0, 1)

    if args.merge:
        try:
            import PyPDF2
            args.merge = True
        except ImportError:
            args.merge = False
            print("Install pypdf2 for pdf merging.")

    create_cards(df, expansion_name, input_dir, output_dir, args.merge, args.side)

def main_cli():
    try:
        main()
    except KeyboardInterrupt:
        print("Interrupted.")

if __name__ == "__main__":
    main()