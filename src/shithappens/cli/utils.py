from pathlib import Path
from glob import glob
import click

from shithappens.utils import install_lang

install_lang("en")

def verify_input_dir(input_dir: Path):
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
    
    return xlsx_path, output_dir