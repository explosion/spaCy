# coding: utf-8
from __future__ import unicode_literals

import pytest


# Calling the Lemmatizer directly
# Imitates behavior of:
# Tagger.set_annotations()
# -> vocab.morphology.assign_tag_id()
# -> vocab.morphology.assign_tag_id()
#   -> Token.tag.__set__
#     -> vocab.morphology.assign_tag(...)
#       -> ... ->  Morphology.assign_tag(...)
#         -> self.lemmatize(analysis.tag.pos, token.lex.orth,


noun_irreg_lemmatization_cases = [
    ("volkeren", "volk"),
    ("vaatje", "vat"),
    ("verboden", "verbod"),
    ("ijsje", "ijsje"),
    ("slagen", "slag"),
    ("verdragen", "verdrag"),
    ("verloven", "verlof"),
    ("gebeden", "gebed"),
    ("gaten", "gat"),
    ("staven", "staf"),
    ("aquariums", "aquarium"),
    ("podia", "podium"),
    ("holen", "hol"),
    ("lammeren", "lam"),
    ("bevelen", "bevel"),
    ("wegen", "weg"),
    ("moeilijkheden", "moeilijkheid"),
    ("aanwezigheden", "aanwezigheid"),
    ("goden", "god"),
    ("loten", "lot"),
    ("kaarsen", "kaars"),
    ("leden", "lid"),
    ("glaasje", "glas"),
    ("eieren", "ei"),
    ("vatten", "vat"),
    ("kalveren", "kalf"),
    ("padden", "pad"),
    ("smeden", "smid"),
    ("genen", "gen"),
    ("beenderen", "been"),
]


verb_irreg_lemmatization_cases = [
    ("liep", "lopen"),
    ("hief", "heffen"),
    ("begon", "beginnen"),
    ("sla", "slaan"),
    ("aangekomen", "aankomen"),
    ("sproot", "spruiten"),
    ("waart", "zijn"),
    ("snoof", "snuiven"),
    ("spoot", "spuiten"),
    ("ontbeet", "ontbijten"),
    ("gehouwen", "houwen"),
    ("afgewassen", "afwassen"),
    ("deed", "doen"),
    ("schoven", "schuiven"),
    ("gelogen", "liegen"),
    ("woog", "wegen"),
    ("gebraden", "braden"),
    ("smolten", "smelten"),
    ("riep", "roepen"),
    ("aangedaan", "aandoen"),
    ("vermeden", "vermijden"),
    ("stootten", "stoten"),
    ("ging", "gaan"),
    ("geschoren", "scheren"),
    ("gesponnen", "spinnen"),
    ("reden", "rijden"),
    ("zochten", "zoeken"),
    ("leed", "lijden"),
    ("verzonnen", "verzinnen"),
]


@pytest.mark.parametrize("text,lemma", noun_irreg_lemmatization_cases)
def test_nl_lemmatizer_noun_lemmas_irreg(nl_lemmatizer, text, lemma):
    pos = "noun"
    lemmas_pred = nl_lemmatizer(text, pos)
    assert lemma == sorted(lemmas_pred)[0]


@pytest.mark.parametrize("text,lemma", verb_irreg_lemmatization_cases)
def test_nl_lemmatizer_verb_lemmas_irreg(nl_lemmatizer, text, lemma):
    pos = "verb"
    lemmas_pred = nl_lemmatizer(text, pos)
    assert lemma == sorted(lemmas_pred)[0]


@pytest.mark.skip
@pytest.mark.parametrize("text,lemma", [])
def test_nl_lemmatizer_verb_lemmas_reg(nl_lemmatizer, text, lemma):
    # TODO: add test
    pass


@pytest.mark.skip
@pytest.mark.parametrize("text,lemma", [])
def test_nl_lemmatizer_adjective_lemmas(nl_lemmatizer, text, lemma):
    # TODO: add test
    pass


@pytest.mark.skip
@pytest.mark.parametrize("text,lemma", [])
def test_nl_lemmatizer_determiner_lemmas(nl_lemmatizer, text, lemma):
    # TODO: add test
    pass


@pytest.mark.skip
@pytest.mark.parametrize("text,lemma", [])
def test_nl_lemmatizer_adverb_lemmas(nl_lemmatizer, text, lemma):
    # TODO: add test
    pass


@pytest.mark.parametrize("text,lemma", [])
def test_nl_lemmatizer_pronoun_lemmas(nl_lemmatizer, text, lemma):
    # TODO: add test
    pass


# Using the lemma lookup table only
@pytest.mark.parametrize("text,lemma", noun_irreg_lemmatization_cases)
def test_nl_lemmatizer_lookup_noun(nl_lemmatizer, text, lemma):
    lemma_pred = nl_lemmatizer.lookup(text)
    assert lemma_pred in (lemma, text)


@pytest.mark.parametrize("text,lemma", verb_irreg_lemmatization_cases)
def test_nl_lemmatizer_lookup_verb(nl_lemmatizer, text, lemma):
    lemma_pred = nl_lemmatizer.lookup(text)
    assert lemma_pred in (lemma, text)
