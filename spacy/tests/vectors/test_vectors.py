import pytest

@pytest.mark.models
def test_token_vector(EN):
    token = EN(u'Apples and oranges')[0]
    token.vector
    token.vector_norm

@pytest.mark.models
def test_lexeme_vector(EN):
    lexeme = EN.vocab[u'apples']
    lexeme.vector
    lexeme.vector_norm


@pytest.mark.models
def test_doc_vector(EN):
    doc = EN(u'Apples and oranges')
    doc.vector
    doc.vector_norm

@pytest.mark.models
def test_span_vector(EN):
    span = EN(u'Apples and oranges')[0:2]
    span.vector
    span.vector_norm

@pytest.mark.models
def test_token_token_similarity(EN):
    apples, oranges = EN(u'apples oranges')
    assert apples.similarity(oranges) == oranges.similarity(apples)
    assert 0.0 < apples.similarity(oranges) < 1.0
    

@pytest.mark.models
def test_token_lexeme_similarity(EN):
    apples = EN(u'apples')
    oranges = EN.vocab[u'oranges']
    assert apples.similarity(oranges) == oranges.similarity(apples)
    assert 0.0 < apples.similarity(oranges) < 1.0
 

@pytest.mark.models
def test_token_span_similarity(EN):
    doc = EN(u'apples orange juice')
    apples = doc[0]
    oranges = doc[1:3]
    assert apples.similarity(oranges) == oranges.similarity(apples)
    assert 0.0 < apples.similarity(oranges) < 1.0
 

@pytest.mark.models
def test_token_doc_similarity(EN):
    doc = EN(u'apples orange juice')
    apples = doc[0]
    assert apples.similarity(doc) == doc.similarity(apples)
    assert 0.0 < apples.similarity(doc) < 1.0
 

@pytest.mark.models
def test_lexeme_span_similarity(EN):
    doc = EN(u'apples orange juice')
    apples = EN.vocab[u'apples']
    span = doc[1:3]
    assert apples.similarity(span) == span.similarity(apples)
    assert 0.0 < apples.similarity(span) < 1.0


@pytest.mark.models
def test_lexeme_lexeme_similarity(EN):
    apples = EN.vocab[u'apples']
    oranges = EN.vocab[u'oranges']
    assert apples.similarity(oranges) == oranges.similarity(apples)
    assert 0.0 < apples.similarity(oranges) < 1.0
 

@pytest.mark.models
def test_lexeme_doc_similarity(EN):
    doc = EN(u'apples orange juice')
    apples = EN.vocab[u'apples']
    assert apples.similarity(doc) == doc.similarity(apples)
    assert 0.0 < apples.similarity(doc) < 1.0
 

@pytest.mark.models
def test_span_span_similarity(EN):
    doc = EN(u'apples orange juice')
    apples = doc[0:2]
    oj = doc[1:3]
    assert apples.similarity(oj) == oj.similarity(apples)
    assert 0.0 < apples.similarity(oj) < 1.0
 

@pytest.mark.models
def test_span_doc_similarity(EN):
    doc = EN(u'apples orange juice')
    apples = doc[0:2]
    oj = doc[1:3]
    assert apples.similarity(doc) == doc.similarity(apples)
    assert 0.0 < apples.similarity(doc) < 1.0
 

@pytest.mark.models
def test_doc_doc_similarity(EN):
    apples = EN(u'apples and apple pie')
    oranges = EN(u'orange juice')
    assert apples.similarity(oranges) == apples.similarity(oranges)
    assert 0.0 < apples.similarity(oranges) < 1.0
 
