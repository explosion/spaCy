from pathlib import Path
from wasabi import Printer
import srsly
import re

from .converters import conllu2json, iob2json, conll_ner2json
from .converters import ner_jsonl2json


# Converters are matched by file extension except for ner/iob, which are
# matched by file extension and content. To add a converter, add a new
# entry to this dict with the file extension mapped to the converter function
# imported from /converters.
CONVERTERS = {
    "conllubio": conllu2json,
    "conllu": conllu2json,
    "conll": conllu2json,
    "ner": conll_ner2json,
    "iob": iob2json,
    "jsonl": ner_jsonl2json,
}

# File types
FILE_TYPES = ("json", "jsonl", "msg")
FILE_TYPES_STDOUT = ("json", "jsonl")


def convert(
    # fmt: off
    input_file: ("Input file", "positional", None, str),
    output_dir: ("Output directory. '-' for stdout.", "positional", None, str) = "-",
    file_type: (f"Type of data to produce: {FILE_TYPES}", "option", "t", str, FILE_TYPES) = "json",
    n_sents: ("Number of sentences per doc (0 to disable)", "option", "n", int) = 1,
    seg_sents: ("Segment sentences (for -c ner)", "flag", "s") = False,
    model: ("Model for sentence segmentation (for -s)", "option", "b", str) = None,
    morphology: ("Enable appending morphology to tags", "flag", "m", bool) = False,
    merge_subtokens: ("Merge CoNLL-U subtokens", "flag", "T", bool) = False,
    converter: (f"Converter: {tuple(CONVERTERS.keys())}", "option", "c", str) = "auto",
    ner_map_path: ("NER tag mapping (as JSON-encoded dict of entity types)", "option", "N", Path) = None,
    lang: ("Language (if tokenizer required)", "option", "l", str) = None,
    # fmt: on
):
    """
    Convert files into JSON format for use with train command and other
    experiment management functions. If no output_dir is specified, the data
    is written to stdout, so you can pipe them forward to a JSON file:
    $ spacy convert some_file.conllu > some_file.json
    """
    no_print = output_dir == "-"
    msg = Printer(no_print=no_print)
    input_path = Path(input_file)
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
    input_data = input_path.open("r", encoding="utf-8").read()
    if converter == "auto":
        converter = input_path.suffix[1:]
    if converter == "ner" or converter == "iob":
        converter_autodetect = autodetect_ner_format(input_data)
        if converter_autodetect == "ner":
            msg.info("Auto-detected token-per-line NER format")
            converter = converter_autodetect
        elif converter_autodetect == "iob":
            msg.info("Auto-detected sentence-per-line NER format")
            converter = converter_autodetect
        else:
            msg.warn(
                "Can't automatically detect NER format. Conversion may not succeed. See https://spacy.io/api/cli#convert"
            )
    if converter not in CONVERTERS:
        msg.fail(f"Can't find converter for {converter}", exits=1)
    ner_map = None
    if ner_map_path is not None:
        ner_map = srsly.read_json(ner_map_path)
    # Use converter function to convert data
    func = CONVERTERS[converter]
    data = func(
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
    if output_dir != "-":
        # Export data to a file
        suffix = f".{file_type}"
        output_file = Path(output_dir) / Path(input_path.parts[-1]).with_suffix(suffix)
        if file_type == "json":
            srsly.write_json(output_file, data)
        elif file_type == "jsonl":
            srsly.write_jsonl(output_file, data)
        elif file_type == "msg":
            srsly.write_msgpack(output_file, data)
        msg.good(f"Generated output file ({len(data)} documents): {output_file}")
    else:
        # Print to stdout
        if file_type == "json":
            srsly.write_json("-", data)
        elif file_type == "jsonl":
            srsly.write_jsonl("-", data)


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
