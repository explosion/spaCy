import pickle

import pytest
import re

from spacy.util import get_lang_class
from spacy.tokenizer import Tokenizer
from spacy.tokens import Doc
from spacy.attrs import ENT_IOB, ENT_TYPE

from ..util import make_tempdir, assert_packed_msg_equal


def load_tokenizer(b):
    tok = get_lang_class("en")().tokenizer
    tok.from_bytes(b)
    return tok


@pytest.mark.issue(2833)
def test_issue2833(en_vocab):
    """Test that a custom error is raised if a token or span is pickled."""
    doc = Doc(en_vocab, words=["Hello", "world"])
    with pytest.raises(NotImplementedError):
        pickle.dumps(doc[0])
    with pytest.raises(NotImplementedError):
        pickle.dumps(doc[0:2])


@pytest.mark.issue(3012)
def test_issue3012(en_vocab):
    """Test that the is_tagged attribute doesn't get overwritten when we from_array
    without tag information."""
    words = ["This", "is", "10", "%", "."]
    tags = ["DT", "VBZ", "CD", "NN", "."]
    pos = ["DET", "VERB", "NUM", "NOUN", "PUNCT"]
    ents = ["O", "O", "B-PERCENT", "I-PERCENT", "O"]
    doc = Doc(en_vocab, words=words, tags=tags, pos=pos, ents=ents)
    assert doc.has_annotation("TAG")
    expected = ("10", "NUM", "CD", "PERCENT")
    assert (doc[2].text, doc[2].pos_, doc[2].tag_, doc[2].ent_type_) == expected
    header = [ENT_IOB, ENT_TYPE]
    ent_array = doc.to_array(header)
    doc.from_array(header, ent_array)
    assert (doc[2].text, doc[2].pos_, doc[2].tag_, doc[2].ent_type_) == expected
    # Serializing then deserializing
    doc_bytes = doc.to_bytes()
    doc2 = Doc(en_vocab).from_bytes(doc_bytes)
    assert (doc2[2].text, doc2[2].pos_, doc2[2].tag_, doc2[2].ent_type_) == expected


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
