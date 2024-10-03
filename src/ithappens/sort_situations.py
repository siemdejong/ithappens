import itertools
from pathlib import Path
from typing import Literal

import click
import pandas as pd
from tqdm import tqdm

UP = "\x1b[3A"
ERASE = "\x1b[2A"


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
        print(f"{input_path} does not contain any Excel files.")
        exit()

    return df


def prompt_question(df: pd.DataFrame, situations, round=None):
    tqdm.write(f"{UP}")
    for i, situation in enumerate(situations, 1):
        tqdm.write(f"[{i}] #{situation} {df.loc[situation]['desc']}")
    try:
        most_miserable_idx = int(click.getchar())
        if most_miserable_idx == 0:
            raise ValueError("0 is not a valid choice.")
        df.loc[situations[most_miserable_idx - 1], "score"] += 1
        if round is not None:
            df.loc[situations[0], f"round_{round}"] = situations[1]
            df.loc[situations[1], f"round_{round}"] = situations[0]
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
            "Some items have equal ranking score. "
            f"Please check the output file ({output_file})."
        )
    print("Manually assign a misery-index to situations.")


def sort(
    xlsx_path,
    output_dir,
    strategy: Literal["swiss", "round-robin"] = "swiss",
    rounds=9,
    prescore=10,
):
    df = parse_excel(xlsx_path, 0)

    if strategy == "swiss":
        print("\n")
        if prescore == 10:
            print("Rate the situation 1-10. (Press 0 for rate 10.)")
        else:
            print("Rate this situation 1-{}".format(prescore))
        try:
            df["score"]
        except KeyError:
            df["score"] = 0
        # First, give items scores 1-9 and 0, with 0=10.
        with tqdm(
            df.iterrows(),
            desc="Prescore",
            total=len(df),
            maxinterval=1,
            unit="situation",
        ) as prog_iter:
            for i, situation in prog_iter:
                tqdm.write(ERASE)
                tqdm.write(situation["desc"])
                while True:
                    try:
                        score_group = int(click.getchar())
                    except ValueError:
                        continue
                    else:
                        break
                df.loc[i, "score"] += score_group if score_group > 0 else 10
        df = df.sort_values(by="score")

        splits = []
        num_groups = 10
        step = int(len(df) / (num_groups - 1))

        # Force step to be even.
        if step % 2 != 0:
            step -= 1
        i = 0
        while i < len(df):
            splits.append(i)
            i += step
        if splits[-1] != len(df) - 1:
            splits.append(len(df) - 1)

        print("\n\n\n")
        print("Which situation is worse?")

        for round_num in tqdm(
            range(rounds), desc="Round", total=rounds, unit="round", maxinterval=1
        ):
            df[f"round_{round_num}"] = None
            for split_begin, split_end in tqdm(
                zip(splits, splits[1:]),
                total=len(splits),
                unit="split",
                leave=False,
                position=1,
                maxinterval=1,
                desc="Split",
            ):
                range_list = range(split_begin, split_end)
                index_list_temp = zip(range_list, range_list[::-1])
                index_list = []
                for item in index_list_temp:
                    if item[0] < item[1]:
                        index_list.append(item)
                for idx1, idx2 in tqdm(
                    index_list,
                    total=len(index_list),
                    maxinterval=1,
                    leave=False,
                    position=2,
                    desc="Comparison",
                    unit="comparison",
                ):
                    df_idx1, df_idx2 = df.index[idx1], df.index[idx2]
                    df_temp_idx2 = df_idx2
                    # No rematches.
                    while True:
                        if idx1 in [
                            df.loc[df_temp_idx2, f"round_{round_n}"]
                            for round_n in range(round_num + 1)
                        ]:
                            df_temp_idx2 -= 1
                        else:
                            break
                    if idx1 >= idx2:
                        with open("test.txt", "a") as f:
                            f.write(f"{idx1}, {idx2}\n")
                        break
                    prompt_question(df, [df_idx1, df_temp_idx2], round_num)
            df = df.sort_values(by="score")

            save(xlsx_path, df)

    elif strategy == "round-robin":
        try:
            continue_from = df["score"].sum()
            print(f"Continuing from situation {continue_from}")
        except KeyError:
            df["misery_index"] = 0
            df["score"] = 0
            continue_from = 0

        combinations = list(itertools.combinations(df.index, 2))[continue_from:]

        print("\nWhich situation is most miserable?\n\n")

        try:
            with tqdm(
                combinations,
                total=len(combinations),
                initial=continue_from,
                smoothing=0,
            ) as progress_iterator:
                for combination in progress_iterator:
                    prompt_question(df, combination)
        except KeyboardInterrupt:
            print("Do you want to save your progress? [y]/n")
            save_progress = click.getchar()
            if not save_progress:
                save_progress = True
            elif save_progress == "n":
                save_progress = False

            if save_progress:
                save(xlsx_path, df)
        else:
            save(xlsx_path, df)


def main_cli(**kwargs):
    try:
        from ithappens.cli.utils import verify_input_dir

        xlsx_path, output_dir = verify_input_dir(Path(kwargs["input_dir"]))
        sort(
            xlsx_path,
            output_dir,
            kwargs["strategy"],
            kwargs["rounds"],
            kwargs["prescore"],
        )
    except KeyboardInterrupt:
        print("Interrupted.")
