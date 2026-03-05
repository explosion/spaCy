from spacy.vocab import Vocab
import pytest


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


@pytest.mark.issue(13882)
def test_memory_zone_vocab_length_decremented():
    """Test that vocab.length is correctly decremented when memory_zone
    clears transient lexemes.

    Bug: The length counter was incremented when adding lexemes but never
    decremented when memory_zone cleared transient lexemes, causing
    len(vocab) to grow continuously even though lexemes were properly removed.
    """
    vocab = Vocab()

    # Add some permanent lexemes
    vocab["hello"]
    vocab["world"]
    initial_len = len(vocab)
    assert initial_len == 2

    # Add transient lexemes inside memory_zone
    with vocab.memory_zone():
        vocab["transient1"]
        vocab["transient2"]
        vocab["transient3"]
        inside_len = len(vocab)
        assert inside_len == 5  # 2 permanent + 3 transient

    # After exiting memory_zone, length should return to initial
    after_zone_len = len(vocab)
    assert after_zone_len == initial_len, (
        f"vocab.length should be {initial_len} after memory_zone, "
        f"but got {after_zone_len}"
    )

    # Verify by iteration that only permanent lexemes remain
    actual_count = sum(1 for _ in vocab)
    assert actual_count == initial_len
    assert after_zone_len == actual_count


@pytest.mark.issue(13882)
def test_memory_zone_multiple_cycles():
    """Test that vocab.length is correctly maintained across multiple
    memory_zone cycles."""
    vocab = Vocab()
    vocab["permanent"]
    base_len = len(vocab)
    assert base_len == 1

    # Multiple memory_zone cycles
    for i in range(3):
        with vocab.memory_zone():
            for j in range(5):
                vocab[f"temp_{i}_{j}"]

        # Length should return to base after each cycle
        assert len(vocab) == base_len, (
            f"After cycle {i+1}, vocab.length should be {base_len}, "
            f"but got {len(vocab)}"
        )

    # Final verification
    final_len = len(vocab)
    actual_count = sum(1 for _ in vocab)
    assert final_len == actual_count == base_len
