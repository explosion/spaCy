# coding: utf8
from __future__ import unicode_literals

import pytest
from spacy.displacy import render
from spacy.tokens import Doc


def test_issue2361(de_tokenizer):
    chars = ('&lt;', '&gt;', '&amp;', '&quot;')
    doc = de_tokenizer('< > & " ')
    doc.is_parsed = True
    doc.is_tagged = True
    html = render(doc)
    for char in chars:
        assert char in html
