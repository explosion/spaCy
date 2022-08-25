import tqdm
import sys

from ._util import app, Arg, Opt, setup_gpu, import_code
from typing import Optional, Generator
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
    vocab: Vocab
) -> Generator[Doc, None, None]:
    """
    Load data which is either in a single file
    in .spacy or plain text format or multiple
    text files in a directory.
    """
    # XXX I know that we have it in the developer guidelines
    # to don't try/except, but I thought its appropriate here.
    # because we are not sure exactly what input we are getting.
    if not data_path.is_dir():
        # Yield from DocBin.
        try:
            docbin = DocBin().from_disk(data_path)
            for doc in docbin.get_docs(vocab):
                yield doc
        # Yield from text file.
        except ValueError:
            try:
                with open(data_path, 'r') as fin:
                    for line in fin:
                        yield line
            except UnicodeDecodeError:
                print(
                    f"file {data_path} does not seem "
                    "to be a plain text file"
                )
                sys.exit()
    else:
        # Yield per one file in directory
        for path in data_path.iterdir():
            if path.is_dir():
                raise ValueError(
                    "All files should be text files."
                )
            with open(path, 'r') as fin:
                try:
                    text = fin.read()
                    yield text
                except UnicodeDecodeError:
                    print(
                        f"file {path} does not seem "
                        "to be a plain text file"
                    )
                    sys.exit()


@app.command("apply")
def apply_cli(
    # fmt: off
    model: str = Arg(..., help="Model name or path"),
    data_path: Path = Arg(..., help=path_help, exists=True),
    output: Optional[Path] = Arg(..., help=out_help, dir_okay=False),
    code_path: Optional[Path] = Opt(None, "--code", "-c", help=code_help),
    use_gpu: int = Opt(-1, "--gpu-id", "-g", help="GPU ID or -1 for CPU"),
    batch_size: int = Opt(1, "--batch-size", "-b", help="Batch size"),
    n_process: int = Opt(1, "--n-process", "-n", help="Number of processors to use")
):
    """
    Apply a trained pipeline to documents to get predictions.
    Expects a loadable spaCy pipeline and some data as input.
    The input can be provided multiple formats. It can be a .spacy
    file, a single text file with one document per line or a directory
    where each file is assumed to be plain text document.

    DOCS: https://spacy.io/api/cli#tba
    """
    import_code(code_path)
    setup_gpu(use_gpu)
    apply(data_path, output, model, batch_size, n_process)


def apply(
    data_path: Path,
    output: Path,
    model: str,
    batch_size: int,
    n_process: int
):
    data_path = util.ensure_path(data_path)
    output_path = util.ensure_path(output)
    if not data_path.exists():
        msg.fail("Couldn't find data path.", data_path, exits=1)
    nlp = util.load_model(model)
    msg.good(f"Loaded model {model}")
    vocab = nlp.vocab
    docbin = DocBin()
    datagen = _stream_data(data_path, vocab)
    for doc in tqdm.tqdm(nlp.pipe(datagen, batch_size=batch_size, n_process=n_process)):
        docbin.add(doc)
    if output_path.is_dir():
        output_path = output_path / "predictions.spacy"
    docbin.to_disk(output_path)
