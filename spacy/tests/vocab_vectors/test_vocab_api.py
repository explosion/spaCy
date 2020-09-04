import pytest
from spacy.attrs import LEMMA, ORTH, PROB, IS_ALPHA
from spacy.parts_of_speech import NOUN, VERB


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
        ("PROB", PROB),
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
