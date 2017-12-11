# coding: utf-8
from __future__ import unicode_literals

import pytest
from ....tokens.doc import Doc


@pytest.fixture
def ru_lemmatizer(RU):
    return RU.Defaults.create_lemmatizer()


@pytest.mark.models('ru')
def test_doc_lemmatization(RU):
    doc = Doc(RU.vocab, words=['мама', 'мыла', 'раму'])
    doc[0].tag_ = 'NOUN__Animacy=Anim|Case=Nom|Gender=Fem|Number=Sing'
    doc[1].tag_ = 'VERB__Aspect=Imp|Gender=Fem|Mood=Ind|Number=Sing|Tense=Past|VerbForm=Fin|Voice=Act'
    doc[2].tag_ = 'NOUN__Animacy=Anim|Case=Acc|Gender=Fem|Number=Sing'

    lemmas = [token.lemma_ for token in doc]
    assert lemmas == ['мама', 'мыть', 'рама']


@pytest.mark.models('ru')
@pytest.mark.parametrize('text,lemmas', [('гвоздики', ['гвоздик', 'гвоздика']),
                                         ('люди', ['человек']),
                                         ('реки', ['река']),
                                         ('кольцо', ['кольцо']),
                                         ('пепперони', ['пепперони'])])
def test_ru_lemmatizer_noun_lemmas(ru_lemmatizer, text, lemmas):
    assert sorted(ru_lemmatizer.noun(text)) == lemmas


@pytest.mark.models('ru')
@pytest.mark.parametrize('text,pos,morphology,lemma', [('рой', 'NOUN', None, 'рой'),
                                                       ('рой', 'VERB', None, 'рыть'),
                                                       ('клей', 'NOUN', None, 'клей'),
                                                       ('клей', 'VERB', None, 'клеить'),
                                                       ('три', 'NUM', None, 'три'),
                                                       ('кос', 'NOUN', {'Number': 'Sing'}, 'кос'),
                                                       ('кос', 'NOUN', {'Number': 'Plur'}, 'коса'),
                                                       ('кос', 'ADJ', None, 'косой'),
                                                       ('потом', 'NOUN', None, 'пот'),
                                                       ('потом', 'ADV', None, 'потом')
                                                       ])
def test_ru_lemmatizer_works_with_different_pos_homonyms(ru_lemmatizer, text, pos, morphology, lemma):
    assert ru_lemmatizer(text, pos, morphology) == [lemma]


@pytest.mark.models('ru')
@pytest.mark.parametrize('text,morphology,lemma', [('гвоздики', {'Gender': 'Fem'}, 'гвоздика'),
                                                   ('гвоздики', {'Gender': 'Masc'}, 'гвоздик'),
                                                   ('вина', {'Gender': 'Fem'}, 'вина'),
                                                   ('вина', {'Gender': 'Neut'}, 'вино')
                                                   ])
def test_ru_lemmatizer_works_with_noun_homonyms(ru_lemmatizer, text, morphology, lemma):
    assert ru_lemmatizer.noun(text, morphology) == [lemma]


@pytest.mark.models('ru')
def test_ru_lemmatizer_punct(ru_lemmatizer):
    assert ru_lemmatizer.punct('«') == ['"']
    assert ru_lemmatizer.punct('»') == ['"']


# @pytest.mark.models('ru')
# def test_ru_lemmatizer_lemma_assignment(RU):
#     text = "А роза упала на лапу Азора."
#     doc = RU.make_doc(text)
#     RU.tagger(doc)
#     assert all(t.lemma_ != '' for t in doc)
