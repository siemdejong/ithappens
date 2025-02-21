from pathlib import Path

import click

from ithappens.create_cards import main_cli as create_cli


@click.group(help="Create custom Shit Happens expansion playing cards.")
def cli():
    pass


@cli.command(help="Create cards.")
@click.argument(
    "input_file", type=click.Path(exists=True, dir_okay=False, readable=True)
)
@click.argument("output_dir", type=click.Path(file_okay=False))
@click.option(
    "-n",
    "--name",
    "name",
    help="Expansion name. If no name is specified, infers name from input_dir.",
)
@click.option("-m", "--merge", "merge", is_flag=True, help="Merge output.")
@click.option(
    "-s",
    "--side",
    "side",
    type=click.Choice(["front", "back", "both"], case_sensitive=False),
    default="both",
    help="Side(s) to generate.",
)
@click.option(
    "-e",
    "--expansion_logo_path",
    "expansion_logo_path",
    type=click.Path(exists=True, dir_okay=False, readable=True),
    default=None,
    help="Expansion logo path.",
)
@click.option(
    "-f",
    "--format",
    "format",
    type=click.Choice(["pdf", "png"], case_sensitive=False),
    default="pdf",
    help="Output format.",
)
@click.option(
    "-w", "--workers", "workers", type=int, default=4, help="Number of workers."
)
@click.argument(
    "image_dir", type=click.Path(file_okay=False, path_type=Path), required=False
)
def create(**kwargs):
    create_cli(**kwargs)
