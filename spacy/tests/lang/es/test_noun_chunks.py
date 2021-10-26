from spacy.tokens import Doc
import pytest

@pytest.fixture
def doc_basic(es_vocab):
    words = ["un", "gato"]
    heads = [1, 1]
    deps = ["det", "ROOT"]
    pos = ["DET", "NOUN"]
    return Doc(en_vocab, words=words, heads=heads, deps=deps, pos=pos)

@pytest.fixture
def doc_basic_adj(es_vocab):
    words = ["la", "camisa", "negra"]
    heads = [1, 1, 1]
    deps = ["det", "ROOT", "amod"]
    pos = ["DET", "NOUN", "ADJ"]
    return Doc(en_vocab, words=words, heads=heads, deps=deps, pos=pos)


def test_noun_chunks_is_parsed_es(es_tokenizer):
    """Test that noun_chunks raises Value Error for 'es' language if Doc is not parsed."""
    doc = es_tokenizer("en Oxford este verano")
    with pytest.raises(ValueError):
        list(doc.noun_chunks)


def test_noun_chunks_basic(doc_basic, es_tokenizer):
    """Test that noun_chunks for basic np determiner+noun"""
    doc_chunks = list(doc.noun_chunks)
    assert len(doc_chunks) == 1
    chunk = doc_chunks[0]
    assert chunk in doc_chunks
    assert chunk.start == 0
    assert chunk.end ==2
    assert chunk.text == "un gato"


def test_noun_chunks_basic_adj(doc_basic_adj, es_tokenizer):
    """Test that noun_chunks for basic np determiner+noun+adj"""
    doc_chunks = list(doc.noun_chunks)
    assert len(doc_chunks) == 1
    chunk = doc_chunks[0]
    assert chunk in doc_chunks
    assert chunk.start == 0
    assert chunk.end ==3
    assert chunk.text == "la camisa negra"
