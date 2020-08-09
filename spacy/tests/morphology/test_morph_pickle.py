import pytest
import pickle
from spacy.morphology import Morphology
from spacy.strings import StringStore


@pytest.fixture
def morphology():
    morphology = Morphology(StringStore())
    morphology.add("Feat1=Val1|Feat2=Val2")
    morphology.add("Feat3=Val3|Feat4=Val4")
    return morphology


def test_morphology_pickle_roundtrip(morphology):
    b = pickle.dumps(morphology)
    reloaded_morphology = pickle.loads(b)
    feat = reloaded_morphology.get(morphology.strings["Feat1=Val1|Feat2=Val2"])
    assert feat == "Feat1=Val1|Feat2=Val2"
    feat = reloaded_morphology.get(morphology.strings["Feat3=Val3|Feat4=Val4"])
    assert feat == "Feat3=Val3|Feat4=Val4"
