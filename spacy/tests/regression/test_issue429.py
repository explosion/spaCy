# coding: utf-8
from __future__ import unicode_literals

from ...attrs import ORTH
from ...matcher import Matcher

import pytest


@pytest.mark.models
def test_issue429(EN):
    def merge_phrases(matcher, doc, i, matches):
      if i != len(matches) - 1:
        return None
      spans = [(ent_id, label, doc[start:end]) for ent_id, label, start, end in matches]
      for ent_id, label, span in spans:
        span.merge('NNP' if label else span.root.tag_, span.text, EN.vocab.strings[label])

    doc = EN('a')
    matcher = Matcher(EN.vocab)
    matcher.add('key', label='TEST', attrs={}, specs=[[{ORTH: 'a'}]], on_match=merge_phrases)
    doc = EN.tokenizer('a b c')
    EN.tagger(doc)
    matcher(doc)
    EN.entity(doc)
