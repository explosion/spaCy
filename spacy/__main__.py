from pathlib import Path

FILE = Path(__file__).parent / "cli.json"


def main():
    from radicli import StaticRadicli

    # TODO: ideally we want to set disable=True for local development, but
    # not sure yet how to best determine that?
    static = StaticRadicli.load(FILE)
    static.run()

    from spacy.cli import setup_cli

    cli = setup_cli()
    cli.run()


if __name__ == "__main__":
    main()
