# coding: utf8
from __future__ import unicode_literals

import pytest
import random
import numpy.random
from spacy.language import Language
from spacy.pipeline import TextCategorizer
from spacy.tokens import Doc
from spacy.gold import GoldParse


@pytest.mark.skip(reason="Test is flakey when run with others")
def test_simple_train():
    nlp = Language()
    nlp.add_pipe(nlp.create_pipe("textcat"))
    nlp.get_pipe("textcat").add_label("answer")
    nlp.begin_training()
    for i in range(5):
        for text, answer in [
            ("aaaa", 1.0),
            ("bbbb", 0),
            ("aa", 1.0),
            ("bbbbbbbbb", 0.0),
            ("aaaaaa", 1),
        ]:
            nlp.update([text], [{"cats": {"answer": answer}}])
    doc = nlp("aaa")
    assert "answer" in doc.cats
    assert doc.cats["answer"] >= 0.5


@pytest.mark.skip(reason="Test is flakey when run with others")
def test_textcat_learns_multilabel():
    random.seed(5)
    numpy.random.seed(5)
    docs = []
    nlp = Language()
    letters = ["a", "b", "c"]
    for w1 in letters:
        for w2 in letters:
            cats = {letter: float(w2 == letter) for letter in letters}
            docs.append((Doc(nlp.vocab, words=["d"] * 3 + [w1, w2] + ["d"] * 3), cats))
    random.shuffle(docs)
    model = TextCategorizer(nlp.vocab, width=8)
    for letter in letters:
        model.add_label(letter)
    optimizer = model.begin_training()
    for i in range(30):
        losses = {}
        Ys = [GoldParse(doc, cats=cats) for doc, cats in docs]
        Xs = [doc for doc, cats in docs]
        model.update(Xs, Ys, sgd=optimizer, losses=losses)
        random.shuffle(docs)
    for w1 in letters:
        for w2 in letters:
            doc = Doc(nlp.vocab, words=["d"] * 3 + [w1, w2] + ["d"] * 3)
            truth = {letter: w2 == letter for letter in letters}
            model(doc)
            for cat, score in doc.cats.items():
                if not truth[cat]:
                    assert score < 0.5
                else:
                    assert score > 0.5


def test_label_types():
    nlp = Language()
    nlp.add_pipe(nlp.create_pipe("textcat"))
    nlp.get_pipe("textcat").add_label("answer")
    with pytest.raises(ValueError):
        nlp.get_pipe("textcat").add_label(9)
