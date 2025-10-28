import pytest


def test_ht_tokenizer_handles_basic_contraction(ht_tokenizer):
    text = "m'ap ri"
    tokens = ht_tokenizer(text)
    assert len(tokens) == 3
    assert tokens[0].text == "m'"
    assert tokens[1].text == "ap"
    assert tokens[2].text == "ri"

    text = "mwen di'w non!"
    tokens = ht_tokenizer(text)
    assert len(tokens) == 5
    assert tokens[0].text == "mwen"
    assert tokens[1].text == "di"
    assert tokens[2].text == "'w"
    assert tokens[3].text == "non"
    assert tokens[4].text == "!"


@pytest.mark.parametrize("text", ["Dr."])
def test_ht_tokenizer_handles_basic_abbreviation(ht_tokenizer, text):
    tokens = ht_tokenizer(text)
    assert len(tokens) == 1
    assert tokens[0].text == text


def test_ht_tokenizer_full_sentence(ht_tokenizer):
    text = "Si'm ka vini, m'ap pale ak li."
    tokens = [t.text for t in ht_tokenizer(text)]
    assert tokens == [
        "Si",
        "'m",
        "ka",
        "vini",
        ",",
        "m'",
        "ap",
        "pale",
        "ak",
        "li",
        ".",
    ]
