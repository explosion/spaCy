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


@pytest.fixture
def doc_compound_by_flat(es_vocab):
    words = ["Dom", "Pedro", "II"]
    heads = [0, 0, 0]
    deps = ["ROOT", "flat", "flat"]
    pos = ["PROPN", "PROPN", "PROPN"]
    return Doc(es_vocab, words=words, heads=heads, deps=deps, pos=pos)

@pytest.fixture
def doc_compound_by_flat2(es_vocab):
    words = ["los", "Estados", "Unidos"]
    heads = [1, 1, 1]
    deps = ["det", "ROOT", "flat"]
    pos = ["DET", "PROPN", "PROPN"]
    return Doc(es_vocab, words=words, heads=heads, deps=deps, pos=pos)

@pytest.fixture
def doc_compound_by_flat_and_particle(es_vocab):
    words = ["Miguel", "de", "Cervantes"]
    heads = [0, 2, 0]
    deps = ["ROOT", "case", "flat"]
    pos = ["PROPN", "ADP", "PROPN"]
    return Doc(es_vocab, words=words, heads=heads, deps=deps, pos=pos)

@pytest.fixture
def doc_compound_by_flat_and_particle2(es_vocab):
    words = ["Rio", "de", "Janeiro"]
    heads = [0, 2, 0]
    deps = ["ROOT", "case", "flat"]
    pos = ["PROPN", "ADP", "PROPN"]
    return Doc(es_vocab, words=words, heads=heads, deps=deps, pos=pos)

def test_noun_chunks_is_parsed_es(es_tokenizer):
    """Test that noun_chunks raises Value Error for 'es' language if Doc is not parsed."""
    doc = es_tokenizer("en Oxford este verano")
    with pytest.raises(ValueError):
        list(doc.noun_chunks)


def test_noun_chunks_basic(doc_basic, es_tokenizer):
    """Test that noun_chunks are correct for basic np determiner+noun"""
    doc_chunks = list(doc_basic.noun_chunks)
    assert len(doc_chunks) == 1
    chunk = doc_chunks[0]
    assert chunk in doc_chunks
    assert chunk.start == 0
    assert chunk.end ==2
    assert chunk.text == "un gato"


def test_noun_chunks_basic_adj(doc_basic_adj, es_tokenizer):
    """Test that noun_chunks are correct for basic NP determiner+noun+adj"""
    doc_chunks = list(doc_basic_adj.noun_chunks)
    assert len(doc_chunks) == 1
    chunk = doc_chunks[0]
    assert chunk in doc_chunks
    assert chunk.start == 0
    assert chunk.end ==3
    assert chunk.text == "la camisa negra"

def test_noun_chunks_adj_preceeds_noun(doc_adj_noun, es_tokenizer):
    """Test that noun_chunks are correct for NP determiner+adj+noun"""
    doc_chunks = list(doc_adj_noun.noun_chunks)
    assert len(doc_chunks) == 1
    chunk = doc_chunks[0]
    assert chunk in doc_chunks
    assert chunk.start == 0
    assert chunk.end ==3
    assert chunk.text == "Un lindo gatito"

def test_noun_chunks_noun_conj_noun(doc_noun_conj_noun, es_tokenizer):
    """Test that noun_chunks are correct for two NPs connected by conjunction"""
    doc_chunks = list(doc_noun_conj_noun.noun_chunks)
    assert len(doc_chunks) == 2

    chunk1 = doc_chunks[0]
    assert chunk1 in doc_chunks
    assert chunk1.start == 1
    assert chunk1.end ==3
    assert chunk1.text == "un gato"

    chunk2 = doc_chunks[1]
    assert chunk2 in doc_chunks
    assert chunk2.start == 4
    assert chunk2.end == 6
    assert chunk2.text == "un perro"

def test_noun_chunks_two_adjectives(doc_two_adjs, es_tokenizer):
    """Test that noun_chunks are correct for one two adjectives conjuncted qualifying a noun"""
    doc_chunks = list(doc_two_adjs.noun_chunks)
    assert len(doc_chunks) == 1
    chunk = doc_chunks[0]
    assert chunk in doc_chunks
    assert chunk.start == 0
    assert chunk.end == 5
    assert chunk.text == "Una chica hermosa e inteligente"

def test_compound_by_flat(doc_compound_by_flat, es_tokenizer):
    """Test that noun_chunks are correct for a compound formed by flat rels"""
    doc_chunks = list(doc_compound_by_flat.noun_chunks)
    assert len(doc_chunks) == 1
    chunk = doc_chunks[0]
    assert chunk in doc_chunks
    assert chunk.start == 0
    assert chunk.end == 3
    assert chunk.text == "Dom Pedro II"

def test_proper_noun_compound_flat2(doc_compound_by_flat2, es_tokenizer):
    """Test that noun_chunks are correct for a compound formed by flat rels"""
    doc_chunks = list(doc_compound_by_flat2.noun_chunks)
    assert len(doc_chunks) == 1
    chunk = doc_chunks[0]
    assert chunk in doc_chunks
    assert chunk.start == 0
    assert chunk.end == 3
    assert chunk.text == "los Estados Unidos"

def test_proper_noun_compound_flat_and_case(doc_compound_by_flat_and_particle, es_tokenizer):
    """Test that noun_chunks are correct for a compound formed by flat and case"""
    doc_chunks = list(doc_compound_by_flat_and_particle.noun_chunks)
    assert len(doc_chunks) == 1
    chunk = doc_chunks[0]
    assert chunk in doc_chunks
    assert chunk.start == 0
    assert chunk.end == 3
    assert chunk.text == "Miguel de Cervantes"

def test_proper_noun_compound_flat_and_case2(doc_compound_by_flat_and_particle2, es_tokenizer):
    """Test that noun_chunks are correct for a compound formed by flat and case"""
    doc_chunks = list(doc_compound_by_flat_and_particle2.noun_chunks)
    assert len(doc_chunks) == 1
    chunk = doc_chunks[0]
    assert chunk in doc_chunks
    assert chunk.start == 0
    assert chunk.end == 3
    assert chunk.text == "Rio de Janeiro"
