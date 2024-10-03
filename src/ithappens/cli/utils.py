from pathlib import Path
from glob import glob
import click


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

    xlsx_paths = glob(f"{input_dir / '*.xlsx'}")
    xlsx_paths_num = len(xlsx_paths)
    if not xlsx_paths_num:
        print("Please provide an Excel file in {input_dir}.")
        exit(1)
    elif xlsx_paths_num > 1:
        while True:
            print("\nMore than one input file found.")
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
