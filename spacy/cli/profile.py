from typing import Optional, Sequence, Union, Iterator
import tqdm
from pathlib import Path
import srsly
import cProfile
import pstats
import sys
import itertools
from wasabi import msg, Printer
import typer

from ._util import app, debug_cli, Arg, Opt, NAME
from ..language import Language
from ..util import load_model


@debug_cli.command("profile")
@app.command("profile", hidden=True)
def profile_cli(
    # fmt: off
    ctx: typer.Context,  # This is only used to read current calling context
    model: str = Arg(..., help="Trained pipeline to load"),
    inputs: Optional[Path] = Arg(None, help="Location of input file. '-' for stdin.", exists=True, allow_dash=True),
    n_texts: int = Opt(10000, "--n-texts", "-n", help="Maximum number of texts to use if available"),
    # fmt: on
):
    """
    Profile which functions take the most time in a spaCy pipeline.
    Input should be formatted as one JSON object per line with a key "text".
    It can either be provided as a JSONL file, or be read from sys.sytdin.
    If no input file is specified, the IMDB dataset is loaded via Thinc.

    DOCS: https://spacy.io/api/cli#debug-profile
    """
    if ctx.parent.command.name == NAME:  # called as top-level command
        msg.warn(
            "The profile command is now available via the 'debug profile' "
            "subcommand. You can run python -m spacy debug --help for an "
            "overview of the other available debugging commands."
        )
    profile(model, inputs=inputs, n_texts=n_texts)


def profile(model: str, inputs: Optional[Path] = None, n_texts: int = 10000) -> None:

    if inputs is not None:
        inputs = _read_inputs(inputs, msg)
    if inputs is None:
        try:
            import ml_datasets
        except ImportError:
            msg.fail(
                "This command, when run without an input file, "
                "requires the ml_datasets library to be installed: "
                "pip install ml_datasets",
                exits=1,
            )

        n_inputs = 25000
        with msg.loading("Loading IMDB dataset via Thinc..."):
            imdb_train, _ = ml_datasets.imdb()
            inputs, _ = zip(*imdb_train)
        msg.info(f"Loaded IMDB dataset and using {n_inputs} examples")
        inputs = inputs[:n_inputs]
    with msg.loading(f"Loading pipeline '{model}'..."):
        nlp = load_model(model)
    msg.good(f"Loaded pipeline '{model}'")
    texts = list(itertools.islice(inputs, n_texts))
    cProfile.runctx("parse_texts(nlp, texts)", globals(), locals(), "Profile.prof")
    s = pstats.Stats("Profile.prof")
    msg.divider("Profile stats")
    s.strip_dirs().sort_stats("time").print_stats()


def parse_texts(nlp: Language, texts: Sequence[str]) -> None:
    for doc in nlp.pipe(tqdm.tqdm(texts), batch_size=16):
        pass


def _read_inputs(loc: Union[Path, str], msg: Printer) -> Iterator[str]:
    if loc == "-":
        msg.info("Reading input from sys.stdin")
        file_ = sys.stdin
        file_ = (line.encode("utf8") for line in file_)
    else:
        input_path = Path(loc)
        if not input_path.exists() or not input_path.is_file():
            msg.fail("Not a valid input data file", loc, exits=1)
        msg.info(f"Using data from {input_path.parts[-1]}")
        file_ = input_path.open()
    for line in file_:
        data = srsly.json_loads(line)
        text = data["text"]
        yield text
