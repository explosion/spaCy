# coding: utf-8
from __future__ import unicode_literals

from ...matcher import Matcher

import pytest


@pytest.mark.models('en')
def test_issue429(EN):
    def merge_phrases(matcher, doc, i, matches):
        if i != len(matches) - 1:
            return None
        spans = [(ent_id, ent_id, doc[start:end]) for ent_id, start, end in matches]
        for ent_id, label, span in spans:
            span.merge(
                tag=('NNP' if label else span.root.tag_),
                lemma=span.text,
                label='PERSON')

    doc = EN('a')
    matcher = Matcher(EN.vocab)
    matcher.add('TEST', merge_phrases, [{'ORTH': 'a'}])
    doc = EN.make_doc('a b c')
    EN.tagger(doc)
    matcher(doc)
    EN.entity(doc)
