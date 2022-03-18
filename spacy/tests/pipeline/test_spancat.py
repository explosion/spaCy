import pytest
import numpy
from numpy.testing import assert_array_equal, assert_almost_equal
from thinc.api import get_current_ops, Ragged

from spacy import util
from spacy.lang.en import English
from spacy.language import Language
from spacy.tokens import SpanGroup
from spacy.tokens._dict_proxies import SpanGroups
from spacy.training import Example
from spacy.util import fix_random_seed, registry, make_tempdir

OPS = get_current_ops()

SPAN_KEY = "labeled_spans"

TRAIN_DATA = [
    ("Who is Shaka Khan?", {"spans": {SPAN_KEY: [(7, 17, "PERSON")]}}),
    (
        "I like London and Berlin.",
        {"spans": {SPAN_KEY: [(7, 13, "LOC"), (18, 24, "LOC")]}},
    ),
]

TRAIN_DATA_OVERLAPPING = [
    ("Who is Shaka Khan?", {"spans": {SPAN_KEY: [(7, 17, "PERSON")]}}),
    (
        "I like London and Berlin",
        {"spans": {SPAN_KEY: [(7, 13, "LOC"), (18, 24, "LOC"), (7, 24, "DOUBLE_LOC")]}},
    ),
    ("", {"spans": {SPAN_KEY: []}}),
]


def make_examples(nlp, data=TRAIN_DATA):
    train_examples = []
    for t in data:
        eg = Example.from_dict(nlp.make_doc(t[0]), t[1])
        train_examples.append(eg)
    return train_examples


def test_no_label():
    nlp = Language()
    nlp.add_pipe("spancat", config={"spans_key": SPAN_KEY})
    with pytest.raises(ValueError):
        nlp.initialize()


def test_no_resize():
    nlp = Language()
    spancat = nlp.add_pipe("spancat", config={"spans_key": SPAN_KEY})
    spancat.add_label("Thing")
    spancat.add_label("Phrase")
    assert spancat.labels == ("Thing", "Phrase")
    nlp.initialize()
    assert spancat.model.get_dim("nO") == 2
    # this throws an error because the spancat can't be resized after initialization
    with pytest.raises(ValueError):
        spancat.add_label("Stuff")


def test_implicit_labels():
    nlp = Language()
    spancat = nlp.add_pipe("spancat", config={"spans_key": SPAN_KEY})
    assert len(spancat.labels) == 0
    train_examples = make_examples(nlp)
    nlp.initialize(get_examples=lambda: train_examples)
    assert spancat.labels == ("PERSON", "LOC")


def test_explicit_labels():
    nlp = Language()
    spancat = nlp.add_pipe("spancat", config={"spans_key": SPAN_KEY})
    assert len(spancat.labels) == 0
    spancat.add_label("PERSON")
    spancat.add_label("LOC")
    nlp.initialize()
    assert spancat.labels == ("PERSON", "LOC")


# TODO figure out why this is flaky
@pytest.mark.skip(reason="Test is unreliable for unknown reason")
def test_doc_gc():
    # If the Doc object is garbage collected, the spans won't be functional afterwards
    nlp = Language()
    spancat = nlp.add_pipe("spancat", config={"spans_key": SPAN_KEY})
    spancat.add_label("PERSON")
    nlp.initialize()
    texts = [
        "Just a sentence.",
        "I like London and Berlin",
        "I like Berlin",
        "I eat ham.",
    ]
    all_spans = [doc.spans for doc in nlp.pipe(texts)]
    for text, spangroups in zip(texts, all_spans):
        assert isinstance(spangroups, SpanGroups)
        for key, spangroup in spangroups.items():
            assert isinstance(spangroup, SpanGroup)
            # XXX This fails with length 0 sometimes
            assert len(spangroup) > 0
            with pytest.raises(RuntimeError):
                span = spangroup[0]


@pytest.mark.parametrize(
    "max_positive,nr_results", [(None, 4), (1, 2), (2, 3), (3, 4), (4, 4)]
)
def test_make_spangroup(max_positive, nr_results):
    fix_random_seed(0)
    nlp = Language()
    spancat = nlp.add_pipe(
        "spancat",
        config={"spans_key": SPAN_KEY, "threshold": 0.5, "max_positive": max_positive},
    )
    doc = nlp.make_doc("Greater London")
    ngram_suggester = registry.misc.get("spacy.ngram_suggester.v1")(sizes=[1, 2])
    indices = ngram_suggester([doc])[0].dataXd
    assert_array_equal(OPS.to_numpy(indices), numpy.asarray([[0, 1], [1, 2], [0, 2]]))
    labels = ["Thing", "City", "Person", "GreatCity"]
    scores = numpy.asarray(
        [[0.2, 0.4, 0.3, 0.1], [0.1, 0.6, 0.2, 0.4], [0.8, 0.7, 0.3, 0.9]], dtype="f"
    )
    spangroup = spancat._make_span_group(doc, indices, scores, labels)
    assert len(spangroup) == nr_results

    # first span is always the second token "London"
    assert spangroup[0].text == "London"
    assert spangroup[0].label_ == "City"
    assert_almost_equal(0.6, spangroup.attrs["scores"][0], 5)

    # second span depends on the number of positives that were allowed
    assert spangroup[1].text == "Greater London"
    if max_positive == 1:
        assert spangroup[1].label_ == "GreatCity"
        assert_almost_equal(0.9, spangroup.attrs["scores"][1], 5)
    else:
        assert spangroup[1].label_ == "Thing"
        assert_almost_equal(0.8, spangroup.attrs["scores"][1], 5)

    if nr_results > 2:
        assert spangroup[2].text == "Greater London"
        if max_positive == 2:
            assert spangroup[2].label_ == "GreatCity"
            assert_almost_equal(0.9, spangroup.attrs["scores"][2], 5)
        else:
            assert spangroup[2].label_ == "City"
            assert_almost_equal(0.7, spangroup.attrs["scores"][2], 5)

    assert spangroup[-1].text == "Greater London"
    assert spangroup[-1].label_ == "GreatCity"
    assert_almost_equal(0.9, spangroup.attrs["scores"][-1], 5)


def test_ngram_suggester(en_tokenizer):
    # test different n-gram lengths
    for size in [1, 2, 3]:
        ngram_suggester = registry.misc.get("spacy.ngram_suggester.v1")(sizes=[size])
        docs = [
            en_tokenizer(text)
            for text in [
                "a",
                "a b",
                "a b c",
                "a b c d",
                "a b c d e",
                "a " * 100,
            ]
        ]
        ngrams = ngram_suggester(docs)
        # span sizes are correct
        for s in ngrams.data:
            assert s[1] - s[0] == size
        # spans are within docs
        offset = 0
        for i, doc in enumerate(docs):
            spans = ngrams.dataXd[offset : offset + ngrams.lengths[i]]
            spans_set = set()
            for span in spans:
                assert 0 <= span[0] < len(doc)
                assert 0 < span[1] <= len(doc)
                spans_set.add((int(span[0]), int(span[1])))
            # spans are unique
            assert spans.shape[0] == len(spans_set)
            offset += ngrams.lengths[i]
        # the number of spans is correct
        assert_array_equal(
            OPS.to_numpy(ngrams.lengths),
            [max(0, len(doc) - (size - 1)) for doc in docs],
        )

    # test 1-3-gram suggestions
    ngram_suggester = registry.misc.get("spacy.ngram_suggester.v1")(sizes=[1, 2, 3])
    docs = [
        en_tokenizer(text) for text in ["a", "a b", "a b c", "a b c d", "a b c d e"]
    ]
    ngrams = ngram_suggester(docs)
    assert_array_equal(OPS.to_numpy(ngrams.lengths), [1, 3, 6, 9, 12])
    assert_array_equal(
        OPS.to_numpy(ngrams.data),
        [
            # doc 0
            [0, 1],
            # doc 1
            [0, 1],
            [1, 2],
            [0, 2],
            # doc 2
            [0, 1],
            [1, 2],
            [2, 3],
            [0, 2],
            [1, 3],
            [0, 3],
            # doc 3
            [0, 1],
            [1, 2],
            [2, 3],
            [3, 4],
            [0, 2],
            [1, 3],
            [2, 4],
            [0, 3],
            [1, 4],
            # doc 4
            [0, 1],
            [1, 2],
            [2, 3],
            [3, 4],
            [4, 5],
            [0, 2],
            [1, 3],
            [2, 4],
            [3, 5],
            [0, 3],
            [1, 4],
            [2, 5],
        ],
    )

    # test some empty docs
    ngram_suggester = registry.misc.get("spacy.ngram_suggester.v1")(sizes=[1])
    docs = [en_tokenizer(text) for text in ["", "a", ""]]
    ngrams = ngram_suggester(docs)
    assert_array_equal(OPS.to_numpy(ngrams.lengths), [len(doc) for doc in docs])

    # test all empty docs
    ngram_suggester = registry.misc.get("spacy.ngram_suggester.v1")(sizes=[1])
    docs = [en_tokenizer(text) for text in ["", "", ""]]
    ngrams = ngram_suggester(docs)
    assert_array_equal(OPS.to_numpy(ngrams.lengths), [len(doc) for doc in docs])


def test_ngram_sizes(en_tokenizer):
    # test that the range suggester works well
    size_suggester = registry.misc.get("spacy.ngram_suggester.v1")(sizes=[1, 2, 3])
    suggester_factory = registry.misc.get("spacy.ngram_range_suggester.v1")
    range_suggester = suggester_factory(min_size=1, max_size=3)
    docs = [
        en_tokenizer(text) for text in ["a", "a b", "a b c", "a b c d", "a b c d e"]
    ]
    ngrams_1 = size_suggester(docs)
    ngrams_2 = range_suggester(docs)
    assert_array_equal(OPS.to_numpy(ngrams_1.lengths), [1, 3, 6, 9, 12])
    assert_array_equal(OPS.to_numpy(ngrams_1.lengths), OPS.to_numpy(ngrams_2.lengths))
    assert_array_equal(OPS.to_numpy(ngrams_1.data), OPS.to_numpy(ngrams_2.data))

    # one more variation
    suggester_factory = registry.misc.get("spacy.ngram_range_suggester.v1")
    range_suggester = suggester_factory(min_size=2, max_size=4)
    ngrams_3 = range_suggester(docs)
    assert_array_equal(OPS.to_numpy(ngrams_3.lengths), [0, 1, 3, 6, 9])


def test_overfitting_IO():
    # Simple test to try and quickly overfit the spancat component - ensuring the ML models work correctly
    fix_random_seed(0)
    nlp = English()
    spancat = nlp.add_pipe("spancat", config={"spans_key": SPAN_KEY})
    train_examples = make_examples(nlp)
    optimizer = nlp.initialize(get_examples=lambda: train_examples)
    assert spancat.model.get_dim("nO") == 2
    assert set(spancat.labels) == {"LOC", "PERSON"}

    for i in range(50):
        losses = {}
        nlp.update(train_examples, sgd=optimizer, losses=losses)
    assert losses["spancat"] < 0.01

    # test the trained model
    test_text = "I like London and Berlin"
    doc = nlp(test_text)
    assert doc.spans[spancat.key] == doc.spans[SPAN_KEY]
    spans = doc.spans[SPAN_KEY]
    assert len(spans) == 2
    assert len(spans.attrs["scores"]) == 2
    assert min(spans.attrs["scores"]) > 0.9
    assert set([span.text for span in spans]) == {"London", "Berlin"}
    assert set([span.label_ for span in spans]) == {"LOC"}

    # Also test the results are still the same after IO
    with make_tempdir() as tmp_dir:
        nlp.to_disk(tmp_dir)
        nlp2 = util.load_model_from_path(tmp_dir)
        doc2 = nlp2(test_text)
        spans2 = doc2.spans[SPAN_KEY]
        assert len(spans2) == 2
        assert len(spans2.attrs["scores"]) == 2
        assert min(spans2.attrs["scores"]) > 0.9
        assert set([span.text for span in spans2]) == {"London", "Berlin"}
        assert set([span.label_ for span in spans2]) == {"LOC"}

    # Test scoring
    scores = nlp.evaluate(train_examples)
    assert f"spans_{SPAN_KEY}_f" in scores
    assert scores[f"spans_{SPAN_KEY}_p"] == 1.0
    assert scores[f"spans_{SPAN_KEY}_r"] == 1.0
    assert scores[f"spans_{SPAN_KEY}_f"] == 1.0

    # also test that the spancat works for just a single entity in a sentence
    doc = nlp("London")
    assert len(doc.spans[spancat.key]) == 1


def test_overfitting_IO_overlapping():
    # Test for overfitting on overlapping entities
    fix_random_seed(0)
    nlp = English()
    spancat = nlp.add_pipe("spancat", config={"spans_key": SPAN_KEY})

    train_examples = make_examples(nlp, data=TRAIN_DATA_OVERLAPPING)
    optimizer = nlp.initialize(get_examples=lambda: train_examples)
    assert spancat.model.get_dim("nO") == 3
    assert set(spancat.labels) == {"PERSON", "LOC", "DOUBLE_LOC"}

    for i in range(50):
        losses = {}
        nlp.update(train_examples, sgd=optimizer, losses=losses)
    assert losses["spancat"] < 0.01

    # test the trained model
    test_text = "I like London and Berlin"
    doc = nlp(test_text)
    spans = doc.spans[SPAN_KEY]
    assert len(spans) == 3
    assert len(spans.attrs["scores"]) == 3
    assert min(spans.attrs["scores"]) > 0.9
    assert set([span.text for span in spans]) == {
        "London",
        "Berlin",
        "London and Berlin",
    }
    assert set([span.label_ for span in spans]) == {"LOC", "DOUBLE_LOC"}

    # Also test the results are still the same after IO
    with make_tempdir() as tmp_dir:
        nlp.to_disk(tmp_dir)
        nlp2 = util.load_model_from_path(tmp_dir)
        doc2 = nlp2(test_text)
        spans2 = doc2.spans[SPAN_KEY]
        assert len(spans2) == 3
        assert len(spans2.attrs["scores"]) == 3
        assert min(spans2.attrs["scores"]) > 0.9
        assert set([span.text for span in spans2]) == {
            "London",
            "Berlin",
            "London and Berlin",
        }
        assert set([span.label_ for span in spans2]) == {"LOC", "DOUBLE_LOC"}


def test_zero_suggestions():
    # Test with a suggester that returns 0 suggestions

    @registry.misc("test_zero_suggester")
    def make_zero_suggester():
        def zero_suggester(docs, *, ops=None):
            if ops is None:
                ops = get_current_ops()
            return Ragged(
                ops.xp.zeros((0, 0), dtype="i"), ops.xp.zeros((len(docs),), dtype="i")
            )

        return zero_suggester

    fix_random_seed(0)
    nlp = English()
    spancat = nlp.add_pipe(
        "spancat",
        config={"suggester": {"@misc": "test_zero_suggester"}, "spans_key": SPAN_KEY},
    )
    train_examples = make_examples(nlp)
    optimizer = nlp.initialize(get_examples=lambda: train_examples)
    assert spancat.model.get_dim("nO") == 2
    assert set(spancat.labels) == {"LOC", "PERSON"}

    nlp.update(train_examples, sgd=optimizer)


def test_set_candidates():
    nlp = Language()
    spancat = nlp.add_pipe("spancat", config={"spans_key": SPAN_KEY})
    train_examples = make_examples(nlp)
    nlp.initialize(get_examples=lambda: train_examples)
    texts = [
        "Just a sentence.",
        "I like London and Berlin",
        "I like Berlin",
        "I eat ham.",
    ]

    docs = [nlp(text) for text in texts]
    spancat.set_candidates(docs)

    assert len(docs) == len(texts)
    assert type(docs[0].spans["candidates"]) == SpanGroup
    assert len(docs[0].spans["candidates"]) == 9
    assert docs[0].spans["candidates"][0].text == "Just"
    assert docs[0].spans["candidates"][4].text == "Just a"
