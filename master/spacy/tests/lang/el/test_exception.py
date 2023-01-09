import pytest


@pytest.mark.parametrize("text", ["αριθ.", "τρισ.", "δισ.", "σελ."])
def test_el_tokenizer_handles_abbr(el_tokenizer, text):
    tokens = el_tokenizer(text)
    assert len(tokens) == 1


def test_el_tokenizer_handles_exc_in_text(el_tokenizer):
    text = "Στα 14 τρισ. δολάρια το κόστος από την άνοδο της στάθμης της θάλασσας."
    tokens = el_tokenizer(text)
    assert len(tokens) == 14
    assert tokens[2].text == "τρισ."
