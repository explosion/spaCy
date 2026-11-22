import pytest


def test_cy_tokenizer_handles_sentence(cy_tokenizer):
    tokens = [t.text for t in cy_tokenizer("Mae'r gath yn cysgu ar y mat.")]
    assert tokens == ["Mae", "'r", "gath", "yn", "cysgu", "ar", "y", "mat", "."]


def test_cy_tokenizer_handles_clitics_in_sentence(cy_tokenizer):
    text = "Dw i'n mynd i'r dref efo f'ewythr a'i gi."
    tokens = [t.text for t in cy_tokenizer(text)]
    assert tokens == [
        "Dw",
        "i",
        "'n",
        "mynd",
        "i",
        "'r",
        "dref",
        "efo",
        "f'",
        "ewythr",
        "a",
        "'i",
        "gi",
        ".",
    ]


@pytest.mark.parametrize(
    "text,length",
    [
        ("Roedd y cyd-destun yn bwysig i'r drafodaeth.", 9),
        ("Aeth hi i'r siop, ond doedd dim bara ar ôl.", 13),
        ("Beth yw'r amser?", 5),
    ],
)
def test_cy_tokenizer_handles_counts(cy_tokenizer, text, length):
    tokens = cy_tokenizer(text)
    assert len(tokens) == length
