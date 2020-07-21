import pytest
import pickle
from spacy.morphology import Morphology
from spacy.strings import StringStore
from spacy.lemmatizer import Lemmatizer
from spacy.lookups import Lookups


@pytest.fixture
def morphology():
    tag_map = {"A": {"POS": "X"}, "B": {"POS": "NOUN"}}
    exc = {"A": {"a": {"POS": "VERB"}}}
    lemmatizer = Lemmatizer(Lookups())
    return Morphology(StringStore(), tag_map, lemmatizer, exc=exc)


def test_morphology_pickle_roundtrip(morphology):
    b = pickle.dumps(morphology)
    reloaded_morphology = pickle.loads(b)

    assert morphology.tag_map == reloaded_morphology.tag_map
    assert morphology.exc == reloaded_morphology.exc
