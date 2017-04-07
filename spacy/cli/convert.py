# coding: utf8
from __future__ import unicode_literals, division, print_function

import io
from pathlib import Path, PurePosixPath

from .converters import conllu2json
from .. import util


# Converters are matched by file extension. To add a converter, add a new entry
# to this dict with the file extension mapped to the converter function imported
# from /converters.

CONVERTERS = {
    '.conllu': conllu2json
}


def convert(input_file, output_dir, *args):
    input_path = Path(input_file)
    output_path = Path(output_dir)
    check_dirs(input_path, output_path)
    file_ext = input_path.suffix
    if file_ext in CONVERTERS:
        CONVERTERS[file_ext](input_path, output_path, *args)
    else:
        util.sys_exit("Can't find converter for {}".format(input_path.parts[-1]),
                      title="Unknown format")


def check_dirs(input_file, output_path):
    if not input_file.exists():
        util.sys_exit(input_file.as_posix(), title="Input file not found")
    if not output_path.exists():
        util.sys_exit(output_path.as_posix(), title="Output directory not found")
