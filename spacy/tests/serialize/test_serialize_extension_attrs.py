# coding: utf-8
from __future__ import unicode_literals

import pytest
from spacy.tokens import Doc
from spacy.vocab import Vocab


@pytest.fixture
def doc_w_attrs(en_tokenizer):
    Doc.set_extension("_test_attr", default=False)
    Doc.set_extension("_test_prop", getter=lambda doc: len(doc.text))
    Doc.set_extension(
        "_test_method", method=lambda doc, arg: "{}{}".format(len(doc.text), arg)
    )
    doc = en_tokenizer("This is a test.")
    doc._._test_attr = "test"
    return doc


def test_serialize_ext_attrs_from_bytes(doc_w_attrs):
    doc_b = doc_w_attrs.to_bytes()
    doc = Doc(Vocab()).from_bytes(doc_b)
    assert doc._.has("_test_attr")
    assert doc._._test_attr == "test"
    assert doc._._test_prop == len(doc.text)
    assert doc._._test_method("test") == "{}{}".format(len(doc.text), "test")
