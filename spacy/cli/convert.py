# coding: utf8
from __future__ import unicode_literals

import plac
from pathlib import Path
from wasabi import Printer
import srsly

from .converters import conllu2json, iob2json, conll_ner2json
from .converters import ner_jsonl2json


# Converters are matched by file extension. To add a converter, add a new
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


@plac.annotations(
    input_file=("Input file", "positional", None, str),
    output_dir=("Output directory. '-' for stdout.", "positional", None, str),
    file_type=("Type of data to produce: {}".format(FILE_TYPES), "option", "t", str),
    n_sents=("Number of sentences per doc", "option", "n", int),
    converter=("Converter: {}".format(tuple(CONVERTERS.keys())), "option", "c", str),
    lang=("Language (if tokenizer required)", "option", "l", str),
    morphology=("Enable appending morphology to tags", "flag", "m", bool),
)
def convert(
    input_file,
    output_dir="-",
    file_type="json",
    n_sents=1,
    morphology=False,
    converter="auto",
    lang=None,
):
    """
    Convert files into JSON format for use with train command and other
    experiment management functions. If no output_dir is specified, the data
    is written to stdout, so you can pipe them forward to a JSON file:
    $ spacy convert some_file.conllu > some_file.json
    """
    msg = Printer()
    input_path = Path(input_file)
    if file_type not in FILE_TYPES:
        msg.fail(
            "Unknown file type: '{}'".format(file_type),
            "Supported file types: '{}'".format(", ".join(FILE_TYPES)),
            exits=1,
        )
    if file_type not in FILE_TYPES_STDOUT and output_dir == "-":
        # TODO: support msgpack via stdout in srsly?
        msg.fail(
            "Can't write .{} data to stdout.".format(file_type),
            "Please specify an output directory.",
            exits=1,
        )
    if not input_path.exists():
        msg.fail("Input file not found", input_path, exits=1)
    if output_dir != "-" and not Path(output_dir).exists():
        msg.fail("Output directory not found", output_dir, exits=1)
    if converter == "auto":
        converter = input_path.suffix[1:]
    if converter not in CONVERTERS:
        msg.fail("Can't find converter for {}".format(converter), exits=1)
    # Use converter function to convert data
    func = CONVERTERS[converter]
    input_data = input_path.open("r", encoding="utf-8").read()
    data = func(input_data, n_sents=n_sents, use_morphology=morphology, lang=lang)
    if output_dir != "-":
        # Export data to a file
        suffix = ".{}".format(file_type)
        output_file = Path(output_dir) / Path(input_path.parts[-1]).with_suffix(suffix)
        if file_type == "json":
            srsly.write_json(output_file, data)
        elif file_type == "jsonl":
            srsly.write_jsonl(output_file, data)
        elif file_type == "msg":
            srsly.write_msgpack(output_file, data)
        msg.good("Generated output file ({} documents)".format(len(data)), output_file)
    else:
        # Print to stdout
        if file_type == "json":
            srsly.write_json("-", data)
        elif file_type == "jsonl":
            srsly.write_jsonl("-", data)
