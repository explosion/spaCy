import pytest

import pickle
import StringIO


from spacy.morphology import Morphology
from spacy.lemmatizer import Lemmatizer
from spacy.strings import StringStore


def test_pickle():
    morphology = Morphology(StringStore(), {}, Lemmatizer({}, {}, {})) 

    file_ = StringIO.StringIO()
    pickle.dump(morphology, file_)

