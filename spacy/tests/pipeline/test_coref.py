import pytest
import spacy

from spacy import util
from spacy.training import Example
from spacy.lang.en import English
from spacy.tests.util import make_tempdir
from spacy.ml.models.coref_util import (
    DEFAULT_CLUSTER_PREFIX,
    select_non_crossing_spans,
    get_sentence_ids,
    get_clusters_from_doc,
)

from thinc.util import has_torch

# fmt: off
TRAIN_DATA = [
    (
        "Yes, I noticed that many friends around me received it. It seems that almost everyone received this SMS.",
        {
            "spans": {
                f"{DEFAULT_CLUSTER_PREFIX}_1": [
                    (5, 6, "MENTION"),      # I
                    (40, 42, "MENTION"),    # me

                ],
                f"{DEFAULT_CLUSTER_PREFIX}_2": [
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


@pytest.mark.skipif(not has_torch, reason="Torch not available")
def test_add_pipe(nlp):
    nlp.add_pipe("coref")
    assert nlp.pipe_names == ["coref"]


@pytest.mark.skipif(not has_torch, reason="Torch not available")
def test_not_initialized(nlp):
    nlp.add_pipe("coref")
    text = "She gave me her pen."
    with pytest.raises(ValueError, match="E109"):
        nlp(text)


@pytest.mark.skipif(not has_torch, reason="Torch not available")
def test_initialized(nlp):
    nlp.add_pipe("coref")
    nlp.initialize()
    assert nlp.pipe_names == ["coref"]
    text = "She gave me her pen."
    doc = nlp(text)
    for k, v in doc.spans.items():
        # Ensure there are no "She, She, She, She, She, ..." problems
        assert len(v) <= 15


@pytest.mark.skipif(not has_torch, reason="Torch not available")
def test_initialized_short(nlp):
    nlp.add_pipe("coref")
    nlp.initialize()
    assert nlp.pipe_names == ["coref"]
    text = "Hi there"
    doc = nlp(text)


@pytest.mark.skipif(not has_torch, reason="Torch not available")
def test_coref_serialization(nlp):
    # Test that the coref component can be serialized
    nlp.add_pipe("coref", last=True)
    nlp.initialize()
    assert nlp.pipe_names == ["coref"]
    text = "She gave me her pen."
    doc = nlp(text)

    with make_tempdir() as tmp_dir:
        nlp.to_disk(tmp_dir)
        nlp2 = spacy.load(tmp_dir)
        assert nlp2.pipe_names == ["coref"]
        doc2 = nlp2(text)

        assert get_clusters_from_doc(doc) == get_clusters_from_doc(doc2)


@pytest.mark.skipif(not has_torch, reason="Torch not available")
def test_overfitting_IO(nlp):
    # Simple test to try and quickly overfit - ensuring the ML models work correctly
    train_examples = []
    for text, annot in TRAIN_DATA:
        train_examples.append(Example.from_dict(nlp.make_doc(text), annot))

    nlp.add_pipe("coref")
    optimizer = nlp.initialize()
    test_text = TRAIN_DATA[0][0]
    doc = nlp(test_text)

    # Needs ~12 epochs to converge
    for i in range(15):
        losses = {}
        nlp.update(train_examples, sgd=optimizer, losses=losses)
        doc = nlp(test_text)

    # test the trained model
    doc = nlp(test_text)

    # Also test the results are still the same after IO
    with make_tempdir() as tmp_dir:
        nlp.to_disk(tmp_dir)
        nlp2 = util.load_model_from_path(tmp_dir)
        doc2 = nlp2(test_text)

    # Make sure that running pipe twice, or comparing to call, always amounts to the same predictions
    texts = [
        test_text,
        "I noticed many friends around me",
        "They received it. They received the SMS.",
    ]
    docs1 = list(nlp.pipe(texts))
    docs2 = list(nlp.pipe(texts))
    docs3 = [nlp(text) for text in texts]
    assert get_clusters_from_doc(docs1[0]) == get_clusters_from_doc(docs2[0])
    assert get_clusters_from_doc(docs1[0]) == get_clusters_from_doc(docs3[0])


@pytest.mark.skipif(not has_torch, reason="Torch not available")
def test_tokenization_mismatch(nlp):
    train_examples = []
    for text, annot in TRAIN_DATA:
        eg = Example.from_dict(nlp.make_doc(text), annot)
        ref = eg.reference
        char_spans = {}
        for key, cluster in ref.spans.items():
            char_spans[key] = []
            for span in cluster:
                char_spans[key].append((span[0].idx, span[-1].idx + len(span[-1])))
        with ref.retokenize() as retokenizer:
            # merge "many friends"
            retokenizer.merge(ref[5:7])

        # Note this works because it's the same doc and we know the keys
        for key, _ in ref.spans.items():
            spans = char_spans[key]
            ref.spans[key] = [ref.char_span(*span) for span in spans]

        train_examples.append(eg)

    nlp.add_pipe("coref")
    optimizer = nlp.initialize()
    test_text = TRAIN_DATA[0][0]
    doc = nlp(test_text)

    for i in range(15):
        losses = {}
        nlp.update(train_examples, sgd=optimizer, losses=losses)
        doc = nlp(test_text)

    # test the trained model
    doc = nlp(test_text)

    # Also test the results are still the same after IO
    with make_tempdir() as tmp_dir:
        nlp.to_disk(tmp_dir)
        nlp2 = util.load_model_from_path(tmp_dir)
        doc2 = nlp2(test_text)

    # Make sure that running pipe twice, or comparing to call, always amounts to the same predictions
    texts = [
        test_text,
        "I noticed many friends around me",
        "They received it. They received the SMS.",
    ]

    # save the docs so they don't get garbage collected
    docs1 = list(nlp.pipe(texts))
    docs2 = list(nlp.pipe(texts))
    docs3 = [nlp(text) for text in texts]
    assert get_clusters_from_doc(docs1[0]) == get_clusters_from_doc(docs2[0])
    assert get_clusters_from_doc(docs1[0]) == get_clusters_from_doc(docs3[0])


@pytest.mark.skipif(not has_torch, reason="Torch not available")
def test_crossing_spans():
    starts = [6, 10, 0, 1, 0, 1, 0, 1, 2, 2, 2]
    ends = [12, 12, 2, 3, 3, 4, 4, 4, 3, 4, 5]
    idxs = list(range(len(starts)))
    limit = 5

    gold = sorted([0, 1, 2, 4, 6])
    guess = select_non_crossing_spans(idxs, starts, ends, limit)
    guess = sorted(guess)
    assert gold == guess


@pytest.mark.skipif(not has_torch, reason="Torch not available")
def test_sentence_map(snlp):
    doc = snlp("I like text. This is text.")
    sm = get_sentence_ids(doc)
    assert sm == [0, 0, 0, 0, 1, 1, 1, 1]


@pytest.mark.skipif(not has_torch, reason="Torch not available")
def test_whitespace_mismatch(nlp):
    train_examples = []
    for text, annot in TRAIN_DATA:
        eg = Example.from_dict(nlp.make_doc(text), annot)
        eg.predicted = nlp.make_doc("  " + text)
        train_examples.append(eg)

    nlp.add_pipe("coref")
    optimizer = nlp.initialize()
    test_text = TRAIN_DATA[0][0]
    doc = nlp(test_text)

    with pytest.raises(ValueError, match="whitespace"):
        nlp.update(train_examples, sgd=optimizer)
