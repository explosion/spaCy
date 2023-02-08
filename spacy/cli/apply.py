import tqdm
import srsly
from itertools import chain
from pathlib import Path
from typing import Optional, List, Iterable, cast, Union
from wasabi import msg
from radicli import Arg, ExistingPath, ExistingFilePath

from ._util import cli, setup_gpu, import_code, walk_directory
from ..tokens import Doc, DocBin
from ..vocab import Vocab
from ..util import ensure_path, load_model


path_help = """Location of the documents to predict on.
Can be a single file in .spacy format or a .jsonl file.
Files with other extensions are treated as single plain text documents.
If a directory is provided it is traversed recursively to grab
all files to be processed.
The files can be a mixture of .spacy, .jsonl and text files.
If .jsonl is provided the specified field is going
to be grabbed ("text" by default)."""

out_help = "Path to save the resulting .spacy file"
code_help = (
    "Path to Python file with additional " "code (registered functions) to be imported"
)
gold_help = "Use gold preprocessing provided in the .spacy files"
force_msg = (
    "The provided output file already exists. "
    "To force overwriting the output file, set the --force or -F flag."
)


DocOrStrStream = Union[Iterable[str], Iterable[Doc]]


@cli.command(
    "apply",
    # fmt: off
    model=Arg(help="Model name or path"),
    data_path=Arg(help=path_help),
    output_file=Arg(help=out_help),
    code_path=Arg("--code", "-c", help=code_help),
    text_key=Arg("--text-key", "-tk", help="Key containing text string for JSONL"),
    force_overwrite=Arg("--force", "-F", help="Force overwriting the output file"),
    use_gpu=Arg("--gpu-id", "-g", help="GPU ID or -1 for CPU"),
    batch_size=Arg("--batch-size", "-b", help="Batch size"),
    n_process=Arg("--n-process", "-n", help="Number of processors to use"),
    # fmt: on
)
def apply_cli(
    model: str,
    data_path: ExistingPath,
    output_file: Path,
    code_path: Optional[ExistingFilePath] = None,
    text_key: str = "text",
    force_overwrite: bool = False,
    use_gpu: int = -1,
    batch_size: int = 1,
    n_process: int = 1,
):
    """
    Apply a trained pipeline to documents to get predictions.
    Expects a loadable spaCy pipeline and path to the data, which
    can be a directory or a file.
    The data files can be provided in multiple formats:
        1. .spacy files
        2. .jsonl files with a specified "field" to read the text from.
        3. Files with any other extension are assumed to be containing
           a single document.
    DOCS: https://spacy.io/api/cli#apply
    """
    data_path = ensure_path(data_path)
    output_file = ensure_path(output_file)
    code_path = ensure_path(code_path)
    if output_file.exists() and not force_overwrite:
        msg.fail(force_msg, exits=1)
    if not data_path.exists():
        msg.fail(f"Couldn't find data path: {data_path}", exits=1)
    import_code(code_path)
    setup_gpu(use_gpu)
    apply(data_path, output_file, model, text_key, batch_size, n_process)


def apply(
    data_path: Path,
    output_file: Path,
    model: str,
    json_field: str,
    batch_size: int,
    n_process: int,
):
    docbin = DocBin(store_user_data=True)
    paths = walk_directory(data_path)
    if len(paths) == 0:
        docbin.to_disk(output_file)
        msg.warn(
            "Did not find data to process,"
            f" {data_path} seems to be an empty directory."
        )
        return
    nlp = load_model(model)
    vocab = nlp.vocab
    streams: List[DocOrStrStream] = []
    text_files = []
    for path in paths:
        if path.suffix == ".spacy":
            streams.append(_stream_docbin(path, vocab))
        elif path.suffix == ".jsonl":
            streams.append(_stream_jsonl(path, json_field))
        else:
            text_files.append(path)
    if len(text_files) > 0:
        streams.append(_stream_texts(text_files))
    datagen = cast(DocOrStrStream, chain(*streams))
    for doc in tqdm.tqdm(nlp.pipe(datagen, batch_size=batch_size, n_process=n_process)):
        docbin.add(doc)
    if output_file.suffix == "":
        output_file = output_file.with_suffix(".spacy")
    docbin.to_disk(output_file)


def _stream_docbin(path: Path, vocab: Vocab) -> Iterable[Doc]:
    """
    Stream Doc objects from DocBin.
    """
    docbin = DocBin().from_disk(path)
    for doc in docbin.get_docs(vocab):
        yield doc


def _stream_jsonl(path: Path, field: str) -> Iterable[str]:
    """
    Stream "text" field from JSONL. If the field "text" is
    not found it raises error.
    """
    for entry in srsly.read_jsonl(path):
        if field not in entry:
            msg.fail(f"{path} does not contain the required '{field}' field.", exits=1)
        else:
            yield entry[field]


def _stream_texts(paths: Iterable[Path]) -> Iterable[str]:
    """Yields strings from text files in paths."""
    for path in paths:
        with open(path, "r") as fin:
            text = fin.read()
            yield text
