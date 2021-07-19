from typing import Optional, Any, List, Union
from enum import Enum
from pathlib import Path
from wasabi import Printer
import srsly
import re
import sys
import itertools

from ._util import app, Arg, Opt
from ..training import docs_to_json
from ..tokens import DocBin
from ..training.converters import iob_to_docs, conll_ner_to_docs, json_to_docs
from ..training.converters import conllu_to_docs


# Converters are matched by file extension except for ner/iob, which are
# matched by file extension and content. To add a converter, add a new
# entry to this dict with the file extension mapped to the converter function
# imported from /converters.

CONVERTERS = {
    "conllubio": conllu_to_docs,
    "conllu": conllu_to_docs,
    "conll": conll_ner_to_docs,
    "ner": conll_ner_to_docs,
    "iob": iob_to_docs,
    "json": json_to_docs,
}


# File types that can be written to stdout
FILE_TYPES_STDOUT = ("json",)


class FileTypes(str, Enum):
    json = "json"
    spacy = "spacy"


@app.command("convert")
def convert_cli(
    # fmt: off
    input_path: str = Arg(..., help="Input file or directory", exists=True),
    output_dir: Path = Arg("-", help="Output directory. '-' for stdout.", allow_dash=True, exists=True),
    file_type: FileTypes = Opt("spacy", "--file-type", "-t", help="Type of data to produce"),
    n_sents: int = Opt(1, "--n-sents", "-n", help="Number of sentences per doc (0 to disable)"),
    seg_sents: bool = Opt(False, "--seg-sents", "-s", help="Segment sentences (for -c ner)"),
    model: Optional[str] = Opt(None, "--model", "--base", "-b", help="Trained spaCy pipeline for sentence segmentation to use as base (for --seg-sents)"),
    morphology: bool = Opt(False, "--morphology", "-m", help="Enable appending morphology to tags"),
    merge_subtokens: bool = Opt(False, "--merge-subtokens", "-T", help="Merge CoNLL-U subtokens"),
    converter: str = Opt("auto", "--converter", "-c", help=f"Converter: {tuple(CONVERTERS.keys())}"),
    ner_map: Optional[Path] = Opt(None, "--ner-map", "-nm", help="NER tag mapping (as JSON-encoded dict of entity types)", exists=True),
    lang: Optional[str] = Opt(None, "--lang", "-l", help="Language (if tokenizer required)"),
    concatenate: bool = Opt(None, "--concatenate", "-C", help="Concatenate output to a single file"),
    # fmt: on
):
    """
    Convert files into json or DocBin format for training. The resulting .spacy
    file can be used with the train command and other experiment management
    functions.

    If no output_dir is specified and the output format is JSON, the data
    is written to stdout, so you can pipe them forward to a JSON file:
    $ spacy convert some_file.conllu --file-type json > some_file.json

    DOCS: https://spacy.io/api/cli#convert
    """
    if isinstance(file_type, FileTypes):
        # We get an instance of the FileTypes from the CLI so we need its string value
        file_type = file_type.value
    input_path = Path(input_path)
    output_dir = "-" if output_dir == Path("-") else output_dir
    silent = output_dir == "-"
    msg = Printer(no_print=silent)
    verify_cli_args(msg, input_path, output_dir, file_type, converter, ner_map)
    converter = _get_converter(msg, converter, input_path)
    convert(
        input_path,
        output_dir,
        file_type=file_type,
        n_sents=n_sents,
        seg_sents=seg_sents,
        model=model,
        morphology=morphology,
        merge_subtokens=merge_subtokens,
        converter=converter,
        ner_map=ner_map,
        lang=lang,
        concatenate=concatenate,
        silent=silent,
        msg=msg,
    )


def convert(
    input_path: Union[str, Path],
    output_dir: Union[str, Path],
    *,
    file_type: str = "json",
    n_sents: int = 1,
    seg_sents: bool = False,
    model: Optional[str] = None,
    morphology: bool = False,
    merge_subtokens: bool = False,
    converter: str = "auto",
    ner_map: Optional[Path] = None,
    lang: Optional[str] = None,
    concatenate: bool = False,
    silent: bool = True,
    msg: Optional[Printer],
) -> None:
    if not msg:
        msg = Printer(no_print=silent)
    ner_map = srsly.read_json(ner_map) if ner_map is not None else None
    doc_files = []
    for input_loc in walk_directory(Path(input_path), converter):
        with input_loc.open("r", encoding="utf-8") as infile:
            input_data = infile.read()
        # Use converter function to convert data
        func = CONVERTERS[converter]
        docs = func(
            input_data,
            n_sents=n_sents,
            seg_sents=seg_sents,
            append_morphology=morphology,
            merge_subtokens=merge_subtokens,
            lang=lang,
            model=model,
            no_print=silent,
            ner_map=ner_map,
        )
        doc_files.append((input_loc, docs))
    if concatenate:
        all_docs = itertools.chain.from_iterable([docs for _, docs in doc_files])
        doc_files = [(input_path, all_docs)]
    for input_loc, docs in doc_files:
        if file_type == "json":
            data = [docs_to_json(docs)]
            len_docs = len(data)
        else:
            db = DocBin(docs=docs, store_user_data=True)
            len_docs = len(db)
            data = db.to_bytes()
        if output_dir == "-":
            _print_docs_to_stdout(data, file_type)
        else:
            if input_loc != input_path:
                subpath = input_loc.relative_to(input_path)
                output_file = Path(output_dir) / subpath.with_suffix(f".{file_type}")
            else:
                output_file = Path(output_dir) / input_loc.parts[-1]
                output_file = output_file.with_suffix(f".{file_type}")
            _write_docs_to_file(data, output_file, file_type)
            msg.good(f"Generated output file ({len_docs} documents): {output_file}")


def _print_docs_to_stdout(data: Any, output_type: str) -> None:
    if output_type == "json":
        srsly.write_json("-", data)
    else:
        sys.stdout.buffer.write(data)


def _write_docs_to_file(data: Any, output_file: Path, output_type: str) -> None:
    if not output_file.parent.exists():
        output_file.parent.mkdir(parents=True)
    if output_type == "json":
        srsly.write_json(output_file, data)
    else:
        with output_file.open("wb") as file_:
            file_.write(data)


def autodetect_ner_format(input_data: str) -> Optional[str]:
    # guess format from the first 20 lines
    lines = input_data.split("\n")[:20]
    format_guesses = {"ner": 0, "iob": 0}
    iob_re = re.compile(r"\S+\|(O|[IB]-\S+)")
    ner_re = re.compile(r"\S+\s+(O|[IB]-\S+)$")
    for line in lines:
        line = line.strip()
        if iob_re.search(line):
            format_guesses["iob"] += 1
        if ner_re.search(line):
            format_guesses["ner"] += 1
    if format_guesses["iob"] == 0 and format_guesses["ner"] > 0:
        return "ner"
    if format_guesses["ner"] == 0 and format_guesses["iob"] > 0:
        return "iob"
    return None


def walk_directory(path: Path, converter: str) -> List[Path]:
    if not path.is_dir():
        return [path]
    paths = [path]
    locs = []
    seen = set()
    for path in paths:
        if str(path) in seen:
            continue
        seen.add(str(path))
        if path.parts[-1].startswith("."):
            continue
        elif path.is_dir():
            paths.extend(path.iterdir())
        elif converter == "json" and not path.parts[-1].endswith("json"):
            continue
        elif converter == "conll" and not path.parts[-1].endswith("conll"):
            continue
        elif converter == "iob" and not path.parts[-1].endswith("iob"):
            continue
        else:
            locs.append(path)
    # It's good to sort these, in case the ordering messes up cache.
    locs.sort()
    return locs


def verify_cli_args(
    msg: Printer,
    input_path: Union[str, Path],
    output_dir: Union[str, Path],
    file_type: FileTypes,
    converter: str,
    ner_map: Optional[Path],
):
    input_path = Path(input_path)
    if file_type not in FILE_TYPES_STDOUT and output_dir == "-":
        msg.fail(
            f"Can't write .{file_type} data to stdout. Please specify an output directory.",
            exits=1,
        )
    if not input_path.exists():
        msg.fail("Input file not found", input_path, exits=1)
    if output_dir != "-" and not Path(output_dir).exists():
        msg.fail("Output directory not found", output_dir, exits=1)
    if ner_map is not None and not Path(ner_map).exists():
        msg.fail("NER map not found", ner_map, exits=1)
    if input_path.is_dir():
        input_locs = walk_directory(input_path, converter)
        if len(input_locs) == 0:
            msg.fail("No input files in directory", input_path, exits=1)
        file_types = list(set([loc.suffix[1:] for loc in input_locs]))
        if converter == "auto" and len(file_types) >= 2:
            file_types = ",".join(file_types)
            msg.fail("All input files must be same type", file_types, exits=1)
    if converter != "auto" and converter not in CONVERTERS:
        msg.fail(f"Can't find converter for {converter}", exits=1)


def _get_converter(msg, converter, input_path):
    if input_path.is_dir():
        input_path = walk_directory(input_path, converter)[0]
    if converter == "auto":
        converter = input_path.suffix[1:]
    if converter == "ner" or converter == "iob":
        with input_path.open(encoding="utf8") as file_:
            input_data = file_.read()
        converter_autodetect = autodetect_ner_format(input_data)
        if converter_autodetect == "ner":
            msg.info("Auto-detected token-per-line NER format")
            converter = converter_autodetect
        elif converter_autodetect == "iob":
            msg.info("Auto-detected sentence-per-line NER format")
            converter = converter_autodetect
        else:
            msg.warn(
                "Can't automatically detect NER format. "
                "Conversion may not succeed. "
                "See https://spacy.io/api/cli#convert"
            )
    return converter
