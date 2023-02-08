from typing import Optional, Sequence, Union, Iterator
import tqdm
from pathlib import Path
import srsly
import cProfile
import pstats
import sys
import itertools
from wasabi import msg, Printer
from radicli import Arg, ExistingPathOrDash

from ._util import cli
from ..language import Language
from ..util import load_model


@cli.subcommand(
    "debug",
    "profile",
    # fmt: off
    model=Arg(help="Trained pipeline to load"),
    inputs=Arg(help="Location of input file. '-' for stdin."),
    n_texts=Arg("--n-texts", "-n", help="Maximum number of texts to use if available"),
    # fmt: on
)
def profile(
    model: str, inputs: Optional[ExistingPathOrDash] = None, n_texts: int = 10000
) -> None:
    """
    Profile which functions take the most time in a spaCy pipeline.
    Input should be formatted as one JSON object per line with a key "text".
    It can either be provided as a JSONL file, or be read from sys.sytdin.
    If no input file is specified, the IMDB dataset is loaded via Thinc.

    DOCS: https://spacy.io/api/cli#debug-profile
    """
    if inputs is not None:
        texts = _read_inputs(inputs, msg)
        texts = list(itertools.islice(texts, n_texts))
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

        with msg.loading("Loading IMDB dataset via ml_datasets..."):
            imdb_train, _ = ml_datasets.imdb(train_limit=n_texts, dev_limit=0)
            texts, _ = zip(*imdb_train)
        msg.info(f"Loaded IMDB dataset and using {n_texts} examples")
    with msg.loading(f"Loading pipeline '{model}'..."):
        nlp = load_model(model)
    msg.good(f"Loaded pipeline '{model}'")
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
        file_ = input_path.open()  # type: ignore[assignment]
    for line in file_:
        data = srsly.json_loads(line)
        text = data["text"]
        yield text
