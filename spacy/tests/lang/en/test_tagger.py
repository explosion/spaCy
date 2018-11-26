# coding: utf-8
from __future__ import unicode_literals

from ...util import get_doc


def test_en_tagger_load_morph_exc(en_tokenizer):
    text = "I like his style."
    tags = ["PRP", "VBP", "PRP$", "NN", "."]
    morph_exc = {"VBP": {"like": {"lemma": "luck"}}}
    en_tokenizer.vocab.morphology.load_morph_exceptions(morph_exc)
    tokens = en_tokenizer(text)
    doc = get_doc(tokens.vocab, words=[t.text for t in tokens], tags=tags)
    assert doc[1].tag_ == "VBP"
    assert doc[1].lemma_ == "luck"
