# coding: utf8
from __future__ import unicode_literals

import plac
from pathlib import Path

from .converters import conllu2json, conllubio2json, iob2json, conll_ner2json
from ._messages import Messages
from ..util import prints

# Converters are matched by file extension. To add a converter, add a new
# entry to this dict with the file extension mapped to the converter function
# imported from /converters.
CONVERTERS = {
    'conllubio': conllubio2json,
    'conllu': conllu2json,
    'conll': conllu2json,
    'ner': conll_ner2json,
    'iob': iob2json,
}


@plac.annotations(
    input_file=("input file", "positional", None, str),
    output_dir=("output directory for converted file", "positional", None, str),
    n_sents=("Number of sentences per doc", "option", "n", int),
    converter=("Name of converter (auto, iob, conllu or ner)", "option", "c", str),
    morphology=("Enable appending morphology to tags", "flag", "m", bool))
def convert(input_file, output_dir, n_sents=1, morphology=False, converter='auto'):
    """
    Convert files into JSON format for use with train command and other
    experiment management functions.
    """
    input_path = Path(input_file)
    output_path = Path(output_dir)
    if not input_path.exists():
        prints(input_path, title=Messages.M028, exits=1)
    if not output_path.exists():
        prints(output_path, title=Messages.M029, exits=1)
    if converter == 'auto':
        converter = input_path.suffix[1:]
    if converter not in CONVERTERS:
            prints(Messages.M031.format(converter=converter),
                   title=Messages.M030, exits=1)
    func = CONVERTERS[converter]
    func(input_path, output_path,
         n_sents=n_sents, use_morphology=morphology)
