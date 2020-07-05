import pytest
from spacy.gold.example import Example
from spacy.tokens import Doc
from spacy.vocab import Vocab


def test_Example_init_requires_doc_objects():
    vocab = Vocab()
    with pytest.raises(TypeError):
        example = Example(None, None)
    with pytest.raises(TypeError):
        example = Example(Doc(vocab, words=["hi"]), None)
    with pytest.raises(TypeError):
        example = Example(None, Doc(vocab, words=["hi"]))


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
    aligned_tags = example.get_aligned("tag", as_string=True)
    assert aligned_tags == ["NN" for _ in predicted]


def test_aligned_tags():
    pred_words = ["Apply", "some", "sunscreen", "unless", "you", "can", "not"]
    gold_words = ["Apply", "some", "sun", "screen", "unless", "you", "cannot"]
    gold_tags = ["VERB", "DET", "NOUN", "NOUN", "SCONJ", "PRON", "VERB"]
    annots = {"words": gold_words, "tags": gold_tags}
    vocab = Vocab()
    predicted = Doc(vocab, words=pred_words)
    example = Example.from_dict(predicted, annots)
    aligned_tags = example.get_aligned("tag", as_string=True)
    assert aligned_tags == ["VERB", "DET", "NOUN", "SCONJ", "PRON", "VERB", "VERB"]


def test_aligned_tags_multi():
    pred_words = ["Applysome", "sunscreen", "unless", "you", "can", "not"]
    gold_words = ["Apply", "somesun", "screen", "unless", "you", "cannot"]
    gold_tags = ["VERB", "DET", "NOUN", "SCONJ", "PRON", "VERB"]
    annots = {"words": gold_words, "tags": gold_tags}
    vocab = Vocab()
    predicted = Doc(vocab, words=pred_words)
    example = Example.from_dict(predicted, annots)
    aligned_tags = example.get_aligned("tag", as_string=True)
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
    example = Example.from_dict(predicted, annots)
    assert len(list(example.reference.sents)) == 2
    for i, token in enumerate(example.reference):
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
    assert [example.reference[i].ent_iob_ for i in range(7)] == [
        "O",
        "O",
        "B",
        "I",
        "O",
        "B",
        "O",
    ]
    assert example.get_aligned("ENT_IOB") == [2, 2, 3, 1, 2, 3, 2]

    assert example.reference[2].ent_type_ == "LOC"
    assert example.reference[3].ent_type_ == "LOC"
    assert example.reference[5].ent_type_ == "LOC"


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
    example = Example.from_dict(predicted, annots)
    # TODO: shouldn't this throw some sort of warning ?
    assert len(list(example.reference.ents)) == 0


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
