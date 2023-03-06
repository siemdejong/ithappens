import gettext
import itertools
from importlib import resources
from pathlib import Path

import click
import pandas as pd
from tqdm import tqdm

UP = "\x1B[3A"


def parse_excel(input_path: Path, desc_col: int, score_col: int = 2) -> pd.DataFrame:
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
        df = pd.read_excel(input_path, usecols=[desc_col, score_col], engine="openpyxl")
    except Exception:
        print(_("{} does not contain any Excel files.".format(input_path)))
        exit()

    return df


def prompt_question(df: pd.DataFrame, situations):
    tqdm.write(f"{UP}")
    for i, situation in enumerate(situations, 1):
        tqdm.write(f"[{i}] {df.loc[situation]['desc']}")
    try:
        most_miserable_idx = int(click.getchar())
        df.loc[situations[most_miserable_idx - 1], "score"] += 1
    except (ValueError, IndexError):
        prompt_question(df, situations)

def save(xlsx_path, df):
    if "sorted" in xlsx_path.stem:
        in_place = True
    else:
        in_place = False

    if in_place:
        output_file = xlsx_path
    else:
        output_file = xlsx_path.with_name(xlsx_path.stem + "-sorted.xlsx")
    df.to_excel(output_file, index=False)

    if len(df["score"].unique()) != len(df):
        print(
            _(
                "Some items have equal ranking score. Please check the output file ({})."
            ).format(output_file)
        )
    print(_("Manually assign a misery-index to situations."))

def sort(xlsx_path):

    df = parse_excel(xlsx_path, 0)
    try:
        continue_from = df["score"].sum()
        print(_("Continuing from situation {}".format(continue_from)))
    except KeyError:
        df["misery_index"] = 0
        df["score"] = 0
        continue_from = 0

    combinations = list(itertools.combinations(df.index, 2))[continue_from:]

    print(_("\nWhich situation is most miserable?\n\n"))

    try:
        with tqdm(combinations, total=len(combinations), initial=continue_from) as progress_iterator:
            for combination in progress_iterator:
                prompt_question(df, combination)
    except KeyboardInterrupt:
        print(_("Do you want to save your progress? [y]/n"))
        save_progress = click.getchar()
        if not save_progress:
            save_progress = True
        elif save_progress == "n":
            save_progress = False
        
        if save_progress:
            save(xlsx_path, df)
    else:
        save(xlsx_path, df)
