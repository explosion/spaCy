from __future__ import unicode_literals
import random
import numpy.random

from ..pipeline import TextCategorizer
from ..lang.en import English
from ..vocab import Vocab
from ..tokens import Doc
from ..gold import GoldParse


def test_textcat_learns_multilabel():
    random.seed(0)
    numpy.random.seed(0)
    docs = []
    nlp = English()
    vocab = nlp.vocab
    letters = ['a', 'b', 'c']
    for w1 in letters:
        for w2 in letters:
            cats = {letter: float(w2==letter) for letter in letters}
            docs.append((Doc(vocab, words=['d']*3 + [w1, w2] + ['d']*3), cats))
    random.shuffle(docs)
    model = TextCategorizer(vocab, width=8)
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
            doc = Doc(vocab, words=['d']*3 + [w1, w2] + ['d']*3)
            truth = {letter: w2==letter for letter in letters}
            model(doc)
            for cat, score in doc.cats.items():
                if not truth[cat]:
                    assert score < 0.5
                else:
                    assert score > 0.5

