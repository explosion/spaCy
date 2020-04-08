# coding: utf8
from __future__ import unicode_literals

import numpy

from spacy.lang.en import English
from spacy.vocab import Vocab


def test_issue4725():
    # ensures that this runs correctly and doesn't hang or crash because of the global vectors
    vocab = Vocab(vectors_name="test_vocab_add_vector")
    data = numpy.ndarray((5, 3), dtype="f")
    data[0] = 1.0
    data[1] = 2.0
    vocab.set_vector("cat", data[0])
    vocab.set_vector("dog", data[1])

    nlp = English(vocab=vocab)
    ner = nlp.create_pipe("ner")
    nlp.add_pipe(ner)
    nlp.begin_training()
    docs = ["Kurt is in London."] * 10
    for _ in nlp.pipe(docs, batch_size=2, n_process=2):
        pass
