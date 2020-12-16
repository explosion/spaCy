# coding: utf8
from __future__ import unicode_literals

from wasabi import Printer

from ...gold import iob_to_biluo
from ...util import minibatch
from .conll_ner2json import n_sents_info


def iob2json(input_data, n_sents=10, no_print=False, *args, **kwargs):
    """
    Convert IOB files with one sentence per line and tags separated with '|'
    into JSON format for use with train cli. IOB and IOB2 are accepted.

    Sample formats:

    I|O like|O London|I-GPE and|O New|B-GPE York|I-GPE City|I-GPE .|O
    I|O like|O London|B-GPE and|O New|B-GPE York|I-GPE City|I-GPE .|O
    I|PRP|O like|VBP|O London|NNP|I-GPE and|CC|O New|NNP|B-GPE York|NNP|I-GPE City|NNP|I-GPE .|.|O
    I|PRP|O like|VBP|O London|NNP|B-GPE and|CC|O New|NNP|B-GPE York|NNP|I-GPE City|NNP|I-GPE .|.|O
    """
    msg = Printer(no_print=no_print)
    docs = read_iob(input_data.split("\n"))
    if n_sents > 0:
        n_sents_info(msg, n_sents)
        docs = merge_sentences(docs, n_sents)
    return docs


def read_iob(raw_sents):
    sentences = []
    for line in raw_sents:
        if not line.strip():
            continue
        tokens = [t.split("|") for t in line.split()]
        if len(tokens[0]) == 3:
            words, pos, iob = zip(*tokens)
        elif len(tokens[0]) == 2:
            words, iob = zip(*tokens)
            pos = ["-"] * len(words)
        else:
            raise ValueError(
                "The sentence-per-line IOB/IOB2 file is not formatted correctly. Try checking whitespace and delimiters. See https://spacy.io/api/cli#convert"
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
    docs = [{"id": i, "paragraphs": [para]} for i, para in enumerate(paragraphs)]
    return docs


def merge_sentences(docs, n_sents):
    merged = []
    for group in minibatch(docs, size=n_sents):
        group = list(group)
        first = group.pop(0)
        to_extend = first["paragraphs"][0]["sentences"]
        for sent in group:
            to_extend.extend(sent["paragraphs"][0]["sentences"])
        merged.append(first)
    return merged
