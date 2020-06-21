from spacy.cli import app
from typer.main import get_command

if __name__ == "__main__":
    command = get_command(app)
    # Ensure that the help messages always display the correct prompt
    command(prog_name="python -m spacy")
