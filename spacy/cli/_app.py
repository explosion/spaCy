import typer
from typer.main import get_command


COMMAND = "python -m spacy"
NAME = "spacy"
HELP = """spaCy Command-line Interface

DOCS: https://spacy.io/api/cli
"""
PROJECT_HELP = f"""Command-line interface for spaCy projects and working with
project templates. You'd typically start by cloning a project template to a local
directory and fetching its assets like datasets etc. See the project's
project.yml for the available commands.
"""


app = typer.Typer(name=NAME, help=HELP)
project_cli = typer.Typer(name="project", help=PROJECT_HELP, no_args_is_help=True)
app.add_typer(project_cli)

# Wrappers for Typer's annotations. Initially created to set defaults and to
# keep the names short, but not needed at the moment.
Arg = typer.Argument
Opt = typer.Option


def setup_cli() -> None:
    # Ensure that the help messages always display the correct prompt
    command = get_command(app)
    command(prog_name=COMMAND)
