import pytest


@pytest.mark.parametrize("text", ["z.B.", "Jan."])
def test_lb_tokenizer_handles_abbr(lb_tokenizer, text):
    tokens = lb_tokenizer(text)
    assert len(tokens) == 1


@pytest.mark.parametrize("text", ["d'Saach", "d'Kanner", "d’Welt", "d’Suen"])
def test_lb_tokenizer_splits_contractions(lb_tokenizer, text):
    tokens = lb_tokenizer(text)
    assert len(tokens) == 2


def test_lb_tokenizer_handles_exc_in_text(lb_tokenizer):
    text = "Mee 't ass net evident, d'Liewen."
    tokens = lb_tokenizer(text)
    assert len(tokens) == 9
    assert tokens[1].text == "'t"
