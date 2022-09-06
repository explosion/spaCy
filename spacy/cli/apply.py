import tqdm
import sys

from ._util import app, Arg, Opt, setup_gpu, import_code
from typing import Optional, Generator, Union
from pathlib import Path
from wasabi import msg

from ..tokens import Doc, DocBin
from ..vocab import Vocab
from .. import util


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


def _stream_data(
    data_path: Path,
    vocab: Vocab,
    suffix: Optional[str] = None
) -> Generator[Union[str, Doc], None, None]:
    """
    Load data which is either in a single file
    in .spacy or plain text format or multiple
    text files in a directory. If a directory
    is provided skip subdirectories and undecodeable
    files.
    """
    if not data_path.is_dir():
        # Yield from DocBin.
        if data_path.suffix == ".spacy":
            docbin = DocBin().from_disk(data_path)
            for doc in docbin.get_docs(vocab):
                yield doc
        # Yield from text file
        else:
            try:
                with open(data_path, 'r') as fin:
                    for line in fin:
                        yield line
            except UnicodeDecodeError as e:
                print(e)
                msg.warn(
                    f"{data_path} could not be decoded.",
                    exits=True
                )
    else:
        # Yield per one file in directory
        for path in data_path.iterdir():
            if path.is_dir():
                msg.warn(f"Skipping directory {path}")
            elif suffix is not None and path.suffix != suffix:
                print(suffix, path.suffix)
                msg.warn(f"Skipping file {path}")
            else:
                with open(path, 'r') as fin:
                    try:
                        text = fin.read()
                        yield text
                    except UnicodeDecodeError as e:
                        msg.warn(f"Skipping file {path}")
                        print(e)


@app.command("apply")
def apply_cli(
    # fmt: off
    model: str = Arg(..., help="Model name or path"),
    data_path: Path = Arg(..., help=path_help, exists=True),
    output: Path = Arg(..., help=out_help, dir_okay=False),
    code_path: Optional[Path] = Opt(None, "--code", "-c", help=code_help),
    use_gpu: Optional[int] = Opt(-1, "--gpu-id", "-g", help="GPU ID or -1 for CPU."),
    batch_size: Optional[int] = Opt(1, "--batch-size", "-b", help="Batch size."),
    n_process: Optional[int] = Opt(1, "--n-process", "-n", help="number of processors to use."),
    suffix: Optional[str] = Opt(None, "--suffix", "-n", help="Only read files with file.suffix.")
):
    """
    Apply a trained pipeline to documents to get predictions.
    Expects a loadable spaCy pipeline and some data as input.
    The input can be provided multiple formats. It can be a .spacy
    file, a single text file with one document per line or a directory
    where each file is assumed to be plain text document.

    DOCS: https://spacy.io/api/cli#tba
    """
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
    suffix: Optional[str]
):
    data_path = util.ensure_path(data_path)
    output_path = util.ensure_path(output)
    if not data_path.exists():
        msg.fail("Couldn't find data path.", data_path, exits=1)
    nlp = util.load_model(model)
    msg.good(f"Loaded model {model}")
    vocab = nlp.vocab
    docbin = DocBin()
    datagen = _stream_data(data_path, vocab, suffix)
    for doc in tqdm.tqdm(nlp.pipe(datagen, batch_size=batch_size, n_process=n_process)):
        docbin.add(doc)
    if output_path.is_dir():
        output_path = output_path / "predictions.spacy"
    docbin.to_disk(output_path)
