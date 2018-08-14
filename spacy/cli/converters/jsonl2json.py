# coding: utf8
from __future__ import unicode_literals
import ujson as json

from .._messages import Messages
from ...compat import json_dumps, path2str
from ...util import prints, get_lang_class
from ...gold import docs_to_json


def ner_jsonl2json(input_path, output_path, lang=None, n_sents=10, use_morphology=False):
    if lang is None:
        prints(Messages.M054, exits=True)
    json_docs = []
    input_tuples = list(read_jsonl(input_path))
    nlp = get_lang_class(lang)()
    for i, (raw_text, ents) in enumerate(input_tuples):
        doc = nlp.make_doc(raw_text)
        doc[0].is_sent_start = True
        doc.ents = [doc.char_span(s, e, label=L) for s, e, L in ents['entities']]
        json_docs.append(docs_to_json(i, [doc]))

    output_filename = input_path.parts[-1].replace(".jsonl", ".json")
    output_loc = output_path / output_filename
    with (output_loc).open('w', encoding='utf8') as file_:
        file_.write(json_dumps(json_docs))
    prints(Messages.M033.format(n_docs=len(json_docs)),
           title=Messages.M032.format(name=path2str(output_loc)))

def read_jsonl(input_path):
    with input_path.open('r', encoding='utf8') as file_:
        for line in file_:
            yield json.loads(line)
