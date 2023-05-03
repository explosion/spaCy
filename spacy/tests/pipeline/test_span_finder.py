import pytest
from thinc.api import Config
from thinc.types import Ragged

from spacy.language import Language
from spacy.pipeline.span_finder import DEFAULT_PREDICTED_KEY, span_finder_default_config
from spacy.tokens import Doc
from spacy.training import Example
from spacy.util import registry

TRAINING_KEY = "pytest"


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
    example.reference.spans[TRAINING_KEY] = [example.reference.char_span(5, 9)]
    span_finder = nlp.add_pipe("span_finder", config={"training_key": TRAINING_KEY})
    nlp.initialize()

    truth_scores = span_finder._get_aligned_truth_scores([example])
    assert len(truth_scores) == len(tokens_predicted)
    assert truth_scores == reference_truths


def test_span_finder_model():
    nlp = Language()

    docs = [nlp("This is an example."), nlp("This is the second example.")]
    docs[0].spans[TRAINING_KEY] = [docs[0][3:4]]
    docs[1].spans[TRAINING_KEY] = [docs[1][3:5]]

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
    docs[0].spans[TRAINING_KEY] = [docs[0][3:4]]
    docs[1].spans[TRAINING_KEY] = [docs[1][3:5]]

    span_finder = nlp.add_pipe("span_finder", config={"training_key": TRAINING_KEY})
    nlp.initialize()
    docs = list(span_finder.pipe(docs))

    # TODO: update hard-coded name
    assert "span_candidates" in docs[0].spans


@pytest.mark.parametrize(
    "min_length, max_length, span_count",
    [(0, 0, 0), (None, None, 8), (2, None, 6), (None, 1, 2), (2, 3, 2)]
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
                    "training_key": TRAINING_KEY,
                },
            )
        return
    span_finder = nlp.add_pipe(
        "span_finder",
        config={
            "max_length": max_length,
            "min_length": min_length,
            "training_key": TRAINING_KEY,
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

    assert doc.spans[DEFAULT_PREDICTED_KEY]
    assert len(doc.spans[DEFAULT_PREDICTED_KEY]) == span_count

    # Assert below will fail when max_length is set to 0
    if max_length is None:
        max_length = float("inf")
    if min_length is None:
        min_length = 1

    assert all(
        min_length <= len(span) <= max_length
        for span in doc.spans[DEFAULT_PREDICTED_KEY]
    )


def test_span_finder_suggester():
    nlp = Language()
    docs = [nlp("This is an example."), nlp("This is the second example.")]
    docs[0].spans[TRAINING_KEY] = [docs[0][3:4]]
    docs[1].spans[TRAINING_KEY] = [docs[1][3:5]]
    span_finder = nlp.add_pipe("span_finder", config={"training_key": TRAINING_KEY})
    nlp.initialize()
    span_finder.set_annotations(docs, span_finder.predict(docs))

    suggester = registry.misc.get("spacy.span_finder_suggester.v1")(
        candidates_key="span_candidates"
    )

    candidates = suggester(docs)

    span_length = 0
    for doc in docs:
        span_length += len(doc.spans["span_candidates"])

    assert span_length == len(candidates.dataXd)
    assert type(candidates) == Ragged
    assert len(candidates.dataXd[0]) == 2
