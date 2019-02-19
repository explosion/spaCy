# coding: utf8
from __future__ import unicode_literals
from spacy.lang.it import Italian


def test_issue2822():
    """ Test that the abbreviation of poco is kept as one word """
    nlp = Italian()
    text = "Vuoi un po' di zucchero?"

    doc = nlp(text)

    assert len(doc) == 6

    assert doc[0].text == "Vuoi"
    assert doc[1].text == "un"
    assert doc[2].text == "po'"
    assert doc[2].lemma_ == "poco"
    assert doc[3].text == "di"
    assert doc[4].text == "zucchero"
    assert doc[5].text == "?"
