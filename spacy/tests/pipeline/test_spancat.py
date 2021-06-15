from spacy.language import Language
from spacy.training import Example
from spacy.util import fix_random_seed


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
