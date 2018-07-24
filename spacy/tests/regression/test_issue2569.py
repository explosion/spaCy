# coding: utf8
from __future__ import unicode_literals

from spacy.matcher import Matcher
from spacy.tokens import Span


def test_issue2569(en_tokenizer):
    doc = en_tokenizer("It is May 15, 1993.")
    doc.ents = [Span(doc, 2, 6, label=doc.vocab.strings['DATE'])]
    matcher = Matcher(doc.vocab)
    matcher.add("RULE", None, [{'ENT_TYPE':'DATE', 'OP':'+'}])
    matched = [doc[start:end] for _, start, end in matcher(doc)]
    matched = sorted(matched, key=len, reverse=True)
    assert len(matched) == 10
    assert len(matched[0]) == 4
    assert matched[0].text == 'May 15, 1993'
