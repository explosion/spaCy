from __future__ import unicode_literals
import pytest


@pytest.fixture(scope="session")
def nlp():
    from spacy.en import English
    return English()


@pytest.fixture()
def doc(nlp):
    return nlp('Hello, world. Here are two sentences.')


@pytest.fixture()
def token(doc):
    return doc[0]


def test_load_resources_and_process_text():
    from spacy.en import English
    nlp = English()
    doc = nlp('Hello, world. Here are two sentences.')


def test_get_tokens_and_sentences(doc):
    token = doc[0]
    sentence = doc.sents.next()

    assert token is sentence[0]
    assert sentence.text == 'Hello, world.'


def test_use_integer_ids_for_any_strings(nlp, token):
    hello_id = nlp.vocab.strings['Hello']
    hello_str = nlp.vocab.strings[hello_id]

    assert token.orth  == hello_id  == 3404
    assert token.orth_ == hello_str == 'Hello'
