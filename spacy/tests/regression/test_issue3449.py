# coding: utf8
from __future__ import unicode_literals

import pytest

from spacy.lang.en import English


@pytest.mark.xfail(reason="default suffix rules avoid one upper-case letter before dot")
def test_issue3449():
    nlp = English()
    nlp.add_pipe(nlp.create_pipe("sentencizer"))
    text1 = "He gave the ball to I. Do you want to go to the movies with I?"
    text2 = "He gave the ball to I.  Do you want to go to the movies with I?"
    text3 = "He gave the ball to I.\nDo you want to go to the movies with I?"
    t1 = nlp(text1)
    t2 = nlp(text2)
    t3 = nlp(text3)
    assert t1[5].text == "I"
    assert t2[5].text == "I"
    assert t3[5].text == "I"
