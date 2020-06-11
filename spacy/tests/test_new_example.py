import pytest
from spacy.gold.new_example import NewExample as Example
from spacy.tokens import Doc
from spacy.vocab import Vocab


def test_Example_init_requires_doc_objects():
    vocab = Vocab()
    with pytest.raises(TypeError):
        eg = Example(None, None)
    with pytest.raises(TypeError):
        eg = Example(Doc(vocab, words=["hi"]), None)
    with pytest.raises(TypeError):
        eg = Example(None, Doc(vocab, words=["hi"]))


def test_Example_from_dict_basic():
    eg = Example.from_dict(
        Doc(Vocab(), words=["hello", "world"]), {"words": ["hello", "world"]}
    )
    assert isinstance(eg.x, Doc)
    assert isinstance(eg.y, Doc)


@pytest.mark.parametrize(
    "annots", [{"words": ["ice", "cream"], "weirdannots": ["something", "such"]}]
)
def test_Example_from_dict_invalid(annots):
    vocab = Vocab()
    predicted = Doc(vocab, words=annots["words"])
    with pytest.raises(ValueError):
        eg = Example.from_dict(predicted, annots)


@pytest.mark.parametrize("annots", [{"words": ["ice", "cream"], "tags": ["NN", "NN"]}])
def test_Example_from_dict_with_tags(annots):
    vocab = Vocab()
    predicted = Doc(vocab, words=annots["words"])
    eg = Example.from_dict(predicted, annots)
    for i, token in enumerate(eg.reference):
        assert token.tag_ == annots["tags"][i]


@pytest.mark.xfail(reason="TODO - fix")
@pytest.mark.parametrize(
    "annots",
    [
        {
            "words": ["I", "like", "London", "and", "Berlin", "."],
            "entities": [(7, 13, "LOC"), (18, 24, "LOC")],
        }
    ],
)
def test_Example_from_dict_with_entities(annots):
    vocab = Vocab()
    predicted = Doc(vocab, words=annots["words"])
    eg = Example.from_dict(predicted, annots)
    assert len(list(eg.reference.ents)) == 2


@pytest.mark.parametrize(
    "annots",
    [
        {
            "words": ["I", "like", "London", "and", "Berlin", "."],
            "deps": ["nsubj", "ROOT", "dobj", "cc", "conj", "punct"],
            "heads": [1, 1, 1, 2, 2, 1],
        }
    ],
)
def test_Example_from_dict_with_parse(annots):
    vocab = Vocab()
    predicted = Doc(vocab, words=annots["words"])
    eg = Example.from_dict(predicted, annots)
    for i, token in enumerate(eg.reference):
        assert token.dep_ == annots["deps"][i]
        assert token.head.i == annots["heads"][i]


@pytest.mark.xfail(reason="TODO - fix")
@pytest.mark.parametrize(
    "annots",
    [
        {
            "words": ["Sarah", "'s", "sister", "flew"],
            "morphs": [
                "NounType=prop|Number=sing",
                "Poss=yes",
                "Number=sing",
                "Tense=past|VerbForm=fin",
            ],
        }
    ],
)
def test_Example_from_dict_with_morphology(annots):
    vocab = Vocab()
    predicted = Doc(vocab, words=annots["words"])
    eg = Example.from_dict(predicted, annots)
    for i, token in enumerate(eg.reference):
        assert token.morph_ == annots["morphs"][i]


@pytest.mark.parametrize(
    "annots",
    [
        {
            "words": ["This", "is", "one", "sentence", "this", "is", "another"],
            "sent_starts": [1, 0, 0, 0, 1, 0, 0],
        }
    ],
)
def test_Example_from_dict_with_sent_start(annots):
    vocab = Vocab()
    predicted = Doc(vocab, words=annots["words"])
    eg = Example.from_dict(predicted, annots)
    assert len(list(eg.reference.sents)) == 2
    for i, token in enumerate(eg.reference):
        assert bool(token.is_sent_start) == bool(annots["sent_starts"][i])


@pytest.mark.parametrize(
    "annots",
    [
        {
            "words": ["This", "is", "a", "sentence"],
            "cats": {"cat1": 1.0, "cat2": 0.0, "cat3": 0.5},
        }
    ],
)
def test_Example_from_dict_with_cats(annots):
    vocab = Vocab()
    predicted = Doc(vocab, words=annots["words"])
    eg = Example.from_dict(predicted, annots)
    assert len(list(eg.reference.cats)) == 3
    assert eg.reference.cats["cat1"] == 1.0
    assert eg.reference.cats["cat2"] == 0.0
    assert eg.reference.cats["cat3"] == 0.5


@pytest.mark.xfail(reason="TODO - fix")
@pytest.mark.parametrize(
    "annots",
    [
        {
            "words": ["Russ", "Cochran", "made", "reprints"],
            "links": {(0, 12): {"Q7381115": 1.0, "Q2146908": 0.0}},
        }
    ],
)
def test_Example_from_dict_with_links(annots):
    vocab = Vocab()
    predicted = Doc(vocab, words=annots["words"])
    eg = Example.from_dict(predicted, annots)
    assert eg.reference[0].ent_kb_id_ == "Q7381115"
    assert eg.reference[1].ent_kb_id_ == "Q7381115"
    assert eg.reference[2].ent_kb_id_ == ""
    assert eg.reference[3].ent_kb_id_ == ""
