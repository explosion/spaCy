import pytest
import re
import spacy
from spacy.language import Language
from spacy.lang.en import English
from spacy.tokenizer import Tokenizer
from thinc.config import Config

from ..util import make_tempdir
from ... import registry


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
    assert nlp.meta["name"] == name
    new_nlp = Language().from_bytes(nlp.to_bytes(), exclude=["meta"])
    assert not new_nlp.meta["name"] == name
    new_nlp = Language().from_bytes(nlp.to_bytes(exclude=["meta"]))
    assert not new_nlp.meta["name"] == name
    with pytest.raises(ValueError):
        nlp.to_bytes(meta=False)
    with pytest.raises(ValueError):
        Language().from_bytes(nlp.to_bytes(), meta=False)


def test_serialize_models():
    """ Create a non-default parser config to check nlp serializes it correctly """
    config = """
        [model]
        @architectures = "spacy.TransitionBasedParser.v1"
        nr_feature_tokens = 8
        hidden_width = 64
        maxout_pieces = 2
        
        [model.tok2vec]
        @architectures = "spacy.HashEmbedCNN.v1"
        pretrained_vectors = null
        width = 96
        depth = 4
        embed_size = 5000
        window_size = 1
        maxout_pieces = 7
        subword_features = false
        char_embed = false
    """
    nlp = English()
    model = registry.make_from_config(Config().from_str(config), validate=True)["model"]
    pipe_cfg = {"model": model}
    parser = nlp.create_pipe("parser", config=pipe_cfg)
    parser.add_label("nsubj")
    nlp.add_pipe(parser)

    with make_tempdir() as d:
        nlp.to_disk(d)
        nlp2 = spacy.load(d)
