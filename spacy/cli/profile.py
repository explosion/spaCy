import tqdm
from pathlib import Path
import srsly
import cProfile
import pstats
import sys
import itertools
import ml_datasets
from wasabi import msg

from ..util import load_model


def profile(
    # fmt: off
    model: ("Model to load", "positional", None, str),
    inputs: ("Location of input file. '-' for stdin.", "positional", None, str) = None,
    n_texts: ("Maximum number of texts to use if available", "option", "n", int) = 10000,
    # fmt: on
):
    """
    Profile a spaCy pipeline, to find out which functions take the most time.
    Input should be formatted as one JSON object per line with a key "text".
    It can either be provided as a JSONL file, or be read from sys.sytdin.
    If no input file is specified, the IMDB dataset is loaded via Thinc.
    """
    if inputs is not None:
        inputs = _read_inputs(inputs, msg)
    if inputs is None:
        n_inputs = 25000
        with msg.loading("Loading IMDB dataset via Thinc..."):
            imdb_train, _ = ml_datasets.imdb()
            inputs, _ = zip(*imdb_train)
        msg.info(f"Loaded IMDB dataset and using {n_inputs} examples")
        inputs = inputs[:n_inputs]
    with msg.loading(f"Loading model '{model}'..."):
        nlp = load_model(model)
    msg.good(f"Loaded model '{model}'")
    texts = list(itertools.islice(inputs, n_texts))
    cProfile.runctx("parse_texts(nlp, texts)", globals(), locals(), "Profile.prof")
    s = pstats.Stats("Profile.prof")
    msg.divider("Profile stats")
    s.strip_dirs().sort_stats("time").print_stats()


def parse_texts(nlp, texts):
    for doc in nlp.pipe(tqdm.tqdm(texts), batch_size=16):
        pass


def _read_inputs(loc, msg):
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
