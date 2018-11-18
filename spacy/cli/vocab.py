# coding: utf8
from __future__ import unicode_literals

import plac
import json
import spacy
import numpy
from pathlib import Path
from wasabi import Printer

from ._messages import Messages
from ..vectors import Vectors
from ..util import ensure_path


@plac.annotations(
    lang=("Model language", "positional", None, str),
    output_dir=("Model output directory", "positional", None, Path),
    lexemes_loc=("Location of JSONL-formatted lexical data", "positional", None, Path),
    vectors_loc=("Optional vectors path, as numpy .npz", "positional", None, str),
    prune_vectors=("Optional number of vectors to prune to", "option", "V", int),
)
def make_vocab(lang, output_dir, lexemes_loc, vectors_loc=None, prune_vectors=-1):
    """
    Compile a vocabulary from a lexicon jsonl file and word vectors.
    """
    msg = Printer()
    if not lexemes_loc.exists():
        msg.fail(Messages.M067, lexemes_loc, exits=1)
    vectors_loc = ensure_path(vectors_loc)
    nlp = spacy.blank(lang)
    for word in nlp.vocab:
        word.rank = 0
    lex_added = 0
    with lexemes_loc.open() as file_:
        for line in file_:
            if line.strip():
                attrs = json.loads(line)
                if "settings" in attrs:
                    nlp.vocab.cfg.update(attrs["settings"])
                else:
                    lex = nlp.vocab[attrs["orth"]]
                    lex.set_attrs(**attrs)
                    assert lex.rank == attrs["id"]
                lex_added += 1
    if vectors_loc is not None:
        vector_data = numpy.load(vectors_loc.open("rb"))
        nlp.vocab.vectors = Vectors(data=vector_data)
        for word in nlp.vocab:
            if word.rank:
                nlp.vocab.vectors.add(word.orth, row=word.rank)

    if prune_vectors >= 1:
        nlp.vocab.prune_vectors(prune_vectors)
    if not output_dir.exists():
        output_dir.mkdir()
    nlp.to_disk(output_dir)
    vec_added = len(nlp.vocab.vectors)
    msg.good(Messages.M068, Messages.M039.format(entries=lex_added, vectors=vec_added))
    msg.text(output_dir)
    return nlp
