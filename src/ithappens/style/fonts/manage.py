"""Add font files to the matplotlib font manager.

If adding new fonts, copy from
https://matplotlib.org/stable/users/explain/customizing.html#the-default-matplotlibrc-file
and keep only the settings that are different from the default.
"""

import pathlib

from matplotlib import font_manager


def _add_fonts() -> None:
    """Add font files to the matplotlib font manager."""
    fonts_module_dir = pathlib.Path(__file__).parent
    font_files = font_manager.findSystemFonts(fontpaths=[fonts_module_dir])

    for font_file in font_files:
        font_manager.fontManager.addfont(font_file)


__all__ = ["_add_fonts"]
