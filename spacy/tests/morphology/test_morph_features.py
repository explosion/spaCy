from __future__ import unicode_literals
import pytest

from ...morphology import Morphology
from ...strings import StringStore
from ...lemmatizer import Lemmatizer
from ...symbols import *

@pytest.fixture
def morphology():
    return Morphology(StringStore(), {}, Lemmatizer())

def test_init(morphology):
    pass

def test_add_tag_with_string_names(morphology):
    morphology.add({"Case_gen", "Number_Sing"})

def test_add_tag_with_int_ids(morphology):
    morphology.add({Case_gen, Number_sing})

def test_add_tag_with_mix_strings_and_ints(morphology):
    morphology.add({PunctSide_ini, 'VerbType_aux'})


