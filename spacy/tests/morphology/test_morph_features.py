# coding: utf-8
from __future__ import unicode_literals

import pytest
from spacy.morphology import Morphology
from spacy.strings import StringStore, get_string_id
from spacy.lemmatizer import Lemmatizer
from spacy.lookups import Lookups


@pytest.fixture
def morphology():
    lemmatizer = Lemmatizer(Lookups())
    return Morphology(StringStore(), {}, lemmatizer)


def test_init(morphology):
    pass


def test_add_morphology_with_string_names(morphology):
    morphology.add({"Case_gen", "Number_sing"})


def test_add_morphology_with_int_ids(morphology):
    morphology.add({get_string_id("Case_gen"), get_string_id("Number_sing")})


def test_add_morphology_with_mix_strings_and_ints(morphology):
    morphology.add({get_string_id("PunctSide_ini"), "VerbType_aux"})


def test_morphology_tags_hash_distinctly(morphology):
    tag1 = morphology.add({"PunctSide_ini", "VerbType_aux"})
    tag2 = morphology.add({"Case_gen", "Number_sing"})
    assert tag1 != tag2


def test_morphology_tags_hash_independent_of_order(morphology):
    tag1 = morphology.add({"Case_gen", "Number_sing"})
    tag2 = morphology.add({"Number_sing", "Case_gen"})
    assert tag1 == tag2


def test_update_morphology_tag(morphology):
    tag1 = morphology.add({"Case_gen"})
    tag2 = morphology.update(tag1, {"Number_sing"})
    assert tag1 != tag2
    tag3 = morphology.add({"Number_sing", "Case_gen"})
    assert tag2 == tag3
