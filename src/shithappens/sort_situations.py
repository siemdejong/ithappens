import gettext
import itertools
from importlib import resources
from pathlib import Path

import click
import pandas as pd
from tqdm import tqdm

UP = "\x1B[3A"


def install_lang(locale: str):
    locale_res = resources.files("shithappens.locales").joinpath(
        locale + "/LC_MESSAGES/shithappens.mo"
    )
    with resources.as_file(locale_res) as locale_file:
        localedir = locale_file.parent.parent.parent
    lang = gettext.translation("shithappens", localedir=localedir, languages=[locale])
    global _
    _ = lang.gettext


def parse_excel(input_path: Path, desc_col: int) -> pd.DataFrame:
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
        df = pd.read_excel(input_path, usecols=[desc_col], engine="openpyxl")
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


def sort(xlsx_path, lang):
    install_lang(lang)

    df = parse_excel(xlsx_path, 0)
    df["misery_index"] = 0
    df["score"] = 0

    combinations = list(itertools.combinations(df.index, 2))

    print(_("\nWhich situation is most miserable?\n\n"))

    with tqdm(combinations, total=len(combinations)) as progress_iterator:
        for combination in progress_iterator:
            prompt_question(df, combination)

    output_file = xlsx_path.with_name(xlsx_path.stem + "-sorted.xlsx")
    df.sort_values(by=["score"]).to_excel(output_file, index=False)
    if len(df["score"].unique()) != len(df):
        print(
            _(
                "Some items have equal ranking score. Please check the output file ({})."
            ).format(output_file)
        )
    print(_("Manually assign a misery-index to situations."))
