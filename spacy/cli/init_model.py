from typing import Optional, List, Dict, Any, Union, IO
import math
from tqdm import tqdm
import numpy
from ast import literal_eval
from pathlib import Path
from preshed.counter import PreshCounter
import tarfile
import gzip
import zipfile
import srsly
import warnings
from wasabi import msg, Printer
import typer
from ._util import init_cli, Arg, Opt, parse_config_overrides, show_validation_error

DEFAULT_OOV_PROB = -20


#@init_cli.command("vocab")
#@app.command(
#    "init-model",
#    context_settings={"allow_extra_args": True, "ignore_unknown_options": True},
#    hidden=True,  # hide this from main CLI help but still allow it to work with warning
#)
def init_model_cli(
    # fmt: off
    ctx: typer.Context,  # This is only used to read additional arguments
    lang: str = Arg(..., help="Pipeline language"),
    output_dir: Path = Arg(..., help="Pipeline output directory"),
    freqs_loc: Optional[Path] = Arg(None, help="Location of words frequencies file", exists=True),
    clusters_loc: Optional[Path] = Opt(None, "--clusters-loc", "-c", help="Optional location of brown clusters data", exists=True),
    jsonl_loc: Optional[Path] = Opt(None, "--jsonl-loc", "-j", help="Location of JSONL-formatted attributes file", exists=True),
    vectors_loc: Optional[Path] = Opt(None, "--vectors-loc", "-v", help="Optional vectors file in Word2Vec format", exists=True),
    prune_vectors: int = Opt(-1, "--prune-vectors", "-V", help="Optional number of vectors to prune to"),
    truncate_vectors: int = Opt(0, "--truncate-vectors", "-t", help="Optional number of vectors to truncate to when reading in vectors file"),
    vectors_name: Optional[str] = Opt(None, "--vectors-name", "-vn", help="Optional name for the word vectors, e.g. en_core_web_lg.vectors"),
    model_name: Optional[str] = Opt(None, "--meta-name", "-mn", help="Optional name of the package for the pipeline meta"),
    base_model: Optional[str] = Opt(None, "--base", "-b", help="Name of or path to base pipeline to start with (mostly relevant for pipelines with custom tokenizers)")
    # fmt: on
):
    """
    Create a new blank pipeline directory with vocab and vectors from raw data.
    If vectors are provided in Word2Vec format, they can be either a .txt or
    zipped as a .zip or .tar.gz.

    DOCS: https://nightly.spacy.io/api/cli#init-vocab
    """
    if ctx.command.name == "init-model":
        msg.warn(
            "The init-model command is now called 'init vocab'. You can run "
            "'python -m spacy init --help' for an overview of the other "
            "available initialization commands."
        )
    init_vocab(
        lang,
        output_dir,
        freqs_loc=freqs_loc,
        clusters_loc=clusters_loc,
        jsonl_loc=jsonl_loc,
        vectors_loc=vectors_loc,
        prune_vectors=prune_vectors,
        truncate_vectors=truncate_vectors,
        vectors_name=vectors_name,
        model_name=model_name,
        base_model=base_model,
        silent=False,
    )
