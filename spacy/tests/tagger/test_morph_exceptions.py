# coding: utf-8
from __future__ import unicode_literals

from ..util import get_doc

import pytest


def test_tagger_load_morph_exc(en_tokenizer):
    text = "I like his style."
    tags = ['PRP', 'VBP', 'PRP$', 'NN', '.']
    morph_exc = {'PRP$': {'his': {'L': '-PRP-', 'person': 3, 'case': 2}}}
    en_tokenizer.vocab.morphology.load_morph_exceptions(morph_exc)
    tokens = en_tokenizer(text)
    doc = get_doc(tokens.vocab, [t.text for t in tokens], tags=tags)
    assert doc[2].tag_ == 'PRP$'
    assert doc[2].lemma_ == '-PRP-'
