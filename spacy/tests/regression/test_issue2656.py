# coding: utf8
from __future__ import unicode_literals
from spacy.lang.en import English


def test_issue2656():
    """ Test that tokenizer correctly splits of punctuation after numbers with decimal points """
    text = "I went for 40.3, and got home by 10.0."
    nlp = English()
    doc = nlp(text)

    assert len(doc) == 11

    assert doc[0].text == "I"
    assert doc[1].text == "went"
    assert doc[2].text == "for"
    assert doc[3].text == "40.3"
    assert doc[4].text == ","
    assert doc[5].text == "and"
    assert doc[6].text == "got"
    assert doc[7].text == "home"
    assert doc[8].text == "by"
    assert doc[9].text == "10.0"
    assert doc[10].text == "."
