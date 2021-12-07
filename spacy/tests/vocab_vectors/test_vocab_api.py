import pytest
from spacy.attrs import IS_ALPHA, LEMMA, ORTH
from spacy.parts_of_speech import NOUN, VERB
from spacy.vocab import Vocab


@pytest.mark.issue(1868)
def test_issue1868():
    """Test Vocab.__contains__ works with int keys."""
    vocab = Vocab()
    lex = vocab["hello"]
    assert lex.orth in vocab
    assert lex.orth_ in vocab
    assert "some string" not in vocab
    int_id = vocab.strings.add("some string")
    assert int_id not in vocab


@pytest.mark.parametrize(
    "text1,text2", [("Hello", "bye"), ("Hello", "hello"), ("Hello", "Hello,")]
)
def test_vocab_api_neq(en_vocab, text1, text2):
    assert en_vocab[text1].orth != en_vocab[text2].orth


@pytest.mark.parametrize("text", "Hello")
def test_vocab_api_eq(en_vocab, text):
    lex = en_vocab[text]
    assert en_vocab[text].orth == lex.orth


@pytest.mark.parametrize("text", ["example"])
def test_vocab_api_shape_attr(en_vocab, text):
    lex = en_vocab[text]
    assert lex.orth != lex.shape


@pytest.mark.parametrize(
    "string,symbol",
    [
        ("IS_ALPHA", IS_ALPHA),
        ("NOUN", NOUN),
        ("VERB", VERB),
        ("LEMMA", LEMMA),
        ("ORTH", ORTH),
    ],
)
def test_vocab_api_symbols(en_vocab, string, symbol):
    assert en_vocab.strings[string] == symbol


@pytest.mark.parametrize("text", "Hello")
def test_vocab_api_contains(en_vocab, text):
    _ = en_vocab[text]  # noqa: F841
    assert text in en_vocab
    assert "LKsdjvlsakdvlaksdvlkasjdvljasdlkfvm" not in en_vocab


def test_vocab_writing_system(en_vocab):
    assert en_vocab.writing_system["direction"] == "ltr"
    assert en_vocab.writing_system["has_case"] is True
