import pickle
import re

import pytest

from spacy.lang.en import English
from spacy.lang.it import Italian
from spacy.language import Language
from spacy.tokenizer import Tokenizer
from spacy.training import Example
from spacy.util import load_config_from_str

from ..util import make_tempdir


@pytest.fixture
def meta_data():
    return {
        "name": "name-in-fixture",
        "version": "version-in-fixture",
        "description": "description-in-fixture",
        "author": "author-in-fixture",
        "email": "email-in-fixture",
        "url": "url-in-fixture",
        "license": "license-in-fixture",
        "vectors": {"width": 0, "vectors": 0, "keys": 0, "name": None},
    }


@pytest.mark.issue(2482)
def test_issue2482():
    """Test we can serialize and deserialize a blank NER or parser model."""
    nlp = Italian()
    nlp.add_pipe("ner")
    b = nlp.to_bytes()
    Italian().from_bytes(b)


CONFIG_ISSUE_6950 = """
[nlp]
lang = "en"
pipeline = ["tok2vec", "tagger"]

[components]

[components.tok2vec]
factory = "tok2vec"

[components.tok2vec.model]
@architectures = "spacy.Tok2Vec.v1"

[components.tok2vec.model.embed]
@architectures = "spacy.MultiHashEmbed.v1"
width = ${components.tok2vec.model.encode:width}
attrs = ["NORM","PREFIX","SUFFIX","SHAPE"]
rows = [5000,2500,2500,2500]
include_static_vectors = false

[components.tok2vec.model.encode]
@architectures = "spacy.MaxoutWindowEncoder.v1"
width = 96
depth = 4
window_size = 1
maxout_pieces = 3

[components.ner]
factory = "ner"

[components.tagger]
factory = "tagger"

[components.tagger.model]
@architectures = "spacy.Tagger.v2"
nO = null

[components.tagger.model.tok2vec]
@architectures = "spacy.Tok2VecListener.v1"
width = ${components.tok2vec.model.encode:width}
upstream = "*"
"""


@pytest.mark.issue(6950)
def test_issue6950():
    """Test that the nlp object with initialized tok2vec with listeners pickles
    correctly (and doesn't have lambdas).
    """
    nlp = English.from_config(load_config_from_str(CONFIG_ISSUE_6950))
    nlp.initialize(lambda: [Example.from_dict(nlp.make_doc("hello"), {"tags": ["V"]})])
    pickle.dumps(nlp)
    nlp("hello")
    pickle.dumps(nlp)


def test_serialize_language_meta_disk(meta_data):
    language = Language(meta=meta_data)
    with make_tempdir() as d:
        language.to_disk(d)
        new_language = Language().from_disk(d)
    assert new_language.meta == language.meta


def test_serialize_with_custom_tokenizer():
    """Test that serialization with custom tokenizer works without token_match.
    See: https://support.prodi.gy/t/how-to-save-a-custom-tokenizer/661/2
    """
    prefix_re = re.compile(r"""1/|2/|:[0-9][0-9][A-K]:|:[0-9][0-9]:""")
    suffix_re = re.compile(r"""""")
    infix_re = re.compile(r"""[~]""")

    def custom_tokenizer(nlp):
        return Tokenizer(
            nlp.vocab,
            {},
            prefix_search=prefix_re.search,
            suffix_search=suffix_re.search,
            infix_finditer=infix_re.finditer,
        )

    nlp = Language()
    nlp.tokenizer = custom_tokenizer(nlp)
    with make_tempdir() as d:
        nlp.to_disk(d)


def test_serialize_language_exclude(meta_data):
    name = "name-in-fixture"
    nlp = Language(meta=meta_data)
    assert nlp.meta["name"] == name
    new_nlp = Language().from_bytes(nlp.to_bytes())
    assert new_nlp.meta["name"] == name
    new_nlp = Language().from_bytes(nlp.to_bytes(), exclude=["meta"])
    assert not new_nlp.meta["name"] == name
    new_nlp = Language().from_bytes(nlp.to_bytes(exclude=["meta"]))
    assert not new_nlp.meta["name"] == name
