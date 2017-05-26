# coding: utf8
from __future__ import unicode_literals

from ...compat import json_dumps, path2str
from ...util import prints
from ...gold import iob_to_biluo


def iob2json(input_path, output_path, n_sents=10, *a, **k):
    """
    Convert IOB files into JSON format for use with train cli.
    """
    # TODO: This isn't complete yet -- need to map from IOB to
    # BILUO
    with input_path.open() as file_:
        docs = read_iob(file_)

    output_filename = input_path.parts[-1].replace(".iob", ".json")
    output_file = output_path / output_filename
    with output_file.open('w', encoding='utf-8') as f:
        f.write(json_dumps(docs))
    prints("Created %d documents" % len(docs),
           title="Generated output file %s" % path2str(output_file))


def read_iob(file_):
    sentences = []
    for line in file_:
        if not line.strip():
            continue
        tokens = [t.rsplit('|', 2) for t in line.split()]
        words, pos, iob = zip(*tokens)
        biluo = iob_to_biluo(iob)
        sentences.append([
            {'orth': w, 'tag': p, 'ner': ent}
            for (w, p, ent) in zip(words, pos, biluo)
        ])
    sentences = [{'tokens': sent} for sent in sentences]
    paragraphs = [{'sentences': [sent]} for sent in sentences]
    docs = [{'id': 0, 'paragraphs': [para]} for para in paragraphs]
    return docs
