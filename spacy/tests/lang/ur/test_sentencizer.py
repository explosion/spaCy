from spacy.pipeline.sentencizer import Sentencizer
from spacy.util import get_lang_class


def test_ur_sentencizer_splits_on_urdu_punct():
    nlp = get_lang_class("ur")()
    nlp.add_pipe("sentencizer")
    doc = nlp("یہ پہلا جملہ ہے۔ یہ دوسرا جملہ ہے؟ تیسرا بھی ہے۔")
    sents = list(doc.sents)
    assert len(sents) == 3
    assert sents[0].text.endswith("۔")
    assert sents[1].text.endswith("؟")


def test_ur_sentencizer_does_not_split_on_newline_alone():
    nlp = get_lang_class("ur")()
    nlp.add_pipe("sentencizer")
    doc = nlp("پہلی سطر\nدوسری سطر۔")
    assert len(list(doc.sents)) == 1


def test_ur_ellipsis_is_not_consecutive_sentence_boundaries():
    nlp = get_lang_class("ur")()
    nlp.add_pipe("sentencizer")
    ellipsis = nlp("خان۔۔۔اب آیا۔")
    assert [t.text for t in ellipsis] == ["خان", "۔۔۔", "اب", "آیا", "۔"]
    assert "۔۔۔" not in Sentencizer.default_punct_chars
    assert "۔" in Sentencizer.default_punct_chars
    assert len(list(ellipsis.sents)) == 1
    two = nlp("یہ پہلا ہے۔ یہ دوسرا ہے۔")
    assert len(list(two.sents)) == 2


def test_ur_abbreviation_is_not_a_sentence_boundary():
    nlp = get_lang_class("ur")()
    nlp.add_pipe("sentencizer")
    doc = nlp("Dr. Khan آیا۔")
    assert [t.text for t in doc][:2] == ["Dr.", "Khan"]
    assert len(list(doc.sents)) == 1
