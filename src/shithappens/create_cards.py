import argparse
import textwrap
from functools import partial
from glob import glob
from importlib import resources
from pathlib import Path
from typing import Literal, Optional

import matplotlib.font_manager as fm
import matplotlib.image as mpimage
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.figure import Figure
from matplotlib.patches import Rectangle
from matplotlib.text import Annotation
from matplotlib.transforms import Bbox, Transform
from tqdm.contrib.concurrent import process_map

try:
    from tqdm import tqdm
except ImportError:

    def tqdm(iterable, *args, **kwargs):
        del args, kwargs
        return iterable


from shithappens.card import Card
from shithappens.utils import merge_pdfs, slugify


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
    workers: int
    chunks: int


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
    try:
        df = pd.read_excel(input_path, usecols=[desc_col, misery_index_col], engine="openpyxl")
    except Exception:
        print(f"{input_path} does not contain any Excel files.")
        exit()

    return df


def plot_card_front(card: Card) -> Figure:
    # 62x88 mm for typical playing cards.
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

    opensans_resource = resources.files("shithappens.opensans.fonts.ttf").joinpath(
        "OpenSans-ExtraBold.ttf"
    )
    with resources.as_file(opensans_resource) as fpath:
        prop = fm.FontProperties(fname=fpath)

    text_kwargs = dict(wrap=True, horizontalalignment="center", fontproperties=prop)

    # Front.
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
    # 62x88 mm for typical playing cards.
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

    opensans_resource = resources.files("shithappens.opensans.fonts.ttf").joinpath(
        "OpenSans-Regular.ttf"
    )
    with resources.as_file(opensans_resource) as fpath:
        prop = fm.FontProperties(fname=fpath)

    text_kwargs = dict(wrap=True, horizontalalignment="center", fontproperties=prop)

    game_name = "Shit Happens"
    expansion_text = "expansion"
    expansion_text_full = card.expansion_name + " " + expansion_text

    ax.text(
        x_size / 2,
        0.9 * y_size,
        game_name.upper(),
        **text_kwargs,
        color="yellow",
        fontsize=17,
        weight="regular",
        verticalalignment="center",
    )

    opensans_resource = resources.files("shithappens.opensans.fonts.ttf").joinpath(
        "OpenSans-LightItalic.ttf"
    )
    with resources.as_file(opensans_resource) as fpath:
        prop = fm.FontProperties(fname=fpath)

    text_kwargs = dict(wrap=True, horizontalalignment="center", fontproperties=prop)

    ax.text(
        x_size / 2,
        0.85 * y_size,
        expansion_text_full.upper(),
        **text_kwargs,
        color="yellow",
        fontsize=7,
        fontstyle="italic",
        weight="ultralight",
        verticalalignment="center",
    )

    # Game logo.
    game_logo_path = f"{input_dir}/images/game-logo.png"
    if not Path(game_logo_path).exists():
        game_logo = resources.files("shithappens.images").joinpath(
            "game-logo.png"
        )
        with resources.as_file(game_logo) as fpath:
            game_logo_path = str(fpath)
    game_logo = mpimage.imread(game_logo_path)[:, :, 0]

    game_logoax = fig.add_axes([0.1, 0.3, 0.8, 0.5])
    game_logoax.imshow(game_logo, cmap="binary")
    game_logoax.axis("off")

    # Expansion logo.
    expansion_logo_path = f"{input_dir}/images/expansion-logo.png"
    if not Path(expansion_logo_path).exists():
        expansion_logo = resources.files("shithappens.images").joinpath(
            "expansion-logo.png"
        )
        with resources.as_file(expansion_logo) as fpath:
            expansion_logo_path = str(fpath)
    expansion_logo = mpimage.imread(str(expansion_logo_path))

    expansion_logoax = fig.add_axes([0.1, 0.05, 0.8, 0.1])
    expansion_logoax.imshow(expansion_logo)
    expansion_logoax.axis("off")

    ax.set_xlim(0, x_size)
    ax.set_ylim(0, y_size)

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


def create_card(row, expansion_name, input_dir, output_dir, side):
    card = Card(row[1]["desc"], row[1]["misery_index"], expansion_name)

    if side == "front" or side == "both":
        card.fig_front = plot_card_front(card)
        save_card(card, output_dir, "front")

    if side == "back" or side == "both":
        card.fig_back = plot_card_back(card, input_dir)
        save_card(card, output_dir, "back")


def create_cards(
    df: pd.DataFrame,
    expansion_name: str,
    input_dir: Path,
    output_dir: Path,
    merge: bool,
    side: Literal["front", "back", "both"],
    workers: int,
    chunks: int,
) -> None:
    nmax = df.shape[0]
    chunksize = nmax // chunks
    create_card_par = partial(
        create_card,
        expansion_name=expansion_name,
        input_dir=input_dir,
        output_dir=output_dir,
        side=side,
    )
    process_map(
        create_card_par,
        df.iterrows(),
        max_workers=workers,
        chunksize=chunksize,
        total=nmax,
        desc="Plotting cards"
    )

    if merge:
        if side == "front" or side == "both":
            merge_pdfs(output_dir / "front")
        if side == "back" or side == "both":
            merge_pdfs(output_dir / "back")


def main() -> None:
    arg_parser = argparse.ArgumentParser(
        description="Create custom Shit Happens expansion playing cards.",
        add_help=False
    )

    help_group = arg_parser.add_argument_group('help')
    help_group.add_argument("-h", "--help", action='help', help="show this help message and exit")

    input_group = arg_parser.add_argument_group('input')

    input_group.add_argument(
        "input_dir",
        metavar="input_dir",
        nargs="?",
        help="Input directory. Defaults to current working directory.",
        default=Path.cwd(),
    )

    options_group = arg_parser.add_argument_group('options')

    options_group.add_argument(
        "-n",
        "--name",
        help="Expansion name. If no name is specified, infers name from input_dir.",
    )
    options_group.add_argument(
        "-m",
        "--merge",
        help="Merge output. Defaults to --no-merge",
        action=argparse.BooleanOptionalAction,
    )
    options_group.add_argument(
        "-s",
        "--side",
        help="Side(s) to generate. Defaults to both.",
        choices=["front", "back", "both"],
        default="both",
    )

    multiprocessing_group = arg_parser.add_argument_group('multiprocessing')

    multiprocessing_group.add_argument("-w", "--workers", help="Number of workers.", default=4)
    multiprocessing_group.add_argument(
        "-c",
        "--chunks",
        help="Number of chunks for the workers to process.",
        default=30,
    )
    args = arg_parser.parse_args(namespace=ShitHappensArgs())

    try:
        import tqdm
    except ImportError:
        print("Install tqdm to add a progress bar.")
    else:
        del tqdm


    input_dir = Path(args.input_dir)
    while True:
        if input_dir.exists():
            break
        input_dir = Path(input(f"Input directory {input_dir} does not exist. Please specify an existing input directory.\n"))

    xlsx_paths = glob(f"{input_dir / '*.xlsx'}")
    xlsx_paths_num = len(xlsx_paths)
    if not xlsx_paths_num:
        print(f"Please provide an Excel file in {input_dir}.")
        exit(1)
    elif xlsx_paths_num > 1:
        print("More than one input file found.")
        for i, xlsx_path in enumerate(xlsx_paths, 1):
            print(f"[{i}] {xlsx_path}")
        xlsx_index = int(input(f"Select: "))
        xlsx_path = Path(xlsx_paths[xlsx_index - 1])
    else:
        xlsx_path = Path(xlsx_paths[0])

    output_dir = input_dir / "outputs"
    print(f"Reading files from {input_dir}.")
    print(f"Output files in {output_dir}.")

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
        else:
            del PyPDF2

    create_cards(
        df,
        expansion_name,
        input_dir,
        output_dir,
        args.merge,
        args.side,
        args.workers,
        args.chunks,
    )


def main_cli():
    try:
        main()
    except KeyboardInterrupt:
        print("Interrupted.")


if __name__ == "__main__":
    main()
