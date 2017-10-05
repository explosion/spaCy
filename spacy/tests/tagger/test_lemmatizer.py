# coding: utf-8
from __future__ import unicode_literals

import pytest


@pytest.mark.models
@pytest.mark.parametrize('text,lemmas', [("aardwolves", ["aardwolf"]),
                                         ("aardwolf", ["aardwolf"]),
                                         ("planets", ["planet"]),
                                         ("ring", ["ring"]),
                                         ("axes", ["axis", "axe", "ax"])])
def test_tagger_lemmatizer_noun_lemmas(lemmatizer, text, lemmas):
    if lemmatizer is None:
        return None
    assert lemmatizer.noun(text) == set(lemmas)


@pytest.mark.xfail
@pytest.mark.models
def test_tagger_lemmatizer_base_forms(lemmatizer):
    if lemmatizer is None:
        return None
    assert lemmatizer.noun('dive', {'number': 'sing'}) == set(['dive'])
    assert lemmatizer.noun('dive', {'number': 'plur'}) == set(['diva'])


@pytest.mark.models
def test_tagger_lemmatizer_base_form_verb(lemmatizer):
    if lemmatizer is None:
        return None
    assert lemmatizer.verb('saw', {'verbform': 'past'}) == set(['see'])


@pytest.mark.models
def test_tagger_lemmatizer_punct(lemmatizer):
    if lemmatizer is None:
        return None
    assert lemmatizer.punct('“') == set(['"'])
    assert lemmatizer.punct('“') == set(['"'])


@pytest.mark.models
def test_tagger_lemmatizer_lemma_assignment(EN):
    text = "Bananas in pyjamas are geese."
    doc = EN.tokenizer(text)
    assert all(t.lemma_ == '' for t in doc)
    EN.tagger(doc)
    assert all(t.lemma_ != '' for t in doc)


from ...symbols import POS, VERB, VerbForm_part
from ...vocab import Vocab
from ...lemmatizer import Lemmatizer
from ..util import get_doc
def test_tagger_lemmatizer_exceptions():
    index = {"verb": ("cope","cop")}
    exc = {"verb": {"coping": ("cope",)}}
    rules = {"verb": [["ing", ""]]}
    tag_map = {'VBG': {POS: VERB, VerbForm_part: True}}
    lemmatizer = Lemmatizer(index, exc, rules)
    vocab = Vocab(lemmatizer=lemmatizer, tag_map=tag_map)
    doc = get_doc(vocab, ["coping"])
    doc[0].tag_ = 'VBG'
    assert doc[0].text == "coping"
    assert doc[0].lemma_ == "cope"
