# coding: utf8
from __future__ import unicode_literals

import re

from ...gold import iob_to_biluo
from ...util import minibatch


def iob2json(input_data, n_sents=10, *args, **kwargs):
    """
    Convert IOB files into JSON format for use with train cli.
    """
    sentences = read_iob(input_data.split("\n"))
    docs = merge_sentences(sentences, n_sents)
    return docs


def read_iob(raw_sents):
    sentences = []
    for line in raw_sents:
        if not line.strip():
            continue
        tokens = [re.split("[^\w\-]", line.strip())]
        if len(tokens[0]) == 3:
            words, pos, iob = zip(*tokens)
        elif len(tokens[0]) == 2:
            words, iob = zip(*tokens)
            pos = ["-"] * len(words)
        else:
            raise ValueError(
                "The iob/iob2 file is not formatted correctly. Try checking whitespace and delimiters."
            )
        biluo = iob_to_biluo(iob)
        sentences.append(
            [
                {"orth": w, "tag": p, "ner": ent}
                for (w, p, ent) in zip(words, pos, biluo)
            ]
        )
    sentences = [{"tokens": sent} for sent in sentences]
    paragraphs = [{"sentences": [sent]} for sent in sentences]
    docs = [{"id": 0, "paragraphs": [para]} for para in paragraphs]
    return docs


def merge_sentences(docs, n_sents):
    merged = []
    for group in minibatch(docs, size=n_sents):
        group = list(group)
        first = group.pop(0)
        to_extend = first["paragraphs"][0]["sentences"]
        for sent in group[1:]:
            to_extend.extend(sent["paragraphs"][0]["sentences"])
        merged.append(first)
    return merged
