import pytest
from spacy import util
from spacy.training import Example
from spacy.lang.en import English
from spacy.tests.util import make_tempdir
from spacy.pipeline.coref import DEFAULT_CLUSTERS_PREFIX

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
    # TODO: The results of this are weird & non-deterministic
    print(doc.spans)


def test_initialized_short(nlp):
    nlp.add_pipe("coref")
    nlp.initialize()
    assert nlp.pipe_names == ["coref"]
    text = "Hi there"
    # TODO: this crashes with an IndexError: too many indices
    doc = nlp(text)
    print(doc.spans)


def test_initialized_2(nlp):
    nlp.add_pipe("coref")
    nlp.initialize()
    assert nlp.pipe_names == ["coref"]
    text = "She gave me her pen."
    # TODO: This crashes though it works when using intermediate var 'doc' !
    print(nlp(text).spans)


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
    print(losses["coref"]) # < 0.001

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
