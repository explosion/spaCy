def test_tl_simple_punct(tl_tokenizer):
    text = "Sige, punta ka dito"
    tokens = tl_tokenizer(text)
    assert tokens[0].idx == 0
    assert tokens[1].idx == 4
    assert tokens[2].idx == 6
    assert tokens[3].idx == 12
    assert tokens[4].idx == 15
