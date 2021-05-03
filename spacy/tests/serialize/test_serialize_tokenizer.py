import pytest
import re
from spacy.util import get_lang_class
from spacy.tokenizer import Tokenizer

from ..util import make_tempdir, assert_packed_msg_equal


def load_tokenizer(b):
    tok = get_lang_class("en")().tokenizer
    tok.from_bytes(b)
    return tok


def test_serialize_custom_tokenizer(en_vocab, en_tokenizer):
    """Test that custom tokenizer with not all functions defined or empty
    properties can be serialized and deserialized correctly (see #2494,
    #4991)."""
    tokenizer = Tokenizer(en_vocab, suffix_search=en_tokenizer.suffix_search)
    tokenizer_bytes = tokenizer.to_bytes()
    Tokenizer(en_vocab).from_bytes(tokenizer_bytes)

    # test that empty/unset values are set correctly on deserialization
    tokenizer = get_lang_class("en")().tokenizer
    tokenizer.token_match = re.compile("test").match
    assert tokenizer.rules != {}
    assert tokenizer.token_match is not None
    assert tokenizer.url_match is not None
    assert tokenizer.prefix_search is not None
    assert tokenizer.infix_finditer is not None
    tokenizer.from_bytes(tokenizer_bytes)
    assert tokenizer.rules == {}
    assert tokenizer.token_match is None
    assert tokenizer.url_match is None
    assert tokenizer.prefix_search is None
    assert tokenizer.infix_finditer is None

    tokenizer = Tokenizer(en_vocab, rules={"ABC.": [{"ORTH": "ABC"}, {"ORTH": "."}]})
    tokenizer.rules = {}
    tokenizer_bytes = tokenizer.to_bytes()
    tokenizer_reloaded = Tokenizer(en_vocab).from_bytes(tokenizer_bytes)
    assert tokenizer_reloaded.rules == {}


@pytest.mark.parametrize("text", ["I💜you", "they’re", "“hello”"])
def test_serialize_tokenizer_roundtrip_bytes(en_tokenizer, text):
    tokenizer = en_tokenizer
    new_tokenizer = load_tokenizer(tokenizer.to_bytes())
    assert_packed_msg_equal(new_tokenizer.to_bytes(), tokenizer.to_bytes())
    assert new_tokenizer.to_bytes() == tokenizer.to_bytes()
    doc1 = tokenizer(text)
    doc2 = new_tokenizer(text)
    assert [token.text for token in doc1] == [token.text for token in doc2]


def test_serialize_tokenizer_roundtrip_disk(en_tokenizer):
    tokenizer = en_tokenizer
    with make_tempdir() as d:
        file_path = d / "tokenizer"
        tokenizer.to_disk(file_path)
        tokenizer_d = en_tokenizer.from_disk(file_path)
        assert tokenizer.to_bytes() == tokenizer_d.to_bytes()
