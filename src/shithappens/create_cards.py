import argparse
import gettext
import textwrap
from functools import partial
from glob import glob
from importlib import resources
from multiprocessing import Pool
from pathlib import Path
from typing import Literal, Optional

import click
import matplotlib.font_manager as fm
import matplotlib.image as mpimage
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.patches import Rectangle
from matplotlib.text import Annotation
from matplotlib.transforms import Bbox, Transform

try:
    from tqdm import tqdm
except ImportError:

    def tqdm(iterable, *args, **kwargs):
        del args, kwargs
        return iterable


import sys

SCRIPT_DIR = Path(__file__).absolute().parent
sys.path.append(str(SCRIPT_DIR.parent))

from shithappens.card import Card
from shithappens.utils import merge_pdfs, slugify


def install_lang(locale: str):
    locale_res = resources.files("shithappens.locales").joinpath(
        locale + "/LC_MESSAGES/shithappens.mo"
    )
    with resources.as_file(locale_res) as locale_file:
        localedir = locale_file.parent.parent.parent
    lang = gettext.translation("shithappens", localedir=localedir, languages=[locale])
    global _
    _ = lang.gettext


def text_with_wrap_autofit(
    ax: plt.Axes,
    txt: str,
    xy: tuple[float, float],
    width: float,
    height: float,
    *,
    min_font_size=None,
    bleed: Optional[float] = None,
    pad: Optional[float] = None,
    transform: Optional[Transform] = None,
    ha: Literal["left", "center", "right"] = "center",
    va: Literal["bottom", "center", "top"] = "center",
    **kwargs,
):
    """Automatically fits the text to some axes.

    Args:
        ax: axes to put the text on.
        txt: text to display.
        xy: location to place the text.
        width: width of the text box.
        height: height of the text box.
        min_font_size: minimum acceptable font size.
        bleed: bleed of the figure.
        pad: padding of the box.
        transform: matplotlib coordinate transformation.
        ha: horizontal align.
        va: vertical align.
        **kwargs: keyword arguments passed to Axes.annotate.

    Returns:
        text artist.
    """
    if transform is None:
        transform = ax.transData

    #  Different alignments give different bottom left and top right anchors.
    x, y = xy
    if bleed:
        x += bleed
        y += bleed
    if pad:
        x += pad
        y += pad

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

    return text


class ShitHappensArgs(argparse.Namespace):
    input_dir: str
    name: str
    merge: bool
    rank: bool
    side: Literal["front", "back", "both"]
    lang: Literal["en", "nl"]
    format: Literal["pdf", "png"]
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
        df = pd.read_excel(
            input_path, usecols=[desc_col, misery_index_col], engine="openpyxl"
        )
    except Exception:
        print(_("{} does not contain any Excel files.").format(input_path))
        exit()

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

    x_total = x_size + 2 * bleed
    y_total = y_size + 2 * bleed
    xy_size = (x_total, y_total)

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
        (0.5, 0.9),
        0.7,
        0.4,
        **text_kwargs,
        bleed=ax.transData.transform((bleed, bleed))[0],
        transform=ax.transAxes,
        min_font_size=11,
        va="top",
        weight="extra bold",
        color="yellow",
    )

    mi_desc = _("misery index")
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
        str(card.misery_index).upper(),
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

    ax.set_xlim(0, x_total)
    ax.set_ylim(0, y_total)

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
    expansion_text = _("expansion")
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

    opensans_resource = resources.files("shithappens.opensans.fonts.ttf").joinpath(
        "OpenSans-LightItalic.ttf"
    )
    with resources.as_file(opensans_resource) as fpath:
        prop = fm.FontProperties(fname=fpath)

    text_kwargs = dict(wrap=True, horizontalalignment="center", fontproperties=prop)

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
        expansion_logo = resources.files("shithappens.images").joinpath(
            "expansion-logo.png"
        )
        with resources.as_file(expansion_logo) as fpath:
            expansion_logo_path = str(fpath)

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

    side_fn = _("front") if side == "front" else _("back")

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
):
    card = Card(row[1]["desc"], row[1]["misery_index"], expansion_name)

    if side == "front" or side == "both":
        card.fig_front = plot_card_front(card)
        save_card(card, output_dir, "front", format=ext)

    if side == "back" or side == "both":
        card.fig_back = plot_card_back(card, input_dir)
        save_card(card, output_dir, "back", format=ext)


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
    locale: str,
) -> None:
    nmax = df.shape[0]
    chunksize = nmax // chunks
    create_card_par = partial(
        create_card,
        expansion_name=expansion_name,
        input_dir=input_dir,
        output_dir=output_dir,
        side=side,
        ext=ext,
    )
    desc = _("Plotting cards")
    if chunksize:
        with Pool(workers, install_lang, (locale,)) as p:
            list(
                tqdm(
                    p.imap_unordered(create_card_par, df.iterrows(), chunksize),
                    total=nmax,
                    desc=desc,
                )
            )
    else:
        list(tqdm(map(create_card_par, df.iterrows()), total=nmax, desc=desc))

    if merge:
        if side == "front" or side == "both":
            merge_pdfs(output_dir / _("front"))
        if side == "back" or side == "both":
            merge_pdfs(output_dir / _("back"))


def main() -> None:
    arg_parser = argparse.ArgumentParser(
        description="Create custom Shit Happens expansion playing cards.",
        add_help=False,
    )

    help_group = arg_parser.add_argument_group("help")
    help_group.add_argument(
        "-h", "--help", action="help", help="show this help message and exit"
    )

    input_group = arg_parser.add_argument_group("input")

    input_group.add_argument(
        "input_dir",
        metavar="input_dir",
        nargs="?",
        help="Input directory. Defaults to current working directory.",
        default=Path.cwd(),
    )

    options_group = arg_parser.add_argument_group("options")

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

    options_group.add_argument(
        "-l",
        "--lang",
        help="Language. 'en' and 'nl' supported. Defaults to 'en'.",
        choices=["en", "nl"],
        default="en",
    )
    options_group.add_argument(
        "-f",
        "--format",
        help="Output format. 'pdf' and 'png' supported. Defaults to 'pdf'.",
        choices=["pdf", "png"],
        default="pdf",
    )
    options_group.add_argument(
        "-r",
        "--rank",
        help="Rank situations and output in new file. \
            Does not guarantee a linear ranking, i.e. situations can have equal misery index. \
            Ignores all other options. Defaults to --no-rank.",
        action=argparse.BooleanOptionalAction,
    )

    multiprocessing_group = arg_parser.add_argument_group("multiprocessing")

    multiprocessing_group.add_argument(
        "-w", "--workers", help="Number of workers. Defaults to 4.", default=4
    )
    multiprocessing_group.add_argument(
        "-c",
        "--chunks",
        help="Number of chunks for the workers to process. Defaults to 30.",
        default=30,
    )
    args = arg_parser.parse_args(namespace=ShitHappensArgs())

    install_lang(args.lang)

    try:
        import tqdm
    except ImportError:
        print(_("'pip install shithappens[pbar]' to show a progress bar."))
    else:
        del tqdm

    input_dir = Path(args.input_dir)
    while True:
        if input_dir.exists():
            break
        input_dir = Path(
            input(
                _(
                    "Input directory {} does not exist. Please specify an existing input directory.\n"
                ).format(input_dir)
            )
        )

    output_dir = input_dir / "outputs"
    print(_("Reading files from {}.").format(input_dir))
    print(_("Output files in {}.").format(output_dir))

    xlsx_paths = glob(f"{input_dir / '*.xlsx'}")
    xlsx_paths_num = len(xlsx_paths)
    if not xlsx_paths_num:
        print(_("Please provide an Excel file in {}.").format(input_dir))
        exit(1)
    elif xlsx_paths_num > 1:
        while True:
            print(_("\nMore than one input file found."))
            for i, xlsx_path in enumerate(xlsx_paths, 1):
                print(f"[{i}] {xlsx_path}")
            try:
                xlsx_index = int(click.getchar())
                xlsx_path = Path(xlsx_paths[xlsx_index - 1])
            except (ValueError, IndexError):
                continue
            else:
                break

    else:
        xlsx_path = Path(xlsx_paths[0])

    if args.rank:
        from sort_situations import sort

        sort(xlsx_path, args.lang)
    else:

        if args.name:
            expansion_name = args.name
        else:
            expansion_name = input_dir.stem
            print(
                _(
                    "Argument -n/--name not given. " "Expansion name inferred to be {}."
                ).format(expansion_name)
            )

        df = parse_excel(xlsx_path, 0, 1)

        if args.merge:
            try:
                import PyPDF2

                args.merge = True
            except ImportError:
                args.merge = False
                print(_("'pip install shithappens[merge]' for pdf merging."))
            else:
                del PyPDF2

        create_cards(
            df,
            expansion_name,
            input_dir,
            output_dir,
            args.merge,
            args.side,
            args.format,
            args.workers,
            args.chunks,
            args.lang,
        )


def main_cli():
    try:
        main()
    except KeyboardInterrupt:
        print(_("Interrupted."))


if __name__ == "__main__":
    main()
