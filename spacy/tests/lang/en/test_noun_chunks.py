from spacy.tokens import Doc
import pytest


@pytest.fixture
def doc(en_vocab):
    words = ["Peter", "has", "chronic", "command", "and", "control", "issues"]
    heads = [1, 1, 6, 6, 3, 3, 1]
    deps = ["nsubj", "ROOT", "amod", "nmod", "cc", "conj", "dobj"]
    pos = ["PROPN", "VERB", "ADJ", "NOUN", "CCONJ", "NOUN", "NOUN"]
    return Doc(en_vocab, words=words, heads=heads, deps=deps, pos=pos)


def test_noun_chunks_is_parsed(en_tokenizer):
    """Test that noun_chunks raises Value Error for 'en' language if Doc is not parsed."""
    doc = en_tokenizer("This is a sentence")
    with pytest.raises(ValueError):
        list(doc.noun_chunks)


def test_en_noun_chunks_not_nested(doc, en_vocab):
    """Test that each token only appears in one noun chunk at most"""
    word_occurred = {}
    chunks = list(doc.noun_chunks)
    assert len(chunks) > 1
    for chunk in chunks:
        for word in chunk:
            word_occurred.setdefault(word.text, 0)
            word_occurred[word.text] += 1
    assert len(word_occurred) > 0
    for word, freq in word_occurred.items():
        assert freq == 1, (word, [chunk.text for chunk in doc.noun_chunks])


def test_noun_chunks_span(doc, en_tokenizer):
    """Test that the span.noun_chunks property works correctly"""
    doc_chunks = list(doc.noun_chunks)
    span = doc[0:3]
    span_chunks = list(span.noun_chunks)
    assert 0 < len(span_chunks) < len(doc_chunks)
    for chunk in span_chunks:
        assert chunk in doc_chunks
        assert chunk.start >= 0
        assert chunk.end <= 3
