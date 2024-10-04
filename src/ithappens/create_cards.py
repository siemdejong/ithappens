import argparse
import textwrap
import zipfile
from functools import partial
from glob import glob
from multiprocessing import Pool
from pathlib import Path
from typing import Literal, Optional

import matplotlib.font_manager as fm
import matplotlib.image as mpimage
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.axes import Axes
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.figure import Figure
from matplotlib.patches import Rectangle
from matplotlib.text import Annotation
from matplotlib.transforms import Bbox
from tqdm import tqdm


from ithappens.card import Card
from ithappens.utils import slugify, verify_input_dir


def text_with_wrap_autofit(
    ax: plt.Axes,
    txt: str,
    xy_size: tuple[float, float],
    width: float,
    height: float,
    *,
    min_font_size=None,
    bleed: Optional[float] = None,
    pad: Optional[float] = None,
    show_rect: bool = False,
    **kwargs,
):
    """Automatically fits the text to some axes.

    Args:
        ax: axes to put the text on.
        txt: text to display.
        xy: location to place the text.
        width: width of the text box in fractions.
        height: height of the text box in fractions.
        min_font_size: minimum acceptable font size.
        bleed: bleed of the figure.
        pad: padding of the box.
        **kwargs: keyword arguments passed to Axes.annotate.

    Returns:
        text artist.
    """

    #  Different alignments give different bottom left and top right anchors.
    x, y = xy_size
    if bleed is None:
        bleed = 0
    if pad:
        bleed += pad
        x -= 2 * pad
        y -= 2 * pad

    if show_rect:
        alpha = 0.3
    else:
        alpha = 0

    rect = Rectangle(
        (bleed + (1 - width) * x, bleed + (1 - height) * y),
        width * x,
        height * y,
        alpha=alpha,
    )
    ax.add_patch(rect)

    # Get transformation to go from display to data-coordinates.
    inv_data = ax.transData.inverted()

    fig: Figure = ax.get_figure()
    dpi = fig.dpi
    rect_height_inch = rect.get_height() / dpi

    # Initial fontsize according to the height of boxes
    fontsize = rect_height_inch * 72

    wrap_lines = 1
    xy = (bleed + 0.5 * x, bleed + 0.95 * y)
    while True:
        wrapped_txt = "\n".join(
            textwrap.wrap(txt, width=len(txt) // wrap_lines, break_long_words=False)
        )

        # For dramatic effect, place text after ellipsis on newline.
        wrapped_txt = wrapped_txt.replace("... ", "...\n")
        wrapped_txt = wrapped_txt.replace("… ", "...\n")
        text: Annotation = ax.annotate(wrapped_txt, xy, **kwargs)
        text.set_fontsize(fontsize)

        # Adjust the fontsize according to the box size.
        bbox: Bbox = text.get_window_extent()
        inv_text_bbox = inv_data.transform(bbox)
        width_text = inv_text_bbox[1][0] - inv_text_bbox[0][0]
        adjusted_size = fontsize * rect.get_width() / width_text
        if min_font_size is None or adjusted_size >= min_font_size:
            break
        text.remove()
        wrap_lines += 1
    text.set_fontsize(adjusted_size)

    return text


class ithappensArgs(argparse.Namespace):
    input_dir: str
    name: str
    merge: bool
    rank: bool
    side: Literal["front", "back", "both"]
    format: Literal["pdf", "png"]
    workers: int
    chunks: int


def parse_input_file(
    input_path: Path,
) -> pd.DataFrame:
    """Parse an input file.

    It must have two colums: descriptions along with their misery index.

    Args:
        intput_path: path of the input file (.csv or .xlsx)

    Returns:
        Pandas DataFrame with index, description, and misery index.
    """
    usecols = ["misery index", "situation"]
    try:
        df = pd.read_excel(input_path, usecols=usecols)
    except zipfile.BadZipFile:
        pass
    except ValueError:
        print(f"Make sure {input_path} has two columns named {usecols}.")
        exit()
    else:
        return df

    try:
        df = pd.read_csv(input_path, names=usecols)
    except UnicodeDecodeError:
        print(f"{input_path} is not a valid .csv or .xlsx file.")
        exit()
    except ValueError:
        print(f"Make sure {input_path} has two columns named {usecols}.")
        exit()
    else:
        return df


def plot_crop_marks(ax: Axes, bleed: float, factor: float = 0.6):
    """Plots crop marks on the given axis.
    The crop marks will mark the bleed. The crop mark size is adjustable with the factor.
    """
    crop_mark_len = factor * bleed
    fig = ax.get_figure()
    bbox: Bbox = ax.get_window_extent().transformed(fig.dpi_scale_trans.inverted())
    x_size, y_size = bbox.width, bbox.height

    # h, v - horizontal, vertical
    # u, d - up, down
    # l, r - left, right
    hul = (y_size - bleed, 0, crop_mark_len)
    hdl = (bleed, 0, crop_mark_len)
    hur = (y_size - bleed, x_size - crop_mark_len, x_size)
    hdr = (bleed, x_size - crop_mark_len, x_size)
    vul = (bleed, y_size - crop_mark_len, y_size)
    vdl = (bleed, 0, crop_mark_len)
    vur = (x_size - bleed, y_size - crop_mark_len, y_size)
    vdr = (x_size - bleed, 0, crop_mark_len)

    cropmarkstyle = {"color": "white", "linewidth": 1}

    for horizontal_mark in [hul, hdl, hur, hdr]:
        ax.hlines(*horizontal_mark, **cropmarkstyle)
    for vertical_mark in [vul, vdl, vur, vdr]:
        ax.vlines(*vertical_mark, **cropmarkstyle)


def plot_card_front(card: Card) -> Figure:
    # To be able to convert between centimeters and inches.
    cm_per_inch = 2.54

    # 62x88 mm for typical playing cards.
    x_size = 6.2 / cm_per_inch  # cm front and back
    y_size = 8.8 / cm_per_inch  # cm top to bottom

    # Add margin on all sides.
    bleed = 0.5 / cm_per_inch  # cm
    pad = 0.3 / cm_per_inch

    x_total = x_size + 2 * bleed
    y_total = y_size + 2 * bleed
    xy_size = (x_total, y_total)

    plt.style.use("ithappens")
    fig, ax = plt.subplots()

    fig.set_size_inches(*xy_size)
    fig.set_facecolor("black")
    fig.subplots_adjust(left=0, bottom=0, right=1, top=1)

    ax.axis("off")

    ax.set_xlim(0, x_total)
    ax.set_ylim(0, y_total)

    prop = fm.FontProperties(weight="extra bold")

    text_kwargs = dict(wrap=True, horizontalalignment="center", fontproperties=prop)

    # Front.
    text_with_wrap_autofit(
        ax,
        card.desc.upper(),
        (x_size, y_size),
        1,
        0.4,
        **text_kwargs,
        bleed=bleed,
        pad=pad,
        min_font_size=11,
        va="top",
        weight="extra bold",
        color="yellow",
    )

    mi_desc = "misery index"
    ax.text(
        x_total / 2,
        1.3 * y_size / 8 + bleed,
        mi_desc.upper(),
        **text_kwargs,
        color="yellow",
        fontsize=13,
        weight="extra bold",
        verticalalignment="center",
    )

    ax.text(
        x_total / 2,
        0.05 * y_size + bleed,
        card.misery_index if ".5" in str(card.misery_index) else int(card.misery_index),
        **text_kwargs,
        color="black",
        fontsize=23,
        weight="extra bold",
        verticalalignment="center",
    )

    mi_block = Rectangle(
        (bleed + x_size / 4, 0), x_size / 2, y_size / 8 + bleed, fc="yellow"
    )
    ax.add_patch(mi_block)

    plot_crop_marks(ax, bleed)

    plt.close(fig)

    return fig


def plot_card_back(card: Card, input_dir: Path) -> Figure:
    # To be able to convert between centimeters and inches.
    cm_per_inch = 2.54

    # 62x88 mm for typical playing cards.
    x_size = 6.2 / cm_per_inch  # cm front and back
    y_size = 8.8 / cm_per_inch  # cm top to bottom

    # Add margin on all sides.
    bleed = 0.5 / cm_per_inch  # cm

    x_total = x_size + 2 * bleed
    y_total = y_size + 2 * bleed
    xy_size = (x_total, y_total)

    plt.style.use("ithappens")
    fig, ax = plt.subplots()

    fig.set_size_inches(*xy_size)
    fig.set_facecolor("black")
    fig.subplots_adjust(left=0, bottom=0, right=1, top=1)

    ax.axis("off")

    parent_dir = Path(__file__).parent.resolve()

    prop_regular = fm.FontProperties(weight="regular")

    text_kwargs = dict(
        wrap=True, horizontalalignment="center", fontproperties=prop_regular
    )

    game_name = "It Happens"
    expansion_text = "edition"
    expansion_text_full = card.expansion_name + " " + expansion_text

    ax.text(
        x_size / 2 + bleed,
        0.9 * y_size + bleed,
        game_name.upper(),
        **text_kwargs,
        color="yellow",
        fontsize=20,
        weight="regular",
        verticalalignment="center",
    )

    prop_light = fm.FontProperties(weight="regular")

    text_kwargs = dict(
        wrap=True, horizontalalignment="center", fontproperties=prop_light
    )

    ax.text(
        x_size / 2 + bleed,
        0.83 * y_size + bleed,
        expansion_text_full.upper(),
        **text_kwargs,
        color="yellow",
        fontsize=14,
        fontstyle="italic",
        weight="ultralight",
        verticalalignment="center",
    )

    # Expansion logo

    try:
        expansion_logo_path = glob(f"{input_dir}/**/expansion-logo.*")[0]
    except KeyError:
        expansion_logo_path = str(parent_dir / Path("images/expansion-logo.png"))

    expansion_logo = mpimage.imread(expansion_logo_path)

    expansion_logoax = fig.add_axes([0.2, 0.1, 0.6, 0.6])
    expansion_logoax.imshow(
        expansion_logo,
    )
    expansion_logoax.axis("off")

    plot_crop_marks(ax, bleed)

    ax.set_xlim(0, x_total)
    ax.set_ylim(0, y_total)

    plt.close(fig)

    return fig


def save_card(
    card: Card,
    output_dir: Path,
    side: Literal["front", "back"],
    dpi: int = 300,
    format: str = "pdf",
) -> None:
    side_fn = "front" if side == "front" else "back"

    output_dir = output_dir / side_fn

    output_dir.mkdir(parents=True, exist_ok=True)

    fn = f"{card.misery_index}-{card.desc}"
    fn = slugify(fn)
    save_fn = (output_dir / fn).with_suffix("." + format)

    if side == "front":
        card.fig_front.savefig(
            str(save_fn),
            format=save_fn.suffix[1:],
            pad_inches=0,
            dpi=dpi,
            transparent=False,
        )
    elif side == "back":
        card.fig_back.savefig(
            str(save_fn),
            format=save_fn.suffix[1:],
            pad_inches=0,
            dpi=dpi,
            transparent=False,
        )


def create_card(
    row, expansion_name, input_dir, output_dir, side, ext: Literal["pdf", "png"]
) -> Card:
    card = Card(row[1]["desc"], row[1]["misery_index"], expansion_name)

    if side == "front" or side == "both":
        card.fig_front = plot_card_front(card)
        save_card(card, output_dir, "front", format=ext)

    if side == "back" or side == "both":
        card.fig_back = plot_card_back(card, input_dir)
        save_card(card, output_dir, "back", format=ext)

    return card


def create_cards(
    df: pd.DataFrame,
    expansion_name: str,
    input_dir: Path,
    output_dir: Path,
    merge: bool,
    side: Literal["front", "back", "both"],
    ext: Literal["pdf", "png"],
    workers: int,
    chunks: int,
) -> None:
    nmax = df.shape[0]
    chunksize = max(nmax // chunks, 1)
    create_card_par = partial(
        create_card,
        expansion_name=expansion_name,
        input_dir=input_dir,
        output_dir=output_dir,
        side=side,
        ext=ext,
    )
    desc = "Plotting cards"
    with Pool(workers) as p:
        cards = list(
            tqdm(
                p.imap_unordered(create_card_par, df.iterrows(), chunksize),
                total=nmax,
                desc=desc,
            )
        )

    if merge:
        with PdfPages(output_dir / "front" / "merged.pdf") as pdf:
            for card in cards:
                pdf.savefig(card.fig_front)
        with PdfPages(output_dir / "back" / "merged.pdf") as pdf:
            for card in cards:
                pdf.savefig(card.fig_back)


def main(**args) -> None:
    input_dir = Path(args["input_dir"])
    input_path, output_dir = verify_input_dir(input_dir)

    if args["name"]:
        expansion_name = args["name"]
    else:
        expansion_name = input_dir.stem
        print(
            "Argument -n/--name not given. "
            f"Expansion name inferred to be {expansion_name}."
        )

    df = parse_input_file(input_path)

    create_cards(
        df,
        expansion_name,
        input_dir,
        output_dir,
        args["merge"],
        args["side"],
        args["format"],
        args["workers"],
        args["chunks"],
    )


def main_cli(**kwargs):
    try:
        main(**kwargs)
    except KeyboardInterrupt:
        print("Interrupted.")


if __name__ == "__main__":
    main()
