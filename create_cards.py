import pandas as pd
from pathlib import Path
from card import Card
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import matplotlib.image as mpimage
from matplotlib.patches import Rectangle
from tqdm import tqdm
from utils import slugify
from glob import glob
import argparse


class ShitHappensArgs(argparse.Namespace):
    input_dir: str
    name: str


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


def plot_card(card: Card, input_dir: Path) -> Figure:

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

    fig.set_size_inches(*xy_size)
    fig.set_facecolor("black")
    fig.subplots_adjust(left=0, bottom=0, right=1, top=1, wspace=0, hspace=0)

    ax.axis("off")

    text_kwargs = dict(wrap=True, horizontalalignment="center", fontfamily="Open Sans",)

    # Front.
    mi_desc = "misery index"

    ax.text(
        x_size / 4,
        0.8 * (y_size - margin) / 2,
        card.desc.upper(),
        **text_kwargs,
        color="yellow",
        fontsize=130,
        weight="extra bold",
        verticalalignment="top",
    )

    ax.text(
        x_size / 4,
        0.0 - 0.6 * (y_size - margin) / 2,
        mi_desc.upper(),
        **text_kwargs,
        color="yellow",
        fontsize=130,
        weight="extra bold",
        verticalalignment="center",
    )

    ax.text(
        x_size / 4,
        -0.9 * (y_size) / 2,
        str(card.misery_index).upper(),
        **text_kwargs,
        color="black",
        fontsize=230,
        weight="extra bold",
        verticalalignment="center",
    )

    mi_block = Rectangle(
        (x_size / 8, -1 * y_size / 2), 2 * x_size / 8, y_size / 8, fc="yellow",
    )
    ax.add_patch(mi_block)

    # Back.
    game_name = "Shit Happens"
    expansion_text = "expansion"
    expansion_text_full = card.expansion_name + " " + expansion_text

    ax.text(
        -x_size / 4,
        0.7 * (y_size - margin) / 2,
        game_name.upper(),
        **text_kwargs,
        color="yellow",
        fontsize=170,
        weight="regular",
        verticalalignment="center",
    )

    ax.text(
        -x_size / 4,
        0.6 * (y_size - margin) / 2,
        expansion_text_full.upper(),
        **text_kwargs,
        color="yellow",
        fontsize=70,
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
    card: Card, output_dir: Path, dpi: int = 300, format: str = ".pdf",
) -> None:

    output_dir.mkdir(parents=True, exist_ok=True)

    fn = f"{card.misery_index}-{card.desc}"
    fn = slugify(fn)
    save_fn = (output_dir / fn).with_suffix(format)

    card.fig.savefig(str(save_fn), format=save_fn.suffix[1:], pad_inches=0, dpi=dpi)


def create_cards(
    df: pd.DataFrame, expansion_name: str, input_dir: Path, output_dir: Path
) -> None:
    for i, row in tqdm(df.iterrows(), total=df.shape[0]):
        card = Card(row["desc"], row["misery_index"], expansion_name)
        card.fig = plot_card(card, input_dir)
        save_card(card, output_dir)
        # break


def main() -> None:

    argParser = argparse.ArgumentParser(
        description="Create custom Shit Happens expansion playing cards."
    )
    argParser.add_argument("input_dir", metavar="input_dir", help="Input directory.")
    argParser.add_argument("-n", "--name", help="Expansion name.")
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

    create_cards(df, expansion_name, input_dir, output_dir)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Interrupted.")
