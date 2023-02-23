from wasabi import msg
from spacy.__main__ import FILE
from spacy.cli import setup_cli

if __name__ == "__main__":
    cli = setup_cli()
    cli.to_static(FILE)
    msg.good("Successfully generated static CLI", str(FILE))
