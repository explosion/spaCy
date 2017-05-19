# coding: utf8
from __future__ import unicode_literals

from pathlib import Path

from .converters import conllu2json, iob2json
from ..util import prints


# Converters are matched by file extension. To add a converter, add a new entry
# to this dict with the file extension mapped to the converter function imported
# from /converters.

CONVERTERS = {
    '.conllu': conllu2json,
    '.conll': conllu2json,
    '.iob': iob2json
}


def convert(input_file, output_dir, *args):
    input_path = Path(input_file)
    output_path = Path(output_dir)
    if not input_path.exists():
        prints(input_path, title="Input file not found", exits=True)
    if not output_path.exists():
        prints(output_path, title="Output directory not found", exits=True)
    file_ext = input_path.suffix
    if not file_ext in CONVERTERS:
        prints("Can't find converter for %s" % input_path.parts[-1],
               title="Unknown format", exits=True)
    CONVERTERS[file_ext](input_path, output_path, *args)
