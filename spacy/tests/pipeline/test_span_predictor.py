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
    spans2ints,
)

from thinc.util import has_torch

# fmt: off
TRAIN_DATA = [
    (
        "John Smith picked up the red ball and he threw it away.",
        {
            "spans": {
                f"{DEFAULT_CLUSTER_PREFIX}_1": [
                    (0, 11, "MENTION"),      # John Smith
                    (38, 41, "MENTION"),     # he

                ],
                f"{DEFAULT_CLUSTER_PREFIX}_2": [
                    (25, 33, "MENTION"),     # red ball
                    (47, 50, "MENTION"),     # it
                ],
                f"coref_head_clusters_1": [
                    (5, 11, "MENTION"),      # Smith
                    (38, 41, "MENTION"),     # he

                ],
                f"coref_head_clusters_2": [
                    (29, 33, "MENTION"),     # red ball
                    (47, 50, "MENTION"),     # it
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
    nlp.add_pipe("span_predictor")
    assert nlp.pipe_names == ["span_predictor"]


@pytest.mark.skipif(not has_torch, reason="Torch not available")
def test_not_initialized(nlp):
    nlp.add_pipe("span_predictor")
    text = "She gave me her pen."
    with pytest.raises(ValueError, match="E109"):
        nlp(text)


@pytest.mark.skipif(not has_torch, reason="Torch not available")
def test_span_predictor_serialization(nlp):
    # Test that the span predictor component can be serialized
    nlp.add_pipe("span_predictor", last=True)
    nlp.initialize()
    assert nlp.pipe_names == ["span_predictor"]
    text = "She gave me her pen."
    doc = nlp(text)

    with make_tempdir() as tmp_dir:
        nlp.to_disk(tmp_dir)
        nlp2 = spacy.load(tmp_dir)
        assert nlp2.pipe_names == ["span_predictor"]
        doc2 = nlp2(text)

        assert spans2ints(doc) == spans2ints(doc2)


@pytest.mark.skipif(not has_torch, reason="Torch not available")
def test_overfitting_IO(nlp):
    # Simple test to try and quickly overfit - ensuring the ML models work correctly
    train_examples = []
    for text, annot in TRAIN_DATA:
        train_examples.append(Example.from_dict(nlp.make_doc(text), annot))

    nlp.add_pipe("span_predictor")
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
    assert spans2ints(docs1[0]) == spans2ints(docs2[0])
    assert spans2ints(docs1[0]) == spans2ints(docs3[0])
