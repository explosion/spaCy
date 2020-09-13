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

from ._util import app, init_cli, Arg, Opt
from ..vectors import Vectors
from ..errors import Errors, Warnings
from ..language import Language
from ..util import ensure_path, get_lang_class, load_model, OOV_RANK

try:
    import ftfy
except ImportError:
    ftfy = None


DEFAULT_OOV_PROB = -20


@init_cli.command("vocab")
@app.command(
    "init-model",
    context_settings={"allow_extra_args": True, "ignore_unknown_options": True},
    hidden=True,  # hide this from main CLI help but still allow it to work with warning
)
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
    init_model(
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


def init_model(
    lang: str,
    output_dir: Path,
    freqs_loc: Optional[Path] = None,
    clusters_loc: Optional[Path] = None,
    jsonl_loc: Optional[Path] = None,
    vectors_loc: Optional[Path] = None,
    prune_vectors: int = -1,
    truncate_vectors: int = 0,
    vectors_name: Optional[str] = None,
    model_name: Optional[str] = None,
    base_model: Optional[str] = None,
    silent: bool = True,
) -> Language:
    msg = Printer(no_print=silent, pretty=not silent)
    if jsonl_loc is not None:
        if freqs_loc is not None or clusters_loc is not None:
            settings = ["-j"]
            if freqs_loc:
                settings.append("-f")
            if clusters_loc:
                settings.append("-c")
            msg.warn(
                "Incompatible arguments",
                "The -f and -c arguments are deprecated, and not compatible "
                "with the -j argument, which should specify the same "
                "information. Either merge the frequencies and clusters data "
                "into the JSONL-formatted file (recommended), or use only the "
                "-f and -c files, without the other lexical attributes.",
            )
        jsonl_loc = ensure_path(jsonl_loc)
        lex_attrs = srsly.read_jsonl(jsonl_loc)
    else:
        clusters_loc = ensure_path(clusters_loc)
        freqs_loc = ensure_path(freqs_loc)
        if freqs_loc is not None and not freqs_loc.exists():
            msg.fail("Can't find words frequencies file", freqs_loc, exits=1)
        lex_attrs = read_attrs_from_deprecated(msg, freqs_loc, clusters_loc)

    with msg.loading("Creating blank pipeline..."):
        nlp = create_model(lang, lex_attrs, name=model_name, base_model=base_model)

    msg.good("Successfully created blank pipeline")
    if vectors_loc is not None:
        add_vectors(
            msg, nlp, vectors_loc, truncate_vectors, prune_vectors, vectors_name
        )
    vec_added = len(nlp.vocab.vectors)
    lex_added = len(nlp.vocab)
    msg.good(
        "Sucessfully compiled vocab", f"{lex_added} entries, {vec_added} vectors",
    )
    if not output_dir.exists():
        output_dir.mkdir()
    nlp.to_disk(output_dir)
    return nlp


def open_file(loc: Union[str, Path]) -> IO:
    """Handle .gz, .tar.gz or unzipped files"""
    loc = ensure_path(loc)
    if tarfile.is_tarfile(str(loc)):
        return tarfile.open(str(loc), "r:gz")
    elif loc.parts[-1].endswith("gz"):
        return (line.decode("utf8") for line in gzip.open(str(loc), "r"))
    elif loc.parts[-1].endswith("zip"):
        zip_file = zipfile.ZipFile(str(loc))
        names = zip_file.namelist()
        file_ = zip_file.open(names[0])
        return (line.decode("utf8") for line in file_)
    else:
        return loc.open("r", encoding="utf8")


def read_attrs_from_deprecated(
    msg: Printer, freqs_loc: Optional[Path], clusters_loc: Optional[Path]
) -> List[Dict[str, Any]]:
    if freqs_loc is not None:
        with msg.loading("Counting frequencies..."):
            probs, _ = read_freqs(freqs_loc)
        msg.good("Counted frequencies")
    else:
        probs, _ = ({}, DEFAULT_OOV_PROB)  # noqa: F841
    if clusters_loc:
        with msg.loading("Reading clusters..."):
            clusters = read_clusters(clusters_loc)
        msg.good("Read clusters")
    else:
        clusters = {}
    lex_attrs = []
    sorted_probs = sorted(probs.items(), key=lambda item: item[1], reverse=True)
    if len(sorted_probs):
        for i, (word, prob) in tqdm(enumerate(sorted_probs)):
            attrs = {"orth": word, "id": i, "prob": prob}
            # Decode as a little-endian string, so that we can do & 15 to get
            # the first 4 bits. See _parse_features.pyx
            if word in clusters:
                attrs["cluster"] = int(clusters[word][::-1], 2)
            else:
                attrs["cluster"] = 0
            lex_attrs.append(attrs)
    return lex_attrs


def create_model(
    lang: str,
    lex_attrs: List[Dict[str, Any]],
    name: Optional[str] = None,
    base_model: Optional[Union[str, Path]] = None,
) -> Language:
    if base_model:
        nlp = load_model(base_model)
        # keep the tokenizer but remove any existing pipeline components due to
        # potentially conflicting vectors
        for pipe in nlp.pipe_names:
            nlp.remove_pipe(pipe)
    else:
        lang_class = get_lang_class(lang)
        nlp = lang_class()
    for lexeme in nlp.vocab:
        lexeme.rank = OOV_RANK
    for attrs in lex_attrs:
        if "settings" in attrs:
            continue
        lexeme = nlp.vocab[attrs["orth"]]
        lexeme.set_attrs(**attrs)
    if len(nlp.vocab):
        oov_prob = min(lex.prob for lex in nlp.vocab) - 1
    else:
        oov_prob = DEFAULT_OOV_PROB
    nlp.vocab.cfg.update({"oov_prob": oov_prob})
    if name:
        nlp.meta["name"] = name
    return nlp


def add_vectors(
    msg: Printer,
    nlp: Language,
    vectors_loc: Optional[Path],
    truncate_vectors: int,
    prune_vectors: int,
    name: Optional[str] = None,
) -> None:
    vectors_loc = ensure_path(vectors_loc)
    if vectors_loc and vectors_loc.parts[-1].endswith(".npz"):
        nlp.vocab.vectors = Vectors(data=numpy.load(vectors_loc.open("rb")))
        for lex in nlp.vocab:
            if lex.rank and lex.rank != OOV_RANK:
                nlp.vocab.vectors.add(lex.orth, row=lex.rank)
    else:
        if vectors_loc:
            with msg.loading(f"Reading vectors from {vectors_loc}"):
                vectors_data, vector_keys = read_vectors(
                    msg, vectors_loc, truncate_vectors
                )
            msg.good(f"Loaded vectors from {vectors_loc}")
        else:
            vectors_data, vector_keys = (None, None)
        if vector_keys is not None:
            for word in vector_keys:
                if word not in nlp.vocab:
                    nlp.vocab[word]
        if vectors_data is not None:
            nlp.vocab.vectors = Vectors(data=vectors_data, keys=vector_keys)
    if name is None:
        # TODO: Is this correct? Does this matter?
        nlp.vocab.vectors.name = f"{nlp.meta['lang']}_{nlp.meta['name']}.vectors"
    else:
        nlp.vocab.vectors.name = name
    nlp.meta["vectors"]["name"] = nlp.vocab.vectors.name
    if prune_vectors >= 1:
        nlp.vocab.prune_vectors(prune_vectors)


def read_vectors(msg: Printer, vectors_loc: Path, truncate_vectors: int):
    f = open_file(vectors_loc)
    f = ensure_shape(f)
    shape = tuple(int(size) for size in next(f).split())
    if truncate_vectors >= 1:
        shape = (truncate_vectors, shape[1])
    vectors_data = numpy.zeros(shape=shape, dtype="f")
    vectors_keys = []
    for i, line in enumerate(tqdm(f)):
        line = line.rstrip()
        pieces = line.rsplit(" ", vectors_data.shape[1])
        word = pieces.pop(0)
        if len(pieces) != vectors_data.shape[1]:
            msg.fail(Errors.E094.format(line_num=i, loc=vectors_loc), exits=1)
        vectors_data[i] = numpy.asarray(pieces, dtype="f")
        vectors_keys.append(word)
        if i == truncate_vectors - 1:
            break
    return vectors_data, vectors_keys


def ensure_shape(lines):
    """Ensure that the first line of the data is the vectors shape.

    If it's not, we read in the data and output the shape as the first result,
    so that the reader doesn't have to deal with the problem.
    """
    first_line = next(lines)
    try:
        shape = tuple(int(size) for size in first_line.split())
    except ValueError:
        shape = None
    if shape is not None:
        # All good, give the data
        yield first_line
        yield from lines
    else:
        # Figure out the shape, make it the first value, and then give the
        # rest of the data.
        width = len(first_line.split()) - 1
        captured = [first_line] + list(lines)
        length = len(captured)
        yield f"{length} {width}"
        yield from captured


def read_freqs(
    freqs_loc: Path, max_length: int = 100, min_doc_freq: int = 5, min_freq: int = 50
):
    counts = PreshCounter()
    total = 0
    with freqs_loc.open() as f:
        for i, line in enumerate(f):
            freq, doc_freq, key = line.rstrip().split("\t", 2)
            freq = int(freq)
            counts.inc(i + 1, freq)
            total += freq
    counts.smooth()
    log_total = math.log(total)
    probs = {}
    with freqs_loc.open() as f:
        for line in tqdm(f):
            freq, doc_freq, key = line.rstrip().split("\t", 2)
            doc_freq = int(doc_freq)
            freq = int(freq)
            if doc_freq >= min_doc_freq and freq >= min_freq and len(key) < max_length:
                try:
                    word = literal_eval(key)
                except SyntaxError:
                    # Take odd strings literally.
                    word = literal_eval(f"'{key}'")
                smooth_count = counts.smoother(int(freq))
                probs[word] = math.log(smooth_count) - log_total
    oov_prob = math.log(counts.smoother(0)) - log_total
    return probs, oov_prob


def read_clusters(clusters_loc: Path) -> dict:
    clusters = {}
    if ftfy is None:
        warnings.warn(Warnings.W004)
    with clusters_loc.open() as f:
        for line in tqdm(f):
            try:
                cluster, word, freq = line.split()
                if ftfy is not None:
                    word = ftfy.fix_text(word)
            except ValueError:
                continue
            # If the clusterer has only seen the word a few times, its
            # cluster is unreliable.
            if int(freq) >= 3:
                clusters[word] = cluster
            else:
                clusters[word] = "0"
    # Expand clusters with re-casing
    for word, cluster in list(clusters.items()):
        if word.lower() not in clusters:
            clusters[word.lower()] = cluster
        if word.title() not in clusters:
            clusters[word.title()] = cluster
        if word.upper() not in clusters:
            clusters[word.upper()] = cluster
    return clusters
