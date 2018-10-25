# coding: utf8
from __future__ import unicode_literals
from cytoolz import partition_all, concat

from .._messages import Messages
from ...compat import json_dumps, path2str
from ...util import prints
from ...gold import iob_to_biluo


def iob2json(input_path, output_path, n_sents=10, *a, **k):
    """
    Convert IOB files into JSON format for use with train cli.
    """
    with input_path.open('r', encoding='utf8') as file_:
        sentences = read_iob(file_)
    docs = merge_sentences(sentences, n_sents)
    output_filename = input_path.parts[-1].replace(".iob", ".json")
    output_file = output_path / output_filename
    with output_file.open('w', encoding='utf-8') as f:
        f.write(json_dumps(docs))
    prints(Messages.M033.format(n_docs=len(docs)),
           title=Messages.M032.format(name=path2str(output_file)))


def read_iob(raw_sents):
    sentences = []
    for line in raw_sents:
        if not line.strip():
            continue
        tokens = [t.split('|') for t in line.split()]
        if len(tokens[0]) == 3:
            words, pos, iob = zip(*tokens)
        else:
            words, iob = zip(*tokens)
            pos = ['-'] * len(words)
        biluo = iob_to_biluo(iob)
        sentences.append([
            {'orth': w, 'tag': p, 'ner': ent}
            for (w, p, ent) in zip(words, pos, biluo)
        ])
    sentences = [{'tokens': sent} for sent in sentences]
    paragraphs = [{'sentences': [sent]} for sent in sentences]
    docs = [{'id': 0, 'paragraphs': [para]} for para in paragraphs]
    return docs

def merge_sentences(docs, n_sents):
    counter = 0
    merged = []
    for group in partition_all(n_sents, docs):
        group = list(group)
        first = group.pop(0)
        to_extend = first['paragraphs'][0]['sentences']
        for sent in group[1:]:
            to_extend.extend(sent['paragraphs'][0]['sentences'])
        merged.append(first)
    return merged
