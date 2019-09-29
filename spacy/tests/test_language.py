# coding: utf-8
from __future__ import unicode_literals

import pytest
from spacy.vocab import Vocab
from spacy.language import Language
from spacy.tokens import Doc
from spacy.gold import GoldParse


@pytest.fixture
def nlp():
    nlp = Language(Vocab())
    textcat = nlp.create_pipe("textcat")
    for label in ("POSITIVE", "NEGATIVE"):
        textcat.add_label(label)
    nlp.add_pipe(textcat)
    nlp.begin_training()
    return nlp


def test_language_update(nlp):
    text = "hello world"
    annots = {"cats": {"POSITIVE": 1.0, "NEGATIVE": 0.0}}
    wrongkeyannots = {"LABEL": True}
    doc = Doc(nlp.vocab, words=text.split(" "))
    gold = GoldParse(doc, **annots)
    # Update with doc and gold objects
    nlp.update([doc], [gold])
    # Update with text and dict
    nlp.update([text], [annots])
    # Update with doc object and dict
    nlp.update([doc], [annots])
    # Update with text and gold object
    nlp.update([text], [gold])
    # Update badly
    with pytest.raises(IndexError):
        nlp.update([doc], [])
    with pytest.raises(IndexError):
        nlp.update([], [gold])
    with pytest.raises(ValueError):
        nlp.update([text], [wrongkeyannots])


def test_language_evaluate(nlp):
    text = "hello world"
    annots = {"cats": {"POSITIVE": 1.0, "NEGATIVE": 0.0}}
    doc = Doc(nlp.vocab, words=text.split(" "))
    gold = GoldParse(doc, **annots)
    # Evaluate with doc and gold objects
    nlp.evaluate([(doc, gold)])
    # Evaluate with text and dict
    nlp.evaluate([(text, annots)])
    # Evaluate with doc object and dict
    nlp.evaluate([(doc, annots)])
    # Evaluate with text and gold object
    nlp.evaluate([(text, gold)])
    # Evaluate badly
    with pytest.raises(Exception):
        nlp.evaluate([text, gold])
