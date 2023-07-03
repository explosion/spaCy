import pytest

from spacy.morphology import Morphology
from spacy.strings import StringStore, get_string_id


@pytest.fixture
def morphology():
    return Morphology(StringStore())


def test_init(morphology):
    pass


def test_add_morphology_with_string_names(morphology):
    morphology.add({"Case": "gen", "Number": "sing"})


def test_add_morphology_with_int_ids(morphology):
    morphology.strings.add("Case")
    morphology.strings.add("gen")
    morphology.strings.add("Number")
    morphology.strings.add("sing")
    morphology.add(
        {
            get_string_id("Case"): get_string_id("gen"),
            get_string_id("Number"): get_string_id("sing"),
        }
    )


def test_add_morphology_with_mix_strings_and_ints(morphology):
    morphology.strings.add("PunctSide")
    morphology.strings.add("ini")
    morphology.add(
        {get_string_id("PunctSide"): get_string_id("ini"), "VerbType": "aux"}
    )


def test_morphology_tags_hash_distinctly(morphology):
    tag1 = morphology.add({"PunctSide": "ini", "VerbType": "aux"})
    tag2 = morphology.add({"Case": "gen", "Number": "sing"})
    assert tag1 != tag2


def test_morphology_tags_hash_independent_of_order(morphology):
    tag1 = morphology.add({"Case": "gen", "Number": "sing"})
    tag2 = morphology.add({"Number": "sing", "Case": "gen"})
    assert tag1 == tag2
