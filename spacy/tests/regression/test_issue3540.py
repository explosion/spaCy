# coding: utf8
from __future__ import unicode_literals

from spacy.tokens import Doc

import numpy as np


def test_issue3540(en_vocab):

    words = ["I", "live", "in", "NewYork", "right", "now"]
    tensor = np.asarray(
        [[1.0, 1.1], [2.0, 2.1], [3.0, 3.1], [4.0, 4.1], [5.0, 5.1], [6.0, 6.1]],
        dtype="f",
    )
    doc = Doc(en_vocab, words=words)
    doc.tensor = tensor

    gold_text = ["I", "live", "in", "NewYork", "right", "now"]
    assert [token.text for token in doc] == gold_text

    gold_lemma = ["I", "live", "in", "NewYork", "right", "now"]
    assert [token.lemma_ for token in doc] == gold_lemma

    vectors_1 = [token.vector for token in doc]
    assert len(vectors_1) == len(doc)

    with doc.retokenize() as retokenizer:
        heads = [(doc[3], 1), doc[2]]
        attrs = {"POS": ["PROPN", "PROPN"], "DEP": ["pobj", "compound"]}
        retokenizer.split(doc[3], ["New", "York"], heads=heads, attrs=attrs)

    gold_text = ["I", "live", "in", "New", "York", "right", "now"]
    assert [token.text for token in doc] == gold_text

    gold_lemma = ["I", "live", "in", "New", "York", "right", "now"]
    assert [token.lemma_ for token in doc] == gold_lemma

    vectors_2 = [token.vector for token in doc]
    assert len(vectors_2) == len(doc)

    assert vectors_1[0].tolist() == vectors_2[0].tolist()
    assert vectors_1[1].tolist() == vectors_2[1].tolist()
    assert vectors_1[2].tolist() == vectors_2[2].tolist()

    assert vectors_1[4].tolist() == vectors_2[5].tolist()
    assert vectors_1[5].tolist() == vectors_2[6].tolist()
