# coding: utf8
from __future__ import unicode_literals

import plac
from pathlib import Path
from wasabi import Printer

from ..util import write_jsonl, write_json
from ..compat import json_dumps, path2str
from .converters import conllu2json, conllubio2json, iob2json, conll_ner2json
from .converters import ner_jsonl2json
from ._messages import Messages


# Converters are matched by file extension. To add a converter, add a new
# entry to this dict with the file extension mapped to the converter function
# imported from /converters.
CONVERTERS = {
    "conllubio": conllubio2json,
    "conllu": conllu2json,
    "conll": conllu2json,
    "ner": conll_ner2json,
    "iob": iob2json,
    "jsonl": ner_jsonl2json,
}

# File types
FILE_TYPES = ("json", "jsonl")


@plac.annotations(
    input_file=("Input file", "positional", None, str),
    output_dir=("Output directory for converted file", "positional", None, str),
    file_type=("Type of data to produce: 'jsonl' or 'json'", "option", "t", str),
    n_sents=("Number of sentences per doc", "option", "n", int),
    converter=("Name of converter (auto, iob, conllu or ner)", "option", "c", str),
    lang=("Language (if tokenizer required)", "option", "l", str),
    morphology=("Enable appending morphology to tags", "flag", "m", bool),
)
def convert(
    input_file,
    output_dir="-",
    file_type="jsonl",
    n_sents=1,
    morphology=False,
    converter="auto",
    lang=None,
):
    """
    Convert files into JSON format for use with train command and other
    experiment management functions. If no output_dir is specified, the data
    is written to stdout, so you can pipe them forward to a JSONL file:
    $ spacy convert some_file.conllu > some_file.jsonl
    """
    msg = Printer()
    input_path = Path(input_file)
    if file_type not in FILE_TYPES:
        msg.fail(
            Messages.M069.format(name=file_type),
            Messages.M070.format(options=", ".join(FILE_TYPES)),
            exits=1,
        )
    if not input_path.exists():
        msg.fail(Messages.M028, input_path, exits=1)
    if output_dir != "-" and not Path(output_dir).exists():
        msg.fail(Messages.M029, output_dir, exits=1)
    if converter == "auto":
        converter = input_path.suffix[1:]
    if converter not in CONVERTERS:
        msg.fail(Messages.M030, Messages.M031.format(converter=converter), exits=1)
    # Use converter function to convert data
    func = CONVERTERS[converter]
    input_data = input_path.open("r", encoding="utf-8").read()
    data = func(input_data, nsents=n_sents, use_morphology=morphology, lang=lang)
    if output_dir != "-":
        # Export data to a file
        suffix = ".{}".format(file_type)
        output_file = Path(output_dir) / Path(input_path.parts[-1]).with_suffix(suffix)
        if file_type == "json":
            write_json(output_file, data)
        elif file_type == "jsonl":
            write_jsonl(output_file, data)
        msg.good(
            Messages.M032.format(name=path2str(output_file)),
            Messages.M033.format(n_docs=len(data)),
        )
    else:
        # Print to stdout
        if file_type == "json":
            print(json_dumps(data))
        elif file_type == "jsonl":
            for line in data:
                print(json_dumps(line))
