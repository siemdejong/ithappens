import re
import unicodedata
from pathlib import Path


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
