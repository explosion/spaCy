import pytest
from spacy.training.example import Example
from spacy.tokens import Doc
from spacy.vocab import Vocab
from spacy.util import to_ternary_int


def test_Example_init_requires_doc_objects():
    vocab = Vocab()
    with pytest.raises(TypeError):
        Example(None, None)
    with pytest.raises(TypeError):
        Example(Doc(vocab, words=["hi"]), None)
    with pytest.raises(TypeError):
        Example(None, Doc(vocab, words=["hi"]))


def test_Example_from_dict_basic():
    example = Example.from_dict(
        Doc(Vocab(), words=["hello", "world"]), {"words": ["hello", "world"]}
    )
    assert isinstance(example.x, Doc)
    assert isinstance(example.y, Doc)


@pytest.mark.parametrize(
    "annots", [{"words": ["ice", "cream"], "weirdannots": ["something", "such"]}]
)
def test_Example_from_dict_invalid(annots):
    vocab = Vocab()
    predicted = Doc(vocab, words=annots["words"])
    with pytest.raises(KeyError):
        Example.from_dict(predicted, annots)


@pytest.mark.parametrize(
    "pred_words", [["ice", "cream"], ["icecream"], ["i", "ce", "cream"]]
)
@pytest.mark.parametrize("annots", [{"words": ["icecream"], "tags": ["NN"]}])
def test_Example_from_dict_with_tags(pred_words, annots):
    vocab = Vocab()
    predicted = Doc(vocab, words=pred_words)
    example = Example.from_dict(predicted, annots)
    for i, token in enumerate(example.reference):
        assert token.tag_ == annots["tags"][i]
    aligned_tags = example.get_aligned("TAG", as_string=True)
    assert aligned_tags == ["NN" for _ in predicted]


@pytest.mark.filterwarnings("ignore::UserWarning")
def test_aligned_tags():
    pred_words = ["Apply", "some", "sunscreen", "unless", "you", "can", "not"]
    gold_words = ["Apply", "some", "sun", "screen", "unless", "you", "cannot"]
    gold_tags = ["VERB", "DET", "NOUN", "NOUN", "SCONJ", "PRON", "VERB"]
    annots = {"words": gold_words, "tags": gold_tags}
    vocab = Vocab()
    predicted = Doc(vocab, words=pred_words)
    example1 = Example.from_dict(predicted, annots)
    aligned_tags1 = example1.get_aligned("TAG", as_string=True)
    assert aligned_tags1 == ["VERB", "DET", "NOUN", "SCONJ", "PRON", "VERB", "VERB"]
    # ensure that to_dict works correctly
    example2 = Example.from_dict(predicted, example1.to_dict())
    aligned_tags2 = example2.get_aligned("TAG", as_string=True)
    assert aligned_tags2 == ["VERB", "DET", "NOUN", "SCONJ", "PRON", "VERB", "VERB"]


def test_aligned_tags_multi():
    pred_words = ["Applysome", "sunscreen", "unless", "you", "can", "not"]
    gold_words = ["Apply", "somesun", "screen", "unless", "you", "cannot"]
    gold_tags = ["VERB", "DET", "NOUN", "SCONJ", "PRON", "VERB"]
    annots = {"words": gold_words, "tags": gold_tags}
    vocab = Vocab()
    predicted = Doc(vocab, words=pred_words)
    example = Example.from_dict(predicted, annots)
    aligned_tags = example.get_aligned("TAG", as_string=True)
    assert aligned_tags == [None, None, "SCONJ", "PRON", "VERB", "VERB"]


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
    example = Example.from_dict(predicted, annots)
    for i, token in enumerate(example.reference):
        assert token.dep_ == annots["deps"][i]
        assert token.head.i == annots["heads"][i]


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
    example = Example.from_dict(predicted, annots)
    for i, token in enumerate(example.reference):
        assert str(token.morph) == annots["morphs"][i]


@pytest.mark.parametrize(
    "annots",
    [
        {
            "words": ["This", "is", "one", "sentence", "this", "is", "another"],
            "sent_starts": [1, False, 0, None, True, -1, -5.7],
        }
    ],
)
def test_Example_from_dict_with_sent_start(annots):
    vocab = Vocab()
    predicted = Doc(vocab, words=annots["words"])
    example = Example.from_dict(predicted, annots)
    assert len(list(example.reference.sents)) == 2
    for i, token in enumerate(example.reference):
        if to_ternary_int(annots["sent_starts"][i]) == 1:
            assert token.is_sent_start is True
        elif to_ternary_int(annots["sent_starts"][i]) == 0:
            assert token.is_sent_start is None
        else:
            assert token.is_sent_start is False


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
    example = Example.from_dict(predicted, annots)
    assert len(list(example.reference.cats)) == 3
    assert example.reference.cats["cat1"] == 1.0
    assert example.reference.cats["cat2"] == 0.0
    assert example.reference.cats["cat3"] == 0.5


@pytest.mark.parametrize(
    "annots",
    [
        {
            "words": ["I", "like", "New", "York", "and", "Berlin", "."],
            "entities": [(7, 15, "LOC"), (20, 26, "LOC")],
        }
    ],
)
def test_Example_from_dict_with_entities(annots):
    vocab = Vocab()
    predicted = Doc(vocab, words=annots["words"])
    example = Example.from_dict(predicted, annots)
    assert len(list(example.reference.ents)) == 2
    # fmt: off
    assert [example.reference[i].ent_iob_ for i in range(7)] == ["O", "O", "B", "I", "O", "B", "O"]
    assert example.get_aligned("ENT_IOB") == [2, 2, 3, 1, 2, 3, 2]
    # fmt: on
    assert example.reference[2].ent_type_ == "LOC"
    assert example.reference[3].ent_type_ == "LOC"
    assert example.reference[5].ent_type_ == "LOC"


def test_Example_from_dict_with_empty_entities():
    annots = {
        "words": ["I", "like", "New", "York", "and", "Berlin", "."],
        "entities": [],
    }
    vocab = Vocab()
    predicted = Doc(vocab, words=annots["words"])
    example = Example.from_dict(predicted, annots)
    # entities as empty list sets everything to O
    assert example.reference.has_annotation("ENT_IOB")
    assert len(list(example.reference.ents)) == 0
    assert all(token.ent_iob_ == "O" for token in example.reference)
    # various unset/missing entities leaves entities unset
    annots["entities"] = None
    example = Example.from_dict(predicted, annots)
    assert not example.reference.has_annotation("ENT_IOB")
    annots.pop("entities", None)
    example = Example.from_dict(predicted, annots)
    assert not example.reference.has_annotation("ENT_IOB")


@pytest.mark.parametrize(
    "annots",
    [
        {
            "words": ["I", "like", "New", "York", "and", "Berlin", "."],
            "entities": [
                (0, 4, "LOC"),
                (21, 27, "LOC"),
            ],  # not aligned to token boundaries
        }
    ],
)
def test_Example_from_dict_with_entities_invalid(annots):
    vocab = Vocab()
    predicted = Doc(vocab, words=annots["words"])
    with pytest.warns(UserWarning):
        example = Example.from_dict(predicted, annots)
    assert len(list(example.reference.ents)) == 0


@pytest.mark.parametrize(
    "annots",
    [
        {
            "words": ["I", "like", "New", "York", "and", "Berlin", "."],
            "entities": [
                (7, 15, "LOC"),
                (11, 15, "LOC"),
                (20, 26, "LOC"),
            ],  # overlapping
        }
    ],
)
def test_Example_from_dict_with_entities_overlapping(annots):
    vocab = Vocab()
    predicted = Doc(vocab, words=annots["words"])
    with pytest.raises(ValueError):
        Example.from_dict(predicted, annots)


@pytest.mark.parametrize(
    "annots",
    [
        {
            "words": ["I", "like", "New", "York", "and", "Berlin", "."],
            "spans": {
                "cities": [(7, 15, "LOC"), (20, 26, "LOC")],
                "people": [(0, 1, "PERSON")],
            },
        }
    ],
)
def test_Example_from_dict_with_spans(annots):
    vocab = Vocab()
    predicted = Doc(vocab, words=annots["words"])
    example = Example.from_dict(predicted, annots)
    assert len(list(example.reference.ents)) == 0
    assert len(list(example.reference.spans["cities"])) == 2
    assert len(list(example.reference.spans["people"])) == 1
    for span in example.reference.spans["cities"]:
        assert span.label_ == "LOC"
    for span in example.reference.spans["people"]:
        assert span.label_ == "PERSON"


@pytest.mark.parametrize(
    "annots",
    [
        {
            "words": ["I", "like", "New", "York", "and", "Berlin", "."],
            "spans": {
                "cities": [(7, 15, "LOC"), (11, 15, "LOC"), (20, 26, "LOC")],
                "people": [(0, 1, "PERSON")],
            },
        }
    ],
)
def test_Example_from_dict_with_spans_overlapping(annots):
    vocab = Vocab()
    predicted = Doc(vocab, words=annots["words"])
    example = Example.from_dict(predicted, annots)
    assert len(list(example.reference.ents)) == 0
    assert len(list(example.reference.spans["cities"])) == 3
    assert len(list(example.reference.spans["people"])) == 1
    for span in example.reference.spans["cities"]:
        assert span.label_ == "LOC"
    for span in example.reference.spans["people"]:
        assert span.label_ == "PERSON"


@pytest.mark.parametrize(
    "annots",
    [
        {
            "words": ["I", "like", "New", "York", "and", "Berlin", "."],
            "spans": [(0, 1, "PERSON")],
        },
        {
            "words": ["I", "like", "New", "York", "and", "Berlin", "."],
            "spans": {"cities": (7, 15, "LOC")},
        },
        {
            "words": ["I", "like", "New", "York", "and", "Berlin", "."],
            "spans": {"cities": [7, 11]},
        },
        {
            "words": ["I", "like", "New", "York", "and", "Berlin", "."],
            "spans": {"cities": [[7]]},
        },
    ],
)
def test_Example_from_dict_with_spans_invalid(annots):
    vocab = Vocab()
    predicted = Doc(vocab, words=annots["words"])
    with pytest.raises(ValueError):
        Example.from_dict(predicted, annots)


@pytest.mark.parametrize(
    "annots",
    [
        {
            "words": ["I", "like", "New", "York", "and", "Berlin", "."],
            "entities": [(7, 15, "LOC"), (20, 26, "LOC")],
            "links": {
                (7, 15): {"Q60": 1.0, "Q64": 0.0},
                (20, 26): {"Q60": 0.0, "Q64": 1.0},
            },
        }
    ],
)
def test_Example_from_dict_with_links(annots):
    vocab = Vocab()
    predicted = Doc(vocab, words=annots["words"])
    example = Example.from_dict(predicted, annots)
    assert example.reference[0].ent_kb_id_ == ""
    assert example.reference[1].ent_kb_id_ == ""
    assert example.reference[2].ent_kb_id_ == "Q60"
    assert example.reference[3].ent_kb_id_ == "Q60"
    assert example.reference[4].ent_kb_id_ == ""
    assert example.reference[5].ent_kb_id_ == "Q64"
    assert example.reference[6].ent_kb_id_ == ""


@pytest.mark.parametrize(
    "annots",
    [
        {
            "words": ["I", "like", "New", "York", "and", "Berlin", "."],
            "links": {(7, 14): {"Q7381115": 1.0, "Q2146908": 0.0}},
        }
    ],
)
def test_Example_from_dict_with_links_invalid(annots):
    vocab = Vocab()
    predicted = Doc(vocab, words=annots["words"])
    with pytest.raises(ValueError):
        Example.from_dict(predicted, annots)


def test_Example_from_dict_sentences():
    vocab = Vocab()
    predicted = Doc(vocab, words=["One", "sentence", ".", "one", "more"])
    annots = {"sent_starts": [1, 0, 0, 1, 0]}
    ex = Example.from_dict(predicted, annots)
    assert len(list(ex.reference.sents)) == 2

    # this currently throws an error - bug or feature?
    # predicted = Doc(vocab, words=["One", "sentence", "not", "one", "more"])
    # annots = {"sent_starts": [1, 0, 0, 0, 0]}
    # ex = Example.from_dict(predicted, annots)
    # assert len(list(ex.reference.sents)) == 1

    predicted = Doc(vocab, words=["One", "sentence", "not", "one", "more"])
    annots = {"sent_starts": [1, -1, 0, 0, 0]}
    ex = Example.from_dict(predicted, annots)
    assert len(list(ex.reference.sents)) == 1


def test_Example_missing_deps():
    vocab = Vocab()
    words = ["I", "like", "London", "and", "Berlin", "."]
    deps = ["nsubj", "ROOT", "dobj", "cc", "conj", "punct"]
    heads = [1, 1, 1, 2, 2, 1]
    annots_head_only = {"words": words, "heads": heads}
    annots_head_dep = {"words": words, "heads": heads, "deps": deps}
    predicted = Doc(vocab, words=words)

    # when not providing deps, the head information is considered to be missing
    # in this case, the token's heads refer to themselves
    example_1 = Example.from_dict(predicted, annots_head_only)
    assert [t.head.i for t in example_1.reference] == [0, 1, 2, 3, 4, 5]

    # when providing deps, the head information is actually used
    example_2 = Example.from_dict(predicted, annots_head_dep)
    assert [t.head.i for t in example_2.reference] == heads


def test_Example_missing_heads():
    vocab = Vocab()
    words = ["I", "like", "London", "and", "Berlin", "."]
    deps = ["nsubj", "ROOT", "dobj", None, "conj", "punct"]
    heads = [1, 1, 1, None, 2, 1]
    annots = {"words": words, "heads": heads, "deps": deps}
    predicted = Doc(vocab, words=words)

    example = Example.from_dict(predicted, annots)
    parsed_heads = [t.head.i for t in example.reference]
    assert parsed_heads[0] == heads[0]
    assert parsed_heads[1] == heads[1]
    assert parsed_heads[2] == heads[2]
    assert parsed_heads[4] == heads[4]
    assert parsed_heads[5] == heads[5]
    expected = [True, True, True, False, True, True]
    assert [t.has_head() for t in example.reference] == expected
    # Ensure that the missing head doesn't create an artificial new sentence start
    expected = [True, False, False, False, False, False]
    assert example.get_aligned_sent_starts() == expected
