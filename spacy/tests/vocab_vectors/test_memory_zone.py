from spacy.vocab import Vocab


def test_memory_zone_no_insertion():
    vocab = Vocab()
    with vocab.memory_zone():
        pass
    lex = vocab["horse"]
    assert lex.text == "horse"


def test_memory_zone_insertion():
    vocab = Vocab()
    _ = vocab["dog"]
    assert "dog" in vocab
    assert "horse" not in vocab
    with vocab.memory_zone():
        lex = vocab["horse"]
        assert lex.text == "horse"
    assert "dog" in vocab
    assert "horse" not in vocab


def test_memory_zone_redundant_insertion():
    """Test that if we insert an already-existing word while
    in the memory zone, it stays persistent"""
    vocab = Vocab()
    _ = vocab["dog"]
    assert "dog" in vocab
    assert "horse" not in vocab
    with vocab.memory_zone():
        lex = vocab["horse"]
        assert lex.text == "horse"
        _ = vocab["dog"]
    assert "dog" in vocab
    assert "horse" not in vocab
