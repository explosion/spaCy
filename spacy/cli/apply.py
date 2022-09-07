import tqdm
from itertools import chain
from pathlib import Path
from typing import Optional, Generator, Union

from wasabi import msg

from ._util import app, Arg, Opt, setup_gpu, import_code, walk_directory

from ..tokens import Doc, DocBin
from ..vocab import Vocab
from ..util import ensure_path, load_model


path_help = ("Location of the documents to predict on."
             "Can be a single file in .spacy format or "
             "a text file with one document per line."
             "If a directory is provided each "
             "text file in the directory will be treated "
             "as a single document.")
out_help = "Path where to save the result .spacy file"
code_help = ("Path to Python file with additional "
             "code (registered functions) to be imported")
gold_help = "Use gold preprocessing provided in the .spacy files"


def _stream_file(path: Path, vocab: Vocab) -> Generator[Union[Doc, str], None, None]:
    """
    Stream data from a single file. If the path points to
    a .spacy file then yield from the DocBin otherwise
    yield each line of a text file. If a decoding error
    is encountered during reading the file exit.
    """
    if not path.is_dir():
        # Yield from DocBin.
        if path.suffix == ".spacy":
            docbin = DocBin().from_disk(path)
            for doc in docbin.get_docs(vocab):
                yield doc
        # Yield from text file
        else:
            try:
                with open(path, 'r') as fin:
                    for line in fin:
                        yield line
            except UnicodeDecodeError as e:
                print(e)
                msg.warn(
                    f"{path} could not be decoded.",
                    exits=True
                )


def _maybe_read(path: Path) -> Union[str, None]:
    """
    Try to read the text file from the provided path.
    When encoutering a decoding error just warn and pass.
    """
    with open(path, 'r') as fin:
        try:
            text = fin.read()
            return text
        except UnicodeDecodeError as e:
            msg.warn(f"Skipping file {path}")
            print(e)
            return None


@app.command("apply")
def apply_cli(
    # fmt: off
    model: str = Arg(..., help="Model name or path"),
    data_path: Path = Arg(..., help=path_help, exists=True),
    output: Path = Arg(..., help=out_help, dir_okay=False),
    code_path: Optional[Path] = Opt(None, "--code", "-c", help=code_help),
    use_gpu: int = Opt(-1, "--gpu-id", "-g", help="GPU ID or -1 for CPU."),
    batch_size: int = Opt(1, "--batch-size", "-b", help="Batch size."),
    n_process: int = Opt(1, "--n-process", "-n", help="number of processors to use."),
    suffix: str = Opt("", "--suffix", "-n", help="Only read files with file.suffix.")
):
    """
    Apply a trained pipeline to documents to get predictions.
    Expects a loadable spaCy pipeline and some data as input.
    The data can be provided multiple formats. It can be a single
    .spacy file or a single text file with one document per line.
    A directory can also be provided in which case the 'suffix'
    argument is required. All paths pointing to files with the
    provided suffix will be recursively collected and processed.

    DOCS: https://spacy.io/api/cli#tba
    """
    if data_path.is_dir() and suffix == "":
        raise ValueError(
            "When the provided 'data_path' is a directory "
            "the --suffix argument has to be provided as well."
        )
    if suffix is not None:
        if not suffix.startswith("."):
            suffix = "." + suffix
    import_code(code_path)
    setup_gpu(use_gpu)
    apply(data_path, output, model, batch_size, n_process, suffix)


def apply(
    data_path: Path,
    output: Path,
    model: str,
    batch_size: int,
    n_process: int,
    suffix: str
):
    data_path = ensure_path(data_path)
    output_path = ensure_path(output)
    if not data_path.exists():
        msg.fail("Couldn't find data path.", data_path, exits=1)
    nlp = load_model(model)
    msg.good(f"Loaded model {model}")
    vocab = nlp.vocab
    docbin = DocBin()
    datagen: Union[
        Generator[Union[Doc, str], None, None],
        chain[Union[Doc, str]],
        filter[str]
    ]
    if not data_path.is_dir():
        datagen = _stream_file(data_path, vocab)
    else:
        paths = walk_directory(data_path, suffix)
        if suffix == ".spacy":
            datagen = chain(*[_stream_file(path, vocab) for path in paths])
        else:
            datagen = filter(None, (_maybe_read(path) for path in paths))
    for doc in tqdm.tqdm(nlp.pipe(datagen, batch_size=batch_size, n_process=n_process)):
        docbin.add(doc)
    if output_path.is_dir():
        output_path = output_path / "predictions.spacy"
    docbin.to_disk(output_path)
