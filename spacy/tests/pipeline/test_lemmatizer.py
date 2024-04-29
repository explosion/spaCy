import pickle

import pytest

from spacy import registry, util
from spacy.lang.en import English
from spacy.lookups import Lookups

from ..util import make_tempdir


@pytest.fixture
def nlp():
    @registry.misc("cope_lookups")
    def cope_lookups():
        lookups = Lookups()
        lookups.add_table("lemma_lookup", {"cope": "cope", "coped": "cope"})
        lookups.add_table("lemma_index", {"verb": ("cope", "cop")})
        lookups.add_table("lemma_exc", {"verb": {"coping": ("cope",)}})
        lookups.add_table("lemma_rules", {"verb": [["ing", ""]]})
        return lookups

    nlp = English()
    nlp.config["initialize"]["components"]["lemmatizer"] = {
        "lookups": {"@misc": "cope_lookups"}
    }
    return nlp


def test_lemmatizer_init(nlp):
    lemmatizer = nlp.add_pipe("lemmatizer", config={"mode": "lookup"})
    assert isinstance(lemmatizer.lookups, Lookups)
    assert not lemmatizer.lookups.tables
    assert lemmatizer.mode == "lookup"
    with pytest.raises(ValueError):
        nlp("test")
    nlp.initialize()
    assert lemmatizer.lookups.tables
    assert nlp("cope")[0].lemma_ == "cope"
    assert nlp("coped")[0].lemma_ == "cope"
    # replace any tables from spacy-lookups-data
    lemmatizer.lookups = Lookups()
    # lookup with no tables sets text as lemma
    assert nlp("cope")[0].lemma_ == "cope"
    assert nlp("coped")[0].lemma_ == "coped"
    nlp.remove_pipe("lemmatizer")
    lemmatizer = nlp.add_pipe("lemmatizer", config={"mode": "lookup"})
    with pytest.raises(ValueError):
        # Can't initialize without required tables
        lemmatizer.initialize(lookups=Lookups())
    lookups = Lookups()
    lookups.add_table("lemma_lookup", {})
    lemmatizer.initialize(lookups=lookups)


def test_lemmatizer_config(nlp):
    lemmatizer = nlp.add_pipe("lemmatizer", config={"mode": "rule"})
    nlp.initialize()

    # warning if no POS assigned
    doc = nlp.make_doc("coping")
    with pytest.warns(UserWarning):
        doc = lemmatizer(doc)
    # warns once by default
    doc = lemmatizer(doc)

    # works with POS
    doc = nlp.make_doc("coping")
    assert doc[0].lemma_ == ""
    doc[0].pos_ = "VERB"
    doc = lemmatizer(doc)
    doc = lemmatizer(doc)
    assert doc[0].text == "coping"
    assert doc[0].lemma_ == "cope"

    doc = nlp.make_doc("coping")
    doc[0].pos_ = "VERB"
    assert doc[0].lemma_ == ""
    doc = lemmatizer(doc)
    assert doc[0].text == "coping"
    assert doc[0].lemma_ == "cope"


def test_lemmatizer_serialize(nlp):
    lemmatizer = nlp.add_pipe("lemmatizer", config={"mode": "rule"})
    nlp.initialize()

    def cope_lookups():
        lookups = Lookups()
        lookups.add_table("lemma_lookup", {"cope": "cope", "coped": "cope"})
        lookups.add_table("lemma_index", {"verb": ("cope", "cop")})
        lookups.add_table("lemma_exc", {"verb": {"coping": ("cope",)}})
        lookups.add_table("lemma_rules", {"verb": [["ing", ""]]})
        return lookups

    nlp2 = English()
    lemmatizer2 = nlp2.add_pipe("lemmatizer", config={"mode": "rule"})
    lemmatizer2.initialize(lookups=cope_lookups())
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
    doc2 = lemmatizer2(doc2)
    assert doc2[0].text == "coping"
    assert doc2[0].lemma_ == "cope"

    # Make sure that lemmatizer cache can be pickled
    pickle.dumps(lemmatizer2)
