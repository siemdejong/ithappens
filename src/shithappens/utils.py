import re
import unicodedata
from glob import glob
from pathlib import Path
from typing import Optional


def sort_pdfs_by_mi(fn: str):
    """Key for sorted() to sort filenames by leading number.
    The number must be separated with '-'.
    """
    try:
        return float(Path(fn).stem.split("-")[0])
    except ValueError:
        return -1


def merge_pdfs(input_dir: Path, output_dir: Optional[Path] = None):
    """Merges all the pdf files in current directory.
    Source: https://stackoverflow.com/a/47356404/8797886.
    """
    from PyPDF2 import PdfMerger

    merger = PdfMerger()
    allpdfs = [
        a
        for a in sorted(
            glob(str(input_dir / "*.pdf")),
            key=sort_pdfs_by_mi,
        )
        if "merged" not in a
    ]
    for pdf in allpdfs:
        merger.append(pdf)

    if output_dir is None:
        output_dir = input_dir

    with open(output_dir / "merged.pdf", "wb") as merged_pdf:
        merger.write(merged_pdf)


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
