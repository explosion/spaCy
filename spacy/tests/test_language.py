import itertools
import pytest
from spacy.language import Language
from spacy.tokens import Doc, Span
from spacy.vocab import Vocab

from .util import add_vecs_to_vocab, assert_docs_equal
from ..gold import Example


@pytest.fixture
def nlp():
    nlp = Language(Vocab())
    textcat = nlp.create_pipe("textcat")
    for label in ("POSITIVE", "NEGATIVE"):
        textcat.add_label(label)
    nlp.add_pipe(textcat)
    nlp.begin_training()
    return nlp


def test_language_update(nlp):
    text = "hello world"
    annots = {"cats": {"POSITIVE": 1.0, "NEGATIVE": 0.0}}
    wrongkeyannots = {"LABEL": True}
    doc = Doc(nlp.vocab, words=text.split(" "))
    example = Example.from_dict(doc, annots)
    nlp.update([example])

    # Not allowed to call with just one Example
    with pytest.raises(TypeError):
        nlp.update(example)

    # Update with text and dict: not supported anymore since v.3
    with pytest.raises(TypeError):
        nlp.update((text, annots))
    # Update with doc object and dict
    with pytest.raises(TypeError):
        nlp.update((doc, annots))

    # Create examples badly
    with pytest.raises(ValueError):
        example = Example.from_dict(doc, None)
    with pytest.raises(KeyError):
        example = Example.from_dict(doc, wrongkeyannots)


def test_language_evaluate(nlp):
    text = "hello world"
    annots = {"doc_annotation": {"cats": {"POSITIVE": 1.0, "NEGATIVE": 0.0}}}
    doc = Doc(nlp.vocab, words=text.split(" "))
    example = Example.from_dict(doc, annots)
    nlp.evaluate([example])

    # Not allowed to call with just one Example
    with pytest.raises(TypeError):
        nlp.evaluate(example)

    # Evaluate with text and dict: not supported anymore since v.3
    with pytest.raises(TypeError):
        nlp.evaluate([(text, annots)])
    # Evaluate with doc object and dict
    with pytest.raises(TypeError):
        nlp.evaluate([(doc, annots)])
    with pytest.raises(TypeError):
        nlp.evaluate([text, annots])


def test_evaluate_no_pipe(nlp):
    """Test that docs are processed correctly within Language.pipe if the
    component doesn't expose a .pipe method."""

    def pipe(doc):
        return doc

    text = "hello world"
    annots = {"cats": {"POSITIVE": 1.0, "NEGATIVE": 0.0}}
    nlp = Language(Vocab())
    doc = nlp(text)
    nlp.add_pipe(pipe)
    nlp.evaluate([Example.from_dict(doc, annots)])


def vector_modification_pipe(doc):
    doc.vector += 1
    return doc


def userdata_pipe(doc):
    doc.user_data["foo"] = "bar"
    return doc


def ner_pipe(doc):
    span = Span(doc, 0, 1, label="FIRST")
    doc.ents += (span,)
    return doc


@pytest.fixture
def sample_vectors():
    return [
        ("spacy", [-0.1, -0.2, -0.3]),
        ("world", [-0.2, -0.3, -0.4]),
        ("pipe", [0.7, 0.8, 0.9]),
    ]


@pytest.fixture
def nlp2(nlp, sample_vectors):
    add_vecs_to_vocab(nlp.vocab, sample_vectors)
    nlp.add_pipe(vector_modification_pipe)
    nlp.add_pipe(ner_pipe)
    nlp.add_pipe(userdata_pipe)
    return nlp


@pytest.fixture
def texts():
    data = [
        "Hello world.",
        "This is spacy.",
        "You can use multiprocessing with pipe method.",
        "Please try!",
    ]
    return data


@pytest.mark.parametrize("n_process", [1, 2])
def test_language_pipe(nlp2, n_process, texts):
    texts = texts * 10
    expecteds = [nlp2(text) for text in texts]
    docs = nlp2.pipe(texts, n_process=n_process, batch_size=2)

    for doc, expected_doc in zip(docs, expecteds):
        assert_docs_equal(doc, expected_doc)


@pytest.mark.parametrize("n_process", [1, 2])
def test_language_pipe_stream(nlp2, n_process, texts):
    # check if nlp.pipe can handle infinite length iterator properly.
    stream_texts = itertools.cycle(texts)
    texts0, texts1 = itertools.tee(stream_texts)
    expecteds = (nlp2(text) for text in texts0)
    docs = nlp2.pipe(texts1, n_process=n_process, batch_size=2)

    n_fetch = 20
    for doc, expected_doc in itertools.islice(zip(docs, expecteds), n_fetch):
        assert_docs_equal(doc, expected_doc)
