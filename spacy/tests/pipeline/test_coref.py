import pytest
import spacy

from spacy import util
from spacy.training import Example
from spacy.lang.en import English
from spacy.tests.util import make_tempdir
from spacy.pipeline.coref import DEFAULT_CLUSTERS_PREFIX
from spacy.ml.models.coref_util import (
    select_non_crossing_spans,
    get_candidate_mentions,
    get_sentence_map,
)

# fmt: off
TRAIN_DATA = [
    (
        "Yes, I noticed that many friends around me received it. It seems that almost everyone received this SMS.",
        {
            "spans": {
                f"{DEFAULT_CLUSTERS_PREFIX}_1": [
                    (5, 6, "MENTION"),      # I
                    (40, 42, "MENTION"),    # me

                ],
                f"{DEFAULT_CLUSTERS_PREFIX}_2": [
                    (52, 54, "MENTION"),     # it
                    (95, 103, "MENTION"),    # this SMS
                ]
            }
        },
    ),
]
# fmt: on


@pytest.fixture
def nlp():
    return English()


@pytest.fixture
def snlp():
    en = English()
    en.add_pipe("sentencizer")
    return en


def test_add_pipe(nlp):
    nlp.add_pipe("coref")
    assert nlp.pipe_names == ["coref"]


def test_not_initialized(nlp):
    nlp.add_pipe("coref")
    text = "She gave me her pen."
    with pytest.raises(ValueError):
        nlp(text)


def test_initialized(nlp):
    nlp.add_pipe("coref")
    nlp.initialize()
    assert nlp.pipe_names == ["coref"]
    text = "She gave me her pen."
    doc = nlp(text)
    for k, v in doc.spans.items():
        # Ensure there are no "She, She, She, She, She, ..." problems
        assert len(v) <= 15


def test_initialized_short(nlp):
    nlp.add_pipe("coref")
    nlp.initialize()
    assert nlp.pipe_names == ["coref"]
    text = "Hi there"
    doc = nlp(text)
    print(doc.spans)


def test_initialized_2(nlp):
    nlp.add_pipe("coref")
    nlp.initialize()
    assert nlp.pipe_names == ["coref"]
    text = "She gave me her pen."
    # TODO: This crashes though it works when using intermediate var 'doc' !
    print(nlp(text).spans)


def test_coref_serialization(nlp):
    # Test that the coref component can be serialized
    nlp.add_pipe("coref", last=True)
    nlp.initialize()
    assert nlp.pipe_names == ["coref"]
    text = "She gave me her pen."
    doc = nlp(text)
    spans_result = doc.spans

    with make_tempdir() as tmp_dir:
        nlp.to_disk(tmp_dir)
        nlp2 = spacy.load(tmp_dir)
        assert nlp2.pipe_names == ["coref"]
        doc2 = nlp2(text)
        spans_result2 = doc2.spans
        print(1, [(k, len(v)) for k, v in spans_result.items()])
        print(2, [(k, len(v)) for k, v in spans_result2.items()])
        # Note: spans do not compare equal because docs are different and docs
        # use object identity for equality
        for k, v in spans_result.items():
            assert str(spans_result[k]) == str(spans_result2[k])
        # assert spans_result == spans_result2


def test_overfitting_IO(nlp):
    # Simple test to try and quickly overfit the senter - ensuring the ML models work correctly
    train_examples = []
    for text, annot in TRAIN_DATA:
        train_examples.append(Example.from_dict(nlp.make_doc(text), annot))

    nlp.add_pipe("coref")
    optimizer = nlp.initialize()
    test_text = TRAIN_DATA[0][0]
    doc = nlp(test_text)
    print("BEFORE", doc.spans)

    for i in range(5):
        losses = {}
        nlp.update(train_examples, sgd=optimizer, losses=losses)
        doc = nlp(test_text)
        print(i, doc.spans)
    print(losses["coref"])  # < 0.001

    # test the trained model
    doc = nlp(test_text)
    print("AFTER", doc.spans)

    # Also test the results are still the same after IO
    with make_tempdir() as tmp_dir:
        nlp.to_disk(tmp_dir)
        nlp2 = util.load_model_from_path(tmp_dir)
        doc2 = nlp2(test_text)
        print("doc2", doc2.spans)

    # Make sure that running pipe twice, or comparing to call, always amounts to the same predictions
    texts = [
        test_text,
        "I noticed many friends around me",
        "They received it. They received the SMS.",
    ]
    batch_deps_1 = [doc.spans for doc in nlp.pipe(texts)]
    print(batch_deps_1)
    batch_deps_2 = [doc.spans for doc in nlp.pipe(texts)]
    print(batch_deps_2)
    no_batch_deps = [doc.spans for doc in [nlp(text) for text in texts]]
    print(no_batch_deps)
    # assert_equal(batch_deps_1, batch_deps_2)
    # assert_equal(batch_deps_1, no_batch_deps)


def test_crossing_spans():
    starts = [6, 10, 0, 1, 0, 1, 0, 1, 2, 2, 2]
    ends = [12, 12, 2, 3, 3, 4, 4, 4, 3, 4, 5]
    idxs = list(range(len(starts)))
    limit = 5

    gold = sorted([0, 1, 2, 4, 6])
    guess = select_non_crossing_spans(idxs, starts, ends, limit)
    guess = sorted(guess)
    assert gold == guess


def test_mention_generator(snlp):
    nlp = snlp
    doc = nlp("I like text.")  # four tokens
    max_width = 20
    mentions = get_candidate_mentions(doc, max_width)
    assert len(mentions[0]) == 10

    # check multiple sentences
    doc = nlp("I like text. This is text.")  # eight tokens, two sents
    max_width = 20
    mentions = get_candidate_mentions(doc, max_width)
    assert len(mentions[0]) == 20


def test_sentence_map(snlp):
    doc = snlp("I like text. This is text.")
    sm = get_sentence_map(doc)
    assert sm == [0, 0, 0, 0, 1, 1, 1, 1]
