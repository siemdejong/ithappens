import click

from ithappens.create_cards import main_cli as create_cli
from ithappens.sort_situations import main_cli as sort_cli


@click.group(help="Create custom Shit Happens expansion playing cards.")
def cli():
    pass


@cli.command(help="Create cards.")
@click.argument("input_dir")
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
@click.option(
    "-c",
    "--chunks",
    "chunks",
    type=int,
    default=30,
    help="Number of chunks for the workers to process",
)
def create(**kwargs):
    create_cli(**kwargs)


@cli.command(help="Rank situation.")
@click.argument("input_dir")
@click.option(
    "-s",
    "--strategy",
    "strategy",
    type=click.Choice(["swiss", "round-robin"], case_sensitive=False),
    default="swiss",
    help="Ranking strategy.",
)
@click.option(
    "-r",
    "--rounds",
    "rounds",
    type=int,
    default=9,
    help="The number of rounds to use with the swiss strategy.",
)
@click.option(
    "-p",
    "--prescore",
    "prescore",
    type=int,
    default=10,
    help="The number of groups to prescore.",
)
def rank(**kwargs):
    sort_cli(**kwargs)
