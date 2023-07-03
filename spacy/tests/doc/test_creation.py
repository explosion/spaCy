import pytest

from spacy import util
from spacy.tokens import Doc
from spacy.vocab import Vocab


@pytest.fixture
def vocab():
    return Vocab()


def test_empty_doc(vocab):
    doc = Doc(vocab)
    assert len(doc) == 0


def test_single_word(vocab):
    doc = Doc(vocab, words=["a"])
    assert doc.text == "a "
    doc = Doc(vocab, words=["a"], spaces=[False])
    assert doc.text == "a"


def test_create_from_words_and_text(vocab):
    # no whitespace in words
    words = ["'", "dogs", "'", "run"]
    text = "  'dogs'\n\nrun  "
    (words, spaces) = util.get_words_and_spaces(words, text)
    doc = Doc(vocab, words=words, spaces=spaces)
    assert [t.text for t in doc] == ["  ", "'", "dogs", "'", "\n\n", "run", " "]
    assert [t.whitespace_ for t in doc] == ["", "", "", "", "", " ", ""]
    assert doc.text == text
    assert [t.text for t in doc if not t.text.isspace()] == [
        word for word in words if not word.isspace()
    ]

    # partial whitespace in words
    words = ["  ", "'", "dogs", "'", "\n\n", "run", " "]
    text = "  'dogs'\n\nrun  "
    (words, spaces) = util.get_words_and_spaces(words, text)
    doc = Doc(vocab, words=words, spaces=spaces)
    assert [t.text for t in doc] == ["  ", "'", "dogs", "'", "\n\n", "run", " "]
    assert [t.whitespace_ for t in doc] == ["", "", "", "", "", " ", ""]
    assert doc.text == text
    assert [t.text for t in doc if not t.text.isspace()] == [
        word for word in words if not word.isspace()
    ]

    # non-standard whitespace tokens
    words = [" ", " ", "'", "dogs", "'", "\n\n", "run"]
    text = "  'dogs'\n\nrun  "
    (words, spaces) = util.get_words_and_spaces(words, text)
    doc = Doc(vocab, words=words, spaces=spaces)
    assert [t.text for t in doc] == ["  ", "'", "dogs", "'", "\n\n", "run", " "]
    assert [t.whitespace_ for t in doc] == ["", "", "", "", "", " ", ""]
    assert doc.text == text
    assert [t.text for t in doc if not t.text.isspace()] == [
        word for word in words if not word.isspace()
    ]

    # mismatch between words and text
    with pytest.raises(ValueError):
        words = [" ", " ", "'", "dogs", "'", "\n\n", "run"]
        text = "  'dogs'\n\nrun  "
        (words, spaces) = util.get_words_and_spaces(words + ["away"], text)


def test_create_with_heads_and_no_deps(vocab):
    words = "I like ginger".split()
    heads = list(range(len(words)))
    with pytest.raises(ValueError):
        Doc(vocab, words=words, heads=heads)


def test_create_invalid_pos(vocab):
    words = "I like ginger".split()
    pos = "QQ ZZ XX".split()
    with pytest.raises(ValueError):
        Doc(vocab, words=words, pos=pos)
