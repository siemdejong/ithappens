import re
import unicodedata
from pathlib import Path
from glob import glob
import click


def sort_pdfs_by_mi(fn: str):
    """Key for sorted() to sort filenames by leading number.
    The number must be separated with '-'.
    """
    try:
        return float(Path(fn).stem.split("-")[0])
    except ValueError:
        return -1


def slugify(value, allow_unicode=False):
    """
    Convert to ASCII if 'allow_unicode' is False. Convert spaces or repeated
    dashes to single dashes. Remove characters that aren't alphanumerics,
    underscores, or hyphens. Convert to lowercase. Also strip leading and
    trailing whitespace, dashes, and underscores.
    Source: https://github.com/django/django/blob/0b78ac3fc7bd9f0c57518d0c1a153582318edd59/django/utils/text.py#L420.
    """
    value = str(value)
    if allow_unicode:
        value = unicodedata.normalize("NFKC", value)
    else:
        value = (
            unicodedata.normalize("NFKD", value)
            .encode("ascii", "ignore")
            .decode("ascii")
        )
    value = re.sub(r"[^\w\s-]", "", value.lower())
    return re.sub(r"[-\s]+", "-", value).strip("-_")


def verify_input_dir(input_dir: Path):
    while True:
        if input_dir.exists():
            break
        input_dir = Path(
            input(
                f"Input directory {input_dir} does not exist. "
                "Please specify an existing input directory.\n"
            )
        )

    output_dir = input_dir / "outputs"
    print(f"Reading files from {input_dir}.")
    print(f"Output files in {output_dir}.")

    input_paths = list(glob(f"{input_dir / '*.xlsx'}")) + list(
        glob(f"{input_dir / '*.csv'}")
    )
    input_paths_num = len(input_paths)
    if not input_paths_num:
        print(f"Please provide an input file (.csv or .xlsx) in {input_dir}.")
        exit(1)
    elif input_paths_num > 1:
        while True:
            print("\nMore than one input file found.")
            for i, input_path in enumerate(input_paths, 1):
                print(f"[{i}] {input_path}")
            try:
                input_index = int(click.getchar())
                input_path = Path(input_paths[input_index - 1])
            except (ValueError, IndexError):
                continue
            else:
                break

    else:
        input_path = Path(input_paths[0])

    return input_path, output_dir
