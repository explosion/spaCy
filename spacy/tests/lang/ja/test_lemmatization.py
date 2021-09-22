import pytest


@pytest.mark.parametrize(
    "word,lemma",
    [("新しく", "新しい"), ("赤く", "赤い"), ("すごく", "すごい"), ("いただきました", "いただく"), ("なった", "なる")],
)
def test_ja_lemmatizer_assigns(ja_tokenizer, word, lemma):
    test_lemma = ja_tokenizer(word)[0].lemma_
    assert test_lemma == lemma


@pytest.mark.parametrize(
    "word,norm",
    [
        ("SUMMER", "サマー"),
        ("食べ物", "食べ物"),
        ("綜合", "総合"),
        ("コンピュータ", "コンピューター"),
    ],
)
def test_ja_lemmatizer_norm(ja_tokenizer, word, norm):
    test_norm = ja_tokenizer(word)[0].norm_
    assert test_norm == norm
