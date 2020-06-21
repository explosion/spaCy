import typer
from wasabi import msg


def Arg(*args, help=None, **kwargs):
    # Filter out help for now until it's officially supported
    return typer.Argument(*args, **kwargs)


def Opt(*args, **kwargs):
    return typer.Option(*args, show_default=True, **kwargs)


app = typer.Typer(
    name="spacy",
    help="""spaCy Command-line Interface


DOCS: https://spacy.io/api/cli
""",
)


@app.command("link", no_args_is_help=True, deprecated=True, hidden=True)
def link(*args, **kwargs):
    """As of spaCy v3.0, model symlinks are deprecated. You can load models
    using their full names or from a directory path."""
    msg.warn(
        "As of spaCy v3.0, model symlinks are deprecated. You can load models "
        "using their full names or from a directory path."
    )
