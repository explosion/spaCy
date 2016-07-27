import pytest

import pickle
import io


from spacy.morphology import Morphology
from spacy.lemmatizer import Lemmatizer
from spacy.strings import StringStore

@pytest.mark.xfail
def test_pickle():
    morphology = Morphology(StringStore(), {}, Lemmatizer({}, {}, {})) 

    file_ = io.BytesIO()
    pickle.dump(morphology, file_)

