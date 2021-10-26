from spacy.tokens import Doc
import pytest

@pytest.fixture
def doc_basic(es_vocab):
    words = ["un", "gato"]
    heads = [1, 1]
    deps = ["det", "ROOT"]
    pos = ["DET", "NOUN"]
    return Doc(es_vocab, words=words, heads=heads, deps=deps, pos=pos)

@pytest.fixture
def doc_basic_adj(es_vocab):
    words = ["la", "camisa", "negra"]
    heads = [1, 1, 1]
    deps = ["det", "ROOT", "amod"]
    pos = ["DET", "NOUN", "ADJ"]
    return Doc(es_vocab, words=words, heads=heads, deps=deps, pos=pos)

@pytest.fixture
def doc_adj_noun(es_vocab):
    words = ["Un", "lindo", "gatito"]
    heads = [2, 2, 2]
    deps = ["det", "amod", "ROOT"]
    pos = ["DET", "ADJ", "NOUN"]
    return Doc(es_vocab, words=words, heads=heads, deps=deps, pos=pos)

@pytest.fixture
def doc_two_adjs(es_vocab):
    words = ["Una", "chica", "hermosa", "e", "inteligente"]
    heads = [1, 1, 1, 4, 2]
    deps = ["det", "ROOT", "amod", "cc", "conj"]
    pos = ["DET", "NOUN", "ADJ", "CCONJ", "ADJ"]
    return Doc(es_vocab, words=words, heads=heads, deps=deps, pos=pos)

@pytest.fixture
def doc_noun_conj_noun(es_vocab):
    words = ["Tengo", "un", "gato", "y", "un", "perro"]
    heads = [0, 2, 0, 5, 5, 0]
    deps = ["ROOT", "det", "obj", "cc", "det", "conj"]
    pos = ["VERB", "DET", "NOUN", "CCONJ", "DET", "NOUN"]
    return Doc(es_vocab, words=words, heads=heads, deps=deps, pos=pos)

def test_noun_chunks_is_parsed_es(es_tokenizer):
    """Test that noun_chunks raises Value Error for 'es' language if Doc is not parsed."""
    doc = es_tokenizer("en Oxford este verano")
    with pytest.raises(ValueError):
        list(doc.noun_chunks)


def test_noun_chunks_basic(doc_basic, es_tokenizer):
    """Test that noun_chunks for basic np determiner+noun"""
    doc_chunks = list(doc_basic.noun_chunks)
    assert len(doc_chunks) == 1
    chunk = doc_chunks[0]
    assert chunk in doc_chunks
    assert chunk.start == 0
    assert chunk.end ==2
    assert chunk.text == "un gato"


def test_noun_chunks_basic_adj(doc_basic_adj, es_tokenizer):
    """Test that noun_chunks for basic np determiner+noun+adj"""
    doc_chunks = list(doc_basic_adj.noun_chunks)
    assert len(doc_chunks) == 1
    chunk = doc_chunks[0]
    assert chunk in doc_chunks
    assert chunk.start == 0
    assert chunk.end ==3
    assert chunk.text == "la camisa negra"

def test_noun_chunks_adj_preceeds_noun(doc_adj_noun, es_tokenizer):
    """Test that noun_chunks for np determiner+adj+noun"""
    doc_chunks = list(doc_adj_noun.noun_chunks)
    assert len(doc_chunks) == 1
    chunk = doc_chunks[0]
    assert chunk in doc_chunks
    assert chunk.start == 0
    assert chunk.end ==3
    assert chunk.text == "Un lindo gatito"

def test_noun_chunks_noun_conj_noun(doc_noun_conj_noun, es_tokenizer):
    """Test that noun_chunks for two NPs connected by conjunction"""
    doc_chunks = list(doc_noun_conj_noun.noun_chunks)
    assert len(doc_chunks) == 2

    chunk1 = doc_chunks[0]
    assert chunk in doc_chunks
    assert chunk.start == 1
    assert chunk.end ==3
    assert chunk.text == "un gato"

    chunk2 = doc_chunks[1]
    assert chunk1 in doc_chunks
    assert chunk1.start == 4
    assert chunk1.end == 6
    assert chunk1.text == "un perro"

def test_noun_chunks_two_adjectives(doc_two_adjs, es_tokenizer):
    """Test that noun_chunks for np determiner+adj+noun"""
    doc_chunks = list(doc_two_adjs.noun_chunks)
    assert len(doc_chunks) == 1
    chunk = doc_chunks[0]
    assert chunk in doc_chunks
    assert chunk.start == 0
    assert chunk.end == 5
    assert chunk.text == "Una chica hermosa e inteligente"

