# coding: utf8
from __future__ import unicode_literals

from .._messages import Messages
from ...compat import json_dumps, path2str
from ...util import prints
from ...gold import iob_to_biluo


def conll_ner2json(input_path, output_path, n_sents=10, use_morphology=False):
    """
    Convert files in the CoNLL-2003 NER format into JSON format for use with
    train cli.
    """
    docs = read_conll_ner(input_path)

    output_filename = input_path.parts[-1].replace(".conll", "") + ".json"
    output_filename = input_path.parts[-1].replace(".conll", "") + ".json"
    output_file = output_path / output_filename
    with output_file.open('w', encoding='utf-8') as f:
        f.write(json_dumps(docs))
    prints(Messages.M033.format(n_docs=len(docs)),
           title=Messages.M032.format(name=path2str(output_file)))


def read_conll_ner(input_path):
    text = input_path.open('r', encoding='utf-8').read()
    i = 0
    delimit_docs = '-DOCSTART- -X- O O'
    output_docs = []
    for doc in text.strip().split(delimit_docs):
        doc = doc.strip()
        if not doc:
            continue
        output_doc = []
        for sent in doc.split('\n\n'):
            sent = sent.strip()
            if not sent:
                continue
            lines = [line.strip() for line in sent.split('\n') if line.strip()]
            words, tags, chunks, iob_ents = zip(*[line.split() for line in lines])
            biluo_ents = iob_to_biluo(iob_ents)
            output_doc.append({'tokens': [
                {'orth': w, 'tag': tag, 'ner': ent} for (w, tag, ent) in
                zip(words, tags, biluo_ents)
            ]})
        output_docs.append({
            'id': len(output_docs),
            'paragraphs': [{'sentences': output_doc}]
        })
        output_doc = []
    return output_docs
