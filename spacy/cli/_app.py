from typing import Optional
import typer
from typer.main import get_command


COMMAND = "python -m spacy"
NAME = "spacy"
HELP = """spaCy Command-line Interface

DOCS: https://spacy.io/api/cli
"""


app = typer.Typer(name=NAME, help=HELP)


def Arg(*args, help: Optional[str] = None, **kwargs) -> typer.Argument:
    """Wrapper for Typer's annotation to keep it short and set defaults."""
    # Filter out help for now until it's officially supported
    return typer.Argument(*args, **kwargs)


def Opt(*args, **kwargs) -> typer.Option:
    """Wrapper for Typer's annotation to keep it short and set defaults."""
    return typer.Option(*args, show_default=True, **kwargs)


def setup_cli() -> None:
    # Ensure that the help messages always display the correct prompt
    command = get_command(app)
    command(prog_name=COMMAND)
