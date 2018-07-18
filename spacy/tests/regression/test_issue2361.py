# coding: utf8
from __future__ import unicode_literals

import pytest
from spacy.displacy import render
from spacy.tokens import Doc


def test_issue2361(de_tokenizer):
    chars = ('&lt;', '&gt;', '&amp;', '&quot;')
    tokens = de_tokenizer('< > & " ')
    html = render(Doc(tokens.vocab, words=[t.text for t in tokens]))
    for char in chars:
        assert char in html
