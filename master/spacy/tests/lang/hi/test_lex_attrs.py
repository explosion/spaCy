import pytest
from spacy.lang.hi.lex_attrs import norm, like_num


def test_hi_tokenizer_handles_long_text(hi_tokenizer):
    text = """
ये कहानी 1900 के दशक की है। कौशल्या (स्मिता जयकर) को पता चलता है कि उसका
छोटा बेटा, देवदास (शाहरुख खान) वापस घर आ रहा है। देवदास 10 साल पहले कानून की
पढ़ाई करने के लिए इंग्लैंड गया था। उसके लौटने की खुशी में ये बात कौशल्या अपनी पड़ोस
में रहने वाली सुमित्रा (किरण खेर) को भी बता देती है। इस खबर से वो भी खुश हो जाती है।
"""
    tokens = hi_tokenizer(text)
    assert len(tokens) == 86


@pytest.mark.parametrize(
    "word,word_norm",
    [
        ("चलता", "चल"),
        ("पढ़ाई", "पढ़"),
        ("देती", "दे"),
        ("जाती", "ज"),
        ("मुस्कुराकर", "मुस्कुर"),
    ],
)
def test_hi_norm(word, word_norm):
    assert norm(word) == word_norm


@pytest.mark.parametrize(
    "word",
    ["१९८७", "1987", "१२,२६७", "उन्नीस", "पाँच", "नवासी", "५/१०"],
)
def test_hi_like_num(word):
    assert like_num(word)


@pytest.mark.parametrize(
    "word",
    ["पहला", "तृतीय", "निन्यानवेवाँ", "उन्नीस", "तिहत्तरवाँ", "छत्तीसवाँ"],
)
def test_hi_like_num_ordinal_words(word):
    assert like_num(word)
