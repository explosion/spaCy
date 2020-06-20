from pathlib import Path
from wasabi import Printer
import srsly
import re
import sys

from ..tokens import DocBin
from ..gold.converters import iob2docs, conll_ner2docs, json2docs


# Converters are matched by file extension except for ner/iob, which are
# matched by file extension and content. To add a converter, add a new
# entry to this dict with the file extension mapped to the converter function
# imported from /converters.

CONVERTERS = {
    #"conllubio": conllu2docs, TODO
    #"conllu": conllu2docs, TODO
    #"conll": conllu2docs, TODO
    "ner": conll_ner2docs,
    "iob": iob2docs,
    "json": json2docs,
}


# File types
FILE_TYPES = ("json", "jsonl", "msg")
FILE_TYPES_STDOUT = ("json", "jsonl")


def convert(
    # fmt: off
    input_path: ("Input file or directory", "positional", None, Path),
    output_dir: ("Output directory.", "positional", None, Path),
    file_type: (f"Type of data to produce: {FILE_TYPES}", "option", "t", str, FILE_TYPES) = "spacy",
    n_sents: ("Number of sentences per doc (0 to disable)", "option", "n", int) = 1,
    seg_sents: ("Segment sentences (for -c ner)", "flag", "s") = False,
    model: ("Model for sentence segmentation (for -s)", "option", "b", str) = None,
    morphology: ("Enable appending morphology to tags", "flag", "m", bool) = False,
    merge_subtokens: ("Merge CoNLL-U subtokens", "flag", "T", bool) = False,
    converter: (f"Converter: {tuple(CONVERTERS.keys())}", "option", "c", str) = "auto",
    ner_map: ("NER tag mapping (as JSON-encoded dict of entity types)", "option", "N", Path) = None,
    lang: ("Language (if tokenizer required)", "option", "l", str) = None,
    # fmt: on
):
    """
    Convert files into json or DocBin format for use with train command and other
    experiment management functions.
    """
    cli_args = locals()
    no_print = output_dir == "-"
    output_dir = Path(output_dir) if output_dir != "-" else "-"
    msg = Printer(no_print=no_print)
    verify_cli_args(msg, **cli_args)
    converter = _get_converter(msg, converter, input_path)
    ner_map = srsly.read_json(ner_map) if ner_map is not None else None
    for input_loc in walk_directory(input_path):
        input_data = input_loc.open("r", encoding="utf-8").read()
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
            no_print=no_print,
            ner_map=ner_map,
        )
        suffix = f".{file_type}"
        subpath = input_loc.relative_to(input_path)
        output_file = (output_dir / subpath).with_suffix(suffix)
        if not output_file.parent.exists():
            output_file.parent.mkdir(parents=True)
        if file_type == "json":
            data = docs2json(docs)
            srsly.write_json(output_file, docs2json(docs))
        else:
            data = DocBin(docs=docs).to_bytes()
            with output_file.open("wb") as file_:
                file_.write(data)
        msg.good(f"Generated output file ({len(docs)} documents): {output_file}")


def autodetect_ner_format(input_data):
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


def walk_directory(path):
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
        else:
            locs.append(path)
    return locs


def verify_cli_args(
    msg,
    input_path,
    output_dir,
    file_type,
    n_sents,
    seg_sents,
    model,
    morphology,
    merge_subtokens,
    converter,
    ner_map,
    lang
):
    if converter == "ner" or converter == "iob":
        input_data = input_path.open("r", encoding="utf-8").read()
        converter_autodetect = autodetect_ner_format(input_data)
        if converter_autodetect == "ner":
            msg.info("Auto-detected token-per-line NER format")
            converter = converter_autodetect
        elif converter_autodetect == "iob":
            msg.info("Auto-detected sentence-per-line NER format")
            converter = converter_autodetect
        else:
            msg.warn(
                "Can't automatically detect NER format. Conversion may not",
                "succeed. See https://spacy.io/api/cli#convert"
            )
    if file_type not in FILE_TYPES_STDOUT and output_dir == "-":
        # TODO: support msgpack via stdout in srsly?
        msg.fail(
            f"Can't write .{file_type} data to stdout",
            "Please specify an output directory.",
            exits=1,
        )
    if not input_path.exists():
        msg.fail("Input file not found", input_path, exits=1)
    if output_dir != "-" and not Path(output_dir).exists():
        msg.fail("Output directory not found", output_dir, exits=1)
    if input_path.is_dir():
        input_locs = walk_directory(input_path)
        if len(input_locs) == 0:
            msg.fail("No input files in directory", input_path, exits=1)
        file_types = list(set([loc.suffix[1:] for loc in input_locs]))
        if len(file_types) >= 2:
            file_types = ",".join(file_types)
            msg.fail("All input files must be same type", file_types, exits=1)
        if converter == "auto":
            converter = file_types[0]
    else:
        converter = input_path.suffix[1:]
    if converter not in CONVERTERS:
        msg.fail(f"Can't find converter for {converter}", exits=1)
    return converter
 

def _get_converter(msg, converter, input_path):
    if input_path.is_dir():
        input_path = walk_directory(input_path)[0]
    if converter == "auto":
        converter = input_path.suffix[1:]
    if converter == "ner" or converter == "iob":
        with input_path.open() as file_:
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
