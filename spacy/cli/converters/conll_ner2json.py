# coding: utf8
from __future__ import unicode_literals

from ...gold import iob_to_biluo


def conll_ner2json(input_data, **kwargs):
    """
    Convert files in the CoNLL-2003 NER format into JSON format for use with
    train cli.
    """
    delimit_docs = "-DOCSTART- -X- O O"
    output_docs = []
    for doc in input_data.strip().split(delimit_docs):
        doc = doc.strip()
        if not doc:
            continue
        output_doc = []
        for sent in doc.split("\n\n"):
            sent = sent.strip()
            if not sent:
                continue
            lines = [line.strip() for line in sent.split("\n") if line.strip()]
            words, tags, chunks, iob_ents = zip(*[line.split() for line in lines])
            biluo_ents = iob_to_biluo(iob_ents)
            output_doc.append(
                {
                    "tokens": [
                        {"orth": w, "tag": tag, "ner": ent}
                        for (w, tag, ent) in zip(words, tags, biluo_ents)
                    ]
                }
            )
        output_docs.append(
            {"id": len(output_docs), "paragraphs": [{"sentences": output_doc}]}
        )
        output_doc = []
    return output_docs
