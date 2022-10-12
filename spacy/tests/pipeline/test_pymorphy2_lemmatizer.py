import pytest
import pickle
from spacy import util, registry
from spacy.lang.uk import Ukrainian
from spacy.lang.ru import Russian
from spacy.lookups import Lookups

from ..util import make_tempdir


def test_lookup_lemmatizer_uk():
    nlp = Ukrainian()
    lemmatizer = nlp.add_pipe("lemmatizer", config={"mode": "pymorphy2_lookup"})
    assert isinstance(lemmatizer.lookups, Lookups)
    assert not lemmatizer.lookups.tables
    assert lemmatizer.mode == "pymorphy2_lookup"
    nlp.initialize()
    assert nlp("якась")[0].lemma_ == "якийсь"
    assert nlp("якийсь")[0].lemma_ == "якийсь"
    assert nlp("зеленої")[0].lemma_ == 'зелений'
    assert nlp("розповідають")[0].lemma_ == 'розповідати'
    assert nlp("розповіси")[0].lemma_ == 'розповісти'
    # assert nlp("телятові")[0].lemma_ == 'теля' # pymorph2 fails

def test_lookup_lemmatizer_ru():
    nlp = Russian()
    lemmatizer = nlp.add_pipe("lemmatizer", config={"mode": "pymorphy2_lookup"})
    assert isinstance(lemmatizer.lookups, Lookups)
    assert not lemmatizer.lookups.tables
    assert lemmatizer.mode == "pymorphy2_lookup"
    nlp.initialize()
    assert nlp("бременем")[0].lemma_ == 'бремя'
    assert nlp("будешь")[0].lemma_ == "быть"
    # assert nlp("какая-то")[0].lemma_ == "какой-то" # fails due to faulty word splitting
    assert nlp("зелёной")[0].lemma_ == 'зелёный'
