import pytest
from thinc.api import Config

from spacy import util
from spacy.lang.en import English
from spacy.language import Language
from spacy.pipeline.span_finder import span_finder_default_config
from spacy.tokens import Doc
from spacy.training import Example
from spacy.util import fix_random_seed, make_tempdir, registry

SPANS_KEY = "pytest"
TRAIN_DATA = [
    ("Who is Shaka Khan?", {"spans": {SPANS_KEY: [(7, 17)]}}),
    (
        "I like London and Berlin.",
        {"spans": {SPANS_KEY: [(7, 13), (18, 24)]}},
    ),
]

TRAIN_DATA_OVERLAPPING = [
    ("Who is Shaka Khan?", {"spans": {SPANS_KEY: [(7, 17)]}}),
    (
        "I like London and Berlin",
        {"spans": {SPANS_KEY: [(7, 13), (18, 24), (7, 24)]}},
    ),
    ("", {"spans": {SPANS_KEY: []}}),
]


def make_examples(nlp, data=TRAIN_DATA):
    train_examples = []
    for t in data:
        eg = Example.from_dict(nlp.make_doc(t[0]), t[1])
        train_examples.append(eg)
    return train_examples


@pytest.mark.parametrize(
    "tokens_predicted, tokens_reference, reference_truths",
    [
        (
            ["Mon", ".", "-", "June", "16"],
            ["Mon.", "-", "June", "16"],
            [(0, 0), (0, 0), (0, 0), (1, 1), (0, 0)],
        ),
        (
            ["Mon.", "-", "J", "une", "16"],
            ["Mon.", "-", "June", "16"],
            [(0, 0), (0, 0), (1, 0), (0, 1), (0, 0)],
        ),
        (
            ["Mon", ".", "-", "June", "16"],
            ["Mon.", "-", "June", "1", "6"],
            [(0, 0), (0, 0), (0, 0), (1, 1), (0, 0)],
        ),
        (
            ["Mon.", "-J", "un", "e 16"],
            ["Mon.", "-", "June", "16"],
            [(0, 0), (0, 0), (0, 0), (0, 0)],
        ),
        pytest.param(
            ["Mon.-June", "16"],
            ["Mon.", "-", "June", "16"],
            [(0, 1), (0, 0)],
        ),
        pytest.param(
            ["Mon.-", "June", "16"],
            ["Mon.", "-", "J", "une", "16"],
            [(0, 0), (1, 1), (0, 0)],
        ),
        pytest.param(
            ["Mon.-", "June 16"],
            ["Mon.", "-", "June", "16"],
            [(0, 0), (1, 0)],
        ),
    ],
)
def test_loss_alignment_example(tokens_predicted, tokens_reference, reference_truths):
    nlp = Language()
    predicted = Doc(
        nlp.vocab, words=tokens_predicted, spaces=[False] * len(tokens_predicted)
    )
    reference = Doc(
        nlp.vocab, words=tokens_reference, spaces=[False] * len(tokens_reference)
    )
    example = Example(predicted, reference)
    example.reference.spans[SPANS_KEY] = [example.reference.char_span(5, 9)]
    span_finder = nlp.add_pipe("span_finder", config={"spans_key": SPANS_KEY})
    nlp.initialize()
    ops = span_finder.model.ops
    if predicted.text != reference.text:
        with pytest.raises(
            ValueError, match="must match between reference and predicted"
        ):
            span_finder._get_aligned_truth_scores([example], ops)
        return
    truth_scores, masks = span_finder._get_aligned_truth_scores([example], ops)
    assert len(truth_scores) == len(tokens_predicted)
    ops.xp.testing.assert_array_equal(truth_scores, ops.xp.asarray(reference_truths))


def test_span_finder_model():
    nlp = Language()

    docs = [nlp("This is an example."), nlp("This is the second example.")]
    docs[0].spans[SPANS_KEY] = [docs[0][3:4]]
    docs[1].spans[SPANS_KEY] = [docs[1][3:5]]

    total_tokens = 0
    for doc in docs:
        total_tokens += len(doc)

    config = Config().from_str(span_finder_default_config).interpolate()
    model = registry.resolve(config)["model"]

    model.initialize(X=docs)
    predictions = model.predict(docs)

    assert len(predictions) == total_tokens
    assert len(predictions[0]) == 2


def test_span_finder_component():
    nlp = Language()

    docs = [nlp("This is an example."), nlp("This is the second example.")]
    docs[0].spans[SPANS_KEY] = [docs[0][3:4]]
    docs[1].spans[SPANS_KEY] = [docs[1][3:5]]

    span_finder = nlp.add_pipe("span_finder", config={"spans_key": SPANS_KEY})
    nlp.initialize()
    docs = list(span_finder.pipe(docs))

    assert SPANS_KEY in docs[0].spans


@pytest.mark.parametrize(
    "min_length, max_length, span_count",
    [(0, 0, 0), (None, None, 8), (2, None, 6), (None, 1, 2), (2, 3, 2)],
)
def test_set_annotations_span_lengths(min_length, max_length, span_count):
    nlp = Language()
    doc = nlp("Me and Jenny goes together like peas and carrots.")
    if min_length == 0 and max_length == 0:
        with pytest.raises(ValueError, match="Both 'min_length' and 'max_length'"):
            span_finder = nlp.add_pipe(
                "span_finder",
                config={
                    "max_length": max_length,
                    "min_length": min_length,
                    "spans_key": SPANS_KEY,
                },
            )
        return
    span_finder = nlp.add_pipe(
        "span_finder",
        config={
            "max_length": max_length,
            "min_length": min_length,
            "spans_key": SPANS_KEY,
        },
    )
    nlp.initialize()
    # Starts    [Me, Jenny, peas]
    # Ends      [Jenny, peas, carrots]
    scores = [
        (1, 0),
        (0, 0),
        (1, 1),
        (0, 0),
        (0, 0),
        (0, 0),
        (1, 1),
        (0, 0),
        (0, 1),
        (0, 0),
    ]
    span_finder.set_annotations([doc], scores)

    assert doc.spans[SPANS_KEY]
    assert len(doc.spans[SPANS_KEY]) == span_count

    # Assert below will fail when max_length is set to 0
    if max_length is None:
        max_length = float("inf")
    if min_length is None:
        min_length = 1

    assert all(min_length <= len(span) <= max_length for span in doc.spans[SPANS_KEY])


def test_overfitting_IO():
    # Simple test to try and quickly overfit the span_finder component - ensuring the ML models work correctly
    fix_random_seed(0)
    nlp = English()
    span_finder = nlp.add_pipe("span_finder", config={"spans_key": SPANS_KEY})
    train_examples = make_examples(nlp)
    optimizer = nlp.initialize(get_examples=lambda: train_examples)
    assert span_finder.model.get_dim("nO") == 2

    for i in range(50):
        losses = {}
        nlp.update(train_examples, sgd=optimizer, losses=losses)
    assert losses["span_finder"] < 0.001

    # test the trained model
    test_text = "I like London and Berlin"
    doc = nlp(test_text)
    spans = doc.spans[SPANS_KEY]
    assert len(spans) == 3
    assert set([span.text for span in spans]) == {
        "London",
        "Berlin",
        "London and Berlin",
    }

    # Also test the results are still the same after IO
    with make_tempdir() as tmp_dir:
        nlp.to_disk(tmp_dir)
        nlp2 = util.load_model_from_path(tmp_dir)
        doc2 = nlp2(test_text)
        spans2 = doc2.spans[SPANS_KEY]
        assert len(spans2) == 3
        assert set([span.text for span in spans2]) == {
            "London",
            "Berlin",
            "London and Berlin",
        }

    # Test scoring
    scores = nlp.evaluate(train_examples)
    assert f"spans_{SPANS_KEY}_f" in scores
    # It's not perfect 1.0 F1 because it's designed to overgenerate for now.
    assert scores[f"spans_{SPANS_KEY}_p"] == 0.75
    assert scores[f"spans_{SPANS_KEY}_r"] == 1.0

    # also test that the spancat works for just a single entity in a sentence
    doc = nlp("London")
    assert len(doc.spans[SPANS_KEY]) == 1
