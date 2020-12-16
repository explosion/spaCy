# coding: utf8
from __future__ import unicode_literals

from spacy.lang.en import English


def test_issue5152():
    # Test that the comparison between a Span and a Token, goes well
    # There was a bug when the number of tokens in the span equaled the number of characters in the token (!)
    nlp = English()
    text = nlp("Talk about being boring!")
    text_var = nlp("Talk of being boring!")
    y = nlp("Let")

    span = text[0:3]  # Talk about being
    span_2 = text[0:3]  # Talk about being
    span_3 = text_var[0:3]  # Talk of being
    token = y[0]  # Let
    assert span.similarity(token) == 0.0
    assert span.similarity(span_2) == 1.0
    assert span_2.similarity(span_3) < 1.0
