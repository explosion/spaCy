# coding: utf-8
from __future__ import unicode_literals

import pytest
import re
from spacy.language import Language
from spacy.tokenizer import Tokenizer

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
