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
