import pytest


@pytest.mark.parametrize("text,length", [("z.B.", 1), ("zb.", 2), ("(z.B.", 2)])
def test_lb_tokenizer_splits_prefix_interact(lb_tokenizer, text, length):
    tokens = lb_tokenizer(text)
    assert len(tokens) == length


@pytest.mark.parametrize("text", ["z.B.)"])
def test_lb_tokenizer_splits_suffix_interact(lb_tokenizer, text):
    tokens = lb_tokenizer(text)
    assert len(tokens) == 2


@pytest.mark.parametrize("text", ["(z.B.)"])
def test_lb_tokenizer_splits_even_wrap_interact(lb_tokenizer, text):
    tokens = lb_tokenizer(text)
    assert len(tokens) == 3
