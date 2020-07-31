import pytest

from spacy import util
from spacy.lang.en import English
from spacy.lookups import Lookups

from ..util import make_tempdir


@pytest.fixture
def nlp():
    return English()


@pytest.fixture
def lemmatizer(nlp):
    lookups = Lookups()
    lookups.add_table("lemma_index", {"verb": ("cope", "cop")})
    lookups.add_table("lemma_exc", {"verb": {"coping": ("cope",)}})
    lookups.add_table("lemma_rules", {"verb": [["ing", ""]]})
    lemmatizer = nlp.add_pipe("lemmatizer", config={"mode": "rule", "lookups": lookups})
    return lemmatizer


def test_lemmatizer(nlp, lemmatizer):
    doc = nlp.make_doc("coping")
    doc[0].pos_ = "VERB"
    assert doc[0].lemma_ == ""
    doc = lemmatizer(doc)
    assert doc[0].text == "coping"
    assert doc[0].lemma_ == "cope"


def test_lemmatizer_serialize(nlp, lemmatizer):
    nlp2 = English()
    lemmatizer2 = nlp2.add_pipe("lemmatizer")
    lemmatizer2.from_bytes(lemmatizer.to_bytes())
    assert lemmatizer.to_bytes() == lemmatizer2.to_bytes()
    assert lemmatizer.lookups.tables == lemmatizer2.lookups.tables

    # Also test the results are still the same after IO
    with make_tempdir() as tmp_dir:
        nlp.to_disk(tmp_dir)
        nlp2 = util.load_model_from_path(tmp_dir)
        doc2 = nlp2.make_doc("coping")
        doc2[0].pos_ = "VERB"
        assert doc2[0].lemma_ == ""
        doc2 = lemmatizer(doc2)
        assert doc2[0].text == "coping"
        assert doc2[0].lemma_ == "cope"
