from pathlib import Path
import os

FILE = Path(__file__).parent / "cli.json"
IS_DEBUG = "SPACY_CLI_DEBUG" in os.environ
IS_DISABLED = "SPACY_CLI_NO_STATIC" in os.environ


def main():
    from radicli import StaticRadicli

    # TODO: ideally we want to set disable=True for local development, but
    # not sure yet how to best determine that?
    static = StaticRadicli.load(FILE, debug=IS_DEBUG, disable=IS_DISABLED)
    static.run()

    from spacy.cli import setup_cli

    cli = setup_cli()
    cli.run()


if __name__ == "__main__":
    main()
