import pytest
from numpy.testing import assert_equal
from spacy.language import Language
from spacy.training import Example
from spacy.util import fix_random_seed, registry


SPAN_KEY = "labeled_spans"

TRAIN_DATA = [
    ("Who is Shaka Khan?", {"spans": {SPAN_KEY: [(7, 17, "PERSON")]}}),
    (
        "I like London and Berlin.",
        {"spans": {SPAN_KEY: [(7, 13, "LOC"), (18, 24, "LOC")]}},
    ),
]


def make_get_examples(nlp):
    train_examples = []
    for t in TRAIN_DATA:
        eg = Example.from_dict(nlp.make_doc(t[0]), t[1])
        train_examples.append(eg)

    def get_examples():
        return train_examples

    return get_examples


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
    train_examples = []
    for t in TRAIN_DATA:
        train_examples.append(Example.from_dict(nlp.make_doc(t[0]), t[1]))
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


def test_simple_train():
    fix_random_seed(0)
    nlp = Language()
    spancat = nlp.add_pipe("spancat", config={"spans_key": SPAN_KEY})
    get_examples = make_get_examples(nlp)
    nlp.initialize(get_examples)
    sgd = nlp.create_optimizer()
    assert len(spancat.labels) != 0
    for i in range(40):
        losses = {}
        nlp.update(list(get_examples()), losses=losses, drop=0.1, sgd=sgd)
    doc = nlp("I like London and Berlin.")
    assert doc.spans[spancat.key] == doc.spans[SPAN_KEY]
    assert len(doc.spans[spancat.key]) == 2
    assert doc.spans[spancat.key][0].text == "London"
    scores = nlp.evaluate(get_examples())
    assert f"spans_{SPAN_KEY}_f" in scores
    assert scores[f"spans_{SPAN_KEY}_f"] == 1.0


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
                spans_set.add((span[0], span[1]))
            # spans are unique
            assert spans.shape[0] == len(spans_set)
            offset += ngrams.lengths[i]
        # the number of spans is correct
        assert_equal(ngrams.lengths, [max(0, len(doc) - (size - 1)) for doc in docs])

    # test 1-3-gram suggestions
    ngram_suggester = registry.misc.get("spacy.ngram_suggester.v1")(sizes=[1, 2, 3])
    docs = [
        en_tokenizer(text) for text in ["a", "a b", "a b c", "a b c d", "a b c d e"]
    ]
    ngrams = ngram_suggester(docs)
    assert_equal(ngrams.lengths, [1, 3, 6, 9, 12])
    assert_equal(
        ngrams.data,
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
    assert_equal(ngrams.lengths, [len(doc) for doc in docs])

    # test all empty docs
    ngram_suggester = registry.misc.get("spacy.ngram_suggester.v1")(sizes=[1])
    docs = [en_tokenizer(text) for text in ["", "", ""]]
    ngrams = ngram_suggester(docs)
    assert_equal(ngrams.lengths, [len(doc) for doc in docs])


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
    assert_equal(ngrams_1.lengths, [1, 3, 6, 9, 12])
    assert_equal(ngrams_1.lengths, ngrams_2.lengths)
    assert_equal(ngrams_1.data, ngrams_2.data)

    # one more variation
    suggester_factory = registry.misc.get("spacy.ngram_range_suggester.v1")
    range_suggester = suggester_factory(min_size=2, max_size=4)
    ngrams_3 = range_suggester(docs)
    assert_equal(ngrams_3.lengths, [0, 1, 3, 6, 9])
