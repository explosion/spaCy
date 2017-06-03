# coding: utf-8
from __future__ import unicode_literals

from ..util import make_tempdir

import pytest


@pytest.mark.parametrize('text', ["I can't do this"])
def test_serialize_tokenizer_roundtrip_bytes(en_tokenizer, text):
    tokenizer_b = en_tokenizer.to_bytes()
    new_tokenizer = en_tokenizer.from_bytes(tokenizer_b)
    assert new_tokenizer.to_bytes() == tokenizer_b
    doc1 = en_tokenizer(text)
    doc2 = new_tokenizer(text)
    assert [token.text for token in doc1] == [token.text for token in doc2]


def test_serialize_tokenizer_roundtrip_disk(en_tokenizer):
    tokenizer = en_tokenizer
    with make_tempdir() as d:
        file_path = d / 'tokenizer'
        tokenizer.to_disk(file_path)
        tokenizer_d = en_tokenizer.from_disk(file_path)
        assert tokenizer.to_bytes() == tokenizer_d.to_bytes()
