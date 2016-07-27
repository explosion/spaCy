from __future__ import unicode_literals
import pytest
from spacy.attrs import HEAD
import numpy


@pytest.mark.xfail
def test_example_war_and_peace(nlp):
    # from spacy.en import English
    from spacy._doc_examples import download_war_and_peace

    unprocessed_unicode = download_war_and_peace()

    # nlp = English()
    # TODO: ImportError: No module named _doc_examples
    doc = nlp(unprocessed_unicode)


def test_main_entry_point(nlp):
    # from spacy.en import English
    # nlp = English()
    doc = nlp('Some text.') # Applies tagger, parser, entity
    doc = nlp('Some text.', parse=False) # Applies tagger and entity, not parser
    doc = nlp('Some text.', entity=False) # Applies tagger and parser, not entity
    doc = nlp('Some text.', tag=False) # Does not apply tagger, entity or parser
    doc = nlp('') # Zero-length tokens, not an error
    # doc = nlp(b'Some text') <-- Error: need unicode
    doc = nlp(b'Some text'.decode('utf8')) # Encode to unicode first.


@pytest.mark.models
def test_sentence_spans(nlp):
    # from spacy.en import English
    # nlp = English()
    doc = nlp("This is a sentence. Here's another...")
    assert [s.root.orth_ for s in doc.sents] == ["is", "'s"]


@pytest.mark.models
def test_entity_spans(nlp):
    # from spacy.en import English
    # nlp = English()
    tokens = nlp('Mr. Best flew to New York on Saturday morning.')
    ents = list(tokens.ents)
    assert ents[0].label == 346
    assert ents[0].label_ == 'PERSON'
    assert ents[0].orth_ == 'Best'
    assert ents[0].string == ents[0].string


@pytest.mark.models
def test_noun_chunk_spans(nlp):
    # from spacy.en import English
    # nlp = English()
    doc = nlp('The sentence in this example has three noun chunks.')
    for chunk in doc.noun_chunks:
        print(chunk.label, chunk.orth_, '<--', chunk.root.head.orth_)

    # NP The sentence <-- has
    # NP this example <-- in
    # NP three noun chunks <-- has


@pytest.mark.models
def test_count_by(nlp):
    # from spacy.en import English, attrs
    # nlp = English()
    import numpy
    from spacy import attrs
    tokens = nlp('apple apple orange banana')
    assert tokens.count_by(attrs.ORTH) == {3699: 2, 3750: 1, 5965: 1}
    assert repr(tokens.to_array([attrs.ORTH])) == repr(numpy.array([[3699],
                                                        [3699],
                                                        [3750],
                                                        [5965]], dtype=numpy.int32))

@pytest.mark.models
def test_read_bytes(nlp):
    from spacy.tokens.doc import Doc
    loc = 'test_serialize.bin'
    with open(loc, 'wb') as file_:
        file_.write(nlp(u'This is a document.').to_bytes())
        file_.write(nlp(u'This is another.').to_bytes())
    docs = []
    with open(loc, 'rb') as file_:
        for byte_string in Doc.read_bytes(file_):
            docs.append(Doc(nlp.vocab).from_bytes(byte_string))
    assert len(docs) == 2


def test_token_span(doc):
    span = doc[4:6]
    token = span[0]
    assert token.i == 4


@pytest.mark.models
def test_example_i_like_new_york1(nlp):
    toks = nlp('I like New York in Autumn.')


@pytest.fixture
def toks(nlp):
    doc = nlp('I like New York in Autumn.')
    doc.from_array([HEAD], numpy.asarray([[1, 0, 1, -2, -3, -1, -5]], dtype='int32').T)
    return doc


def test_example_i_like_new_york2(toks):
    i, like, new, york, in_, autumn, dot = range(len(toks))


@pytest.fixture
def tok(toks, tok):
    i, like, new, york, in_, autumn, dot = range(len(toks))
    return locals()[tok]


@pytest.fixture
def new(toks):
    return tok(toks, "new")


@pytest.fixture
def york(toks):
    return tok(toks, "york")


@pytest.fixture
def autumn(toks):
    return tok(toks, "autumn")


@pytest.fixture
def dot(toks):
    return tok(toks, "dot")


def test_example_i_like_new_york3(toks, new, york):
    assert toks[new].head.orth_ == 'York'
    assert toks[york].head.orth_ == 'like'


def test_example_i_like_new_york4(toks, new, york):
    new_york = toks[new:york+1]
    assert new_york.root.orth_ == 'York'


def test_example_i_like_new_york5(toks, autumn, dot):
    assert toks[autumn].head.orth_ == 'in'
    assert toks[dot].head.orth_ == 'like'
    autumn_dot = toks[autumn:]
    assert autumn_dot.root.orth_ == 'Autumn'


def test_navigating_the_parse_tree_lefts(doc):
    # TODO: where does the span object come from?
    span = doc[:2]
    lefts = [span.doc[i] for i in range(0, span.start)
             if span.doc[i].head in span]


def test_navigating_the_parse_tree_rights(doc):
    span = doc[:2]
    rights = [span.doc[i] for i in range(span.end, len(span.doc))
              if span.doc[i].head in span]


def test_string_store(doc):
    string_store = doc.vocab.strings
    for i, string in enumerate(string_store):
        assert i == string_store[string]
