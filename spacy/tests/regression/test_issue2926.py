# coding: utf8
from __future__ import unicode_literals
from spacy.lang.fr import French


def test_issue2926():
    """ Test that the tokenizer correctly splits tokens separated by a slash (/) ending in a digit """
    nlp = French()
    text = "Learn html5/css3/javascript/jquery"
    doc = nlp(text)

    assert len(doc) == 8

    assert doc[0].text == "Learn"
    assert doc[1].text == "html5"
    assert doc[2].text == "/"
    assert doc[3].text == "css3"
    assert doc[4].text == "/"
    assert doc[5].text == "javascript"
    assert doc[6].text == "/"
    assert doc[7].text == "jquery"
