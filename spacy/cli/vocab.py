'''Compile a vocabulary from a lexicon jsonl file and word vectors.'''
# coding: utf8
from __future__ import unicode_literals

from pathlib import Path
import plac
import json
import spacy
import numpy
from spacy.util import ensure_path


@plac.annotations(
    lang=("model language", "positional", None, str),
    output_dir=("output directory to store model in", "positional", None, str),
    lexemes_loc=("location of JSONL-formatted lexical data", "positional",
                None, str),
    vectors_loc=("location of vectors data, as numpy .npz (optional)",
              "positional", None, str),
    version=("Model version", "option", "V", str),
    meta_path=("Optional path to meta.json. All relevant properties will be "
               "overwritten.", "option", "m", Path))

def make_vocab(lang, output_dir, lexemes_loc, vectors_loc=None):
    out_dir = ensure_path(output_dir)
    jsonl_loc = ensure_path(lexemes_loc)
    nlp = spacy.blank(lang)
    for word in nlp.vocab:
        word.rank = 0
    with jsonl_loc.open() as file_:
        for line in file_:
            if line.strip():
                attrs = json.loads(line)
                if 'settings' in attrs:
                    nlp.vocab.cfg.update(attrs['settings'])
                else:
                    lex = nlp.vocab[attrs['orth']]
                    lex.set_attrs(**attrs)
                    assert lex.rank == attrs['id']
    if vectors_loc is not None:
        vector_data = numpy.load(open(vectors_loc, 'rb'))
        nlp.vocab.clear_vectors(width=vector_data.shape[1])
        added = 0
        for word in nlp.vocab:
            if word.rank:
                nlp.vocab.vectors.add(word.orth_, row=word.rank,
                                      vector=vector_data[word.rank])
                added += 1
    nlp.to_disk(out_dir)
    return nlp
