from spacy.errors import AlignmentError
from spacy.gold import biluo_tags_from_offsets, offsets_from_biluo_tags
from spacy.gold import spans_from_biluo_tags, iob_to_biluo, align
from spacy.gold import Corpus, docs_to_json
from spacy.gold.example import Example
from spacy.lang.en import English
from spacy.syntax.nonproj import is_nonproj_tree
from spacy.tokens import Doc, DocBin
from spacy.util import get_words_and_spaces, compounding, minibatch
import pytest
import srsly

from .util import make_tempdir
from ..gold.augment import make_orth_variants_example


@pytest.fixture
def doc():
    text = "Sarah's sister flew to Silicon Valley via London."
    tags = ["NNP", "POS", "NN", "VBD", "IN", "NNP", "NNP", "IN", "NNP", "."]
    pos = [
        "PROPN",
        "PART",
        "NOUN",
        "VERB",
        "ADP",
        "PROPN",
        "PROPN",
        "ADP",
        "PROPN",
        "PUNCT",
    ]
    morphs = [
        "NounType=prop|Number=sing",
        "Poss=yes",
        "Number=sing",
        "Tense=past|VerbForm=fin",
        "",
        "NounType=prop|Number=sing",
        "NounType=prop|Number=sing",
        "",
        "NounType=prop|Number=sing",
        "PunctType=peri",
    ]
    # head of '.' is intentionally nonprojective for testing
    heads = [2, 0, 3, 3, 3, 6, 4, 3, 7, 5]
    deps = [
        "poss",
        "case",
        "nsubj",
        "ROOT",
        "prep",
        "compound",
        "pobj",
        "prep",
        "pobj",
        "punct",
    ]
    lemmas = [
        "Sarah",
        "'s",
        "sister",
        "fly",
        "to",
        "Silicon",
        "Valley",
        "via",
        "London",
        ".",
    ]
    biluo_tags = ["U-PERSON", "O", "O", "O", "O", "B-LOC", "L-LOC", "O", "U-GPE", "O"]
    cats = {"TRAVEL": 1.0, "BAKING": 0.0}
    nlp = English()
    doc = nlp(text)
    for i in range(len(tags)):
        doc[i].tag_ = tags[i]
        doc[i].pos_ = pos[i]
        doc[i].morph_ = morphs[i]
        doc[i].lemma_ = lemmas[i]
        doc[i].dep_ = deps[i]
        doc[i].head = doc[heads[i]]
    doc.ents = spans_from_biluo_tags(doc, biluo_tags)
    doc.cats = cats
    doc.is_tagged = True
    doc.is_parsed = True
    return doc


@pytest.fixture()
def merged_dict():
    return {
        "ids": [1, 2, 3, 4, 5, 6, 7],
        "words": ["Hi", "there", "everyone", "It", "is", "just", "me"],
        "spaces": [True, True, True, True, True, True, False],
        "tags": ["INTJ", "ADV", "PRON", "PRON", "AUX", "ADV", "PRON"],
        "sent_starts": [1, 0, 0, 1, 0, 0, 0],
    }


@pytest.fixture
def vocab():
    nlp = English()
    return nlp.vocab


def test_gold_biluo_U(en_vocab):
    words = ["I", "flew", "to", "London", "."]
    spaces = [True, True, True, False, True]
    doc = Doc(en_vocab, words=words, spaces=spaces)
    entities = [(len("I flew to "), len("I flew to London"), "LOC")]
    tags = biluo_tags_from_offsets(doc, entities)
    assert tags == ["O", "O", "O", "U-LOC", "O"]


def test_gold_biluo_BL(en_vocab):
    words = ["I", "flew", "to", "San", "Francisco", "."]
    spaces = [True, True, True, True, False, True]
    doc = Doc(en_vocab, words=words, spaces=spaces)
    entities = [(len("I flew to "), len("I flew to San Francisco"), "LOC")]
    tags = biluo_tags_from_offsets(doc, entities)
    assert tags == ["O", "O", "O", "B-LOC", "L-LOC", "O"]


def test_gold_biluo_BIL(en_vocab):
    words = ["I", "flew", "to", "San", "Francisco", "Valley", "."]
    spaces = [True, True, True, True, True, False, True]
    doc = Doc(en_vocab, words=words, spaces=spaces)
    entities = [(len("I flew to "), len("I flew to San Francisco Valley"), "LOC")]
    tags = biluo_tags_from_offsets(doc, entities)
    assert tags == ["O", "O", "O", "B-LOC", "I-LOC", "L-LOC", "O"]


def test_gold_biluo_overlap(en_vocab):
    words = ["I", "flew", "to", "San", "Francisco", "Valley", "."]
    spaces = [True, True, True, True, True, False, True]
    doc = Doc(en_vocab, words=words, spaces=spaces)
    entities = [
        (len("I flew to "), len("I flew to San Francisco Valley"), "LOC"),
        (len("I flew to "), len("I flew to San Francisco"), "LOC"),
    ]
    with pytest.raises(ValueError):
        biluo_tags_from_offsets(doc, entities)


def test_gold_biluo_misalign(en_vocab):
    words = ["I", "flew", "to", "San", "Francisco", "Valley."]
    spaces = [True, True, True, True, True, False]
    doc = Doc(en_vocab, words=words, spaces=spaces)
    entities = [(len("I flew to "), len("I flew to San Francisco Valley"), "LOC")]
    with pytest.warns(UserWarning):
        tags = biluo_tags_from_offsets(doc, entities)
    assert tags == ["O", "O", "O", "-", "-", "-"]


def test_split_sentences(en_vocab):
    words = ["I", "flew", "to", "San Francisco Valley", "had", "loads of fun"]
    doc = Doc(en_vocab, words=words)
    gold_words = [
        "I",
        "flew",
        "to",
        "San",
        "Francisco",
        "Valley",
        "had",
        "loads",
        "of",
        "fun",
    ]
    sent_starts = [True, False, False, False, False, False, True, False, False, False]
    example = Example.from_dict(doc, {"words": gold_words, "sent_starts": sent_starts})
    assert example.text == "I flew to San Francisco Valley had loads of fun "
    split_examples = example.split_sents()
    assert len(split_examples) == 2
    assert split_examples[0].text == "I flew to San Francisco Valley "
    assert split_examples[1].text == "had loads of fun "

    words = ["I", "flew", "to", "San", "Francisco", "Valley", "had", "loads", "of fun"]
    doc = Doc(en_vocab, words=words)
    gold_words = [
        "I",
        "flew",
        "to",
        "San Francisco",
        "Valley",
        "had",
        "loads of",
        "fun",
    ]
    sent_starts = [True, False, False, False, False, True, False, False]
    example = Example.from_dict(doc, {"words": gold_words, "sent_starts": sent_starts})
    assert example.text == "I flew to San Francisco Valley had loads of fun "
    split_examples = example.split_sents()
    assert len(split_examples) == 2
    assert split_examples[0].text == "I flew to San Francisco Valley "
    assert split_examples[1].text == "had loads of fun "


def test_gold_biluo_different_tokenization(en_vocab, en_tokenizer):
    # one-to-many
    words = ["I", "flew to", "San Francisco Valley", "."]
    spaces = [True, True, False, False]
    doc = Doc(en_vocab, words=words, spaces=spaces)
    entities = [(len("I flew to "), len("I flew to San Francisco Valley"), "LOC")]
    gold_words = ["I", "flew", "to", "San", "Francisco", "Valley", "."]
    example = Example.from_dict(doc, {"words": gold_words, "entities": entities})
    assert example.get_aligned("ENT_IOB") == [2, 2, 3, 2]
    assert example.get_aligned("ENT_TYPE", as_string=True) == ["", "", "LOC", ""]

    # many-to-one
    words = ["I", "flew", "to", "San", "Francisco", "Valley", "."]
    spaces = [True, True, True, True, True, False, False]
    doc = Doc(en_vocab, words=words, spaces=spaces)
    entities = [(len("I flew to "), len("I flew to San Francisco Valley"), "LOC")]
    gold_words = ["I", "flew to", "San Francisco Valley", "."]
    example = Example.from_dict(doc, {"words": gold_words, "entities": entities})
    assert example.get_aligned("ENT_IOB") == [2, 2, 2, 3, 1, 1, 2]
    assert example.get_aligned("ENT_TYPE", as_string=True) == [
        "",
        "",
        "",
        "LOC",
        "LOC",
        "LOC",
        "",
    ]

    # misaligned
    words = ["I flew", "to", "San Francisco", "Valley", "."]
    spaces = [True, True, True, False, False]
    doc = Doc(en_vocab, words=words, spaces=spaces)
    offset_start = len("I flew to ")
    offset_end = len("I flew to San Francisco Valley")
    entities = [(offset_start, offset_end, "LOC")]
    links = {(offset_start, offset_end): {"Q816843": 1.0}}
    gold_words = ["I", "flew to", "San", "Francisco Valley", "."]
    example = Example.from_dict(
        doc, {"words": gold_words, "entities": entities, "links": links}
    )
    assert example.get_aligned("ENT_IOB") == [2, 2, 3, 1, 2]
    assert example.get_aligned("ENT_TYPE", as_string=True) == ["", "", "LOC", "LOC", ""]
    assert example.get_aligned("ENT_KB_ID", as_string=True) == [
        "",
        "",
        "Q816843",
        "Q816843",
        "",
    ]
    assert example.to_dict()["doc_annotation"]["links"][(offset_start, offset_end)] == {
        "Q816843": 1.0
    }

    # additional whitespace tokens in GoldParse words
    words, spaces = get_words_and_spaces(
        ["I", "flew", "to", "San Francisco", "Valley", "."],
        "I flew  to San Francisco Valley.",
    )
    doc = Doc(en_vocab, words=words, spaces=spaces)
    entities = [(len("I flew  to "), len("I flew  to San Francisco Valley"), "LOC")]
    gold_words = ["I", "flew", " ", "to", "San Francisco Valley", "."]
    gold_spaces = [True, True, False, True, False, False]
    example = Example.from_dict(
        doc, {"words": gold_words, "spaces": gold_spaces, "entities": entities}
    )
    assert example.get_aligned("ENT_IOB") == [2, 2, 2, 2, 3, 1, 2]
    assert example.get_aligned("ENT_TYPE", as_string=True) == [
        "",
        "",
        "",
        "",
        "LOC",
        "LOC",
        "",
    ]

    # from issue #4791
    doc = en_tokenizer("I'll return the ₹54 amount")
    gold_words = ["I", "'ll", "return", "the", "₹", "54", "amount"]
    gold_spaces = [False, True, True, True, False, True, False]
    entities = [(16, 19, "MONEY")]
    example = Example.from_dict(
        doc, {"words": gold_words, "spaces": gold_spaces, "entities": entities}
    )
    assert example.get_aligned("ENT_IOB") == [2, 2, 2, 2, 3, 2]
    assert example.get_aligned("ENT_TYPE", as_string=True) == [
        "",
        "",
        "",
        "",
        "MONEY",
        "",
    ]

    doc = en_tokenizer("I'll return the $54 amount")
    gold_words = ["I", "'ll", "return", "the", "$", "54", "amount"]
    gold_spaces = [False, True, True, True, False, True, False]
    entities = [(16, 19, "MONEY")]
    example = Example.from_dict(
        doc, {"words": gold_words, "spaces": gold_spaces, "entities": entities}
    )
    assert example.get_aligned("ENT_IOB") == [2, 2, 2, 2, 3, 1, 2]
    assert example.get_aligned("ENT_TYPE", as_string=True) == [
        "",
        "",
        "",
        "",
        "MONEY",
        "MONEY",
        "",
    ]


def test_roundtrip_offsets_biluo_conversion(en_tokenizer):
    text = "I flew to Silicon Valley via London."
    biluo_tags = ["O", "O", "O", "B-LOC", "L-LOC", "O", "U-GPE", "O"]
    offsets = [(10, 24, "LOC"), (29, 35, "GPE")]
    doc = en_tokenizer(text)
    biluo_tags_converted = biluo_tags_from_offsets(doc, offsets)
    assert biluo_tags_converted == biluo_tags
    offsets_converted = offsets_from_biluo_tags(doc, biluo_tags)
    assert offsets_converted == offsets


def test_biluo_spans(en_tokenizer):
    doc = en_tokenizer("I flew to Silicon Valley via London.")
    biluo_tags = ["O", "O", "O", "B-LOC", "L-LOC", "O", "U-GPE", "O"]
    spans = spans_from_biluo_tags(doc, biluo_tags)
    assert len(spans) == 2
    assert spans[0].text == "Silicon Valley"
    assert spans[0].label_ == "LOC"
    assert spans[1].text == "London"
    assert spans[1].label_ == "GPE"


def test_gold_ner_missing_tags(en_tokenizer):
    doc = en_tokenizer("I flew to Silicon Valley via London.")
    biluo_tags = [None, "O", "O", "B-LOC", "L-LOC", "O", "U-GPE", "O"]
    example = Example.from_dict(doc, {"entities": biluo_tags})
    assert example.get_aligned("ENT_IOB") == [0, 2, 2, 3, 1, 2, 3, 2]


def test_iob_to_biluo():
    good_iob = ["O", "O", "B-LOC", "I-LOC", "O", "B-PERSON"]
    good_biluo = ["O", "O", "B-LOC", "L-LOC", "O", "U-PERSON"]
    bad_iob = ["O", "O", '"', "B-LOC", "I-LOC"]
    converted_biluo = iob_to_biluo(good_iob)
    assert good_biluo == converted_biluo
    with pytest.raises(ValueError):
        iob_to_biluo(bad_iob)


def test_roundtrip_docs_to_docbin(doc):
    nlp = English()
    text = doc.text
    idx = [t.idx for t in doc]
    tags = [t.tag_ for t in doc]
    pos = [t.pos_ for t in doc]
    morphs = [t.morph_ for t in doc]
    lemmas = [t.lemma_ for t in doc]
    deps = [t.dep_ for t in doc]
    heads = [t.head.i for t in doc]
    cats = doc.cats
    ents = [(e.start_char, e.end_char, e.label_) for e in doc.ents]

    # roundtrip to DocBin
    with make_tempdir() as tmpdir:
        json_file = tmpdir / "roundtrip.json"
        srsly.write_json(json_file, [docs_to_json(doc)])
        goldcorpus = Corpus(str(json_file), str(json_file))
        output_file = tmpdir / "roundtrip.spacy"
        data = DocBin(docs=[doc]).to_bytes()
        with output_file.open("wb") as file_:
            file_.write(data)
        goldcorpus = Corpus(train_loc=str(output_file), dev_loc=str(output_file))
        reloaded_example = next(goldcorpus.dev_dataset(nlp=nlp))
        assert len(doc) == goldcorpus.count_train(nlp)
    assert text == reloaded_example.reference.text
    assert idx == [t.idx for t in reloaded_example.reference]
    assert tags == [t.tag_ for t in reloaded_example.reference]
    assert pos == [t.pos_ for t in reloaded_example.reference]
    assert morphs == [t.morph_ for t in reloaded_example.reference]
    assert lemmas == [t.lemma_ for t in reloaded_example.reference]
    assert deps == [t.dep_ for t in reloaded_example.reference]
    assert heads == [t.head.i for t in reloaded_example.reference]
    assert ents == [
        (e.start_char, e.end_char, e.label_) for e in reloaded_example.reference.ents
    ]
    assert "TRAVEL" in reloaded_example.reference.cats
    assert "BAKING" in reloaded_example.reference.cats
    assert cats["TRAVEL"] == reloaded_example.reference.cats["TRAVEL"]
    assert cats["BAKING"] == reloaded_example.reference.cats["BAKING"]


# Hm, not sure where misalignment check would be handled? In the components too?
# I guess that does make sense. A text categorizer doesn't care if it's
# misaligned...
@pytest.mark.xfail(reason="Outdated")
def test_ignore_misaligned(doc):
    nlp = English()
    text = doc.text
    with make_tempdir() as tmpdir:
        json_file = tmpdir / "test.json"
        data = [docs_to_json(doc)]
        data[0]["paragraphs"][0]["raw"] = text.replace("Sarah", "Jane")
        # write to JSON train dicts
        srsly.write_json(json_file, data)
        goldcorpus = Corpus(str(json_file), str(json_file))

        with pytest.raises(AlignmentError):
            train_reloaded_example = next(goldcorpus.train_dataset(nlp))

    with make_tempdir() as tmpdir:
        json_file = tmpdir / "test.json"
        data = [docs_to_json(doc)]
        data[0]["paragraphs"][0]["raw"] = text.replace("Sarah", "Jane")
        # write to JSON train dicts
        srsly.write_json(json_file, data)
        goldcorpus = Corpus(str(json_file), str(json_file))

        # doesn't raise an AlignmentError, but there is nothing to iterate over
        # because the only example can't be aligned
        train_reloaded_example = list(
            goldcorpus.train_dataset(nlp, ignore_misaligned=True)
        )
        assert len(train_reloaded_example) == 0


# We probably want the orth variant logic back, but this test won't be quite
# right -- we need to go from DocBin.
def test_make_orth_variants(doc):
    nlp = English()
    with make_tempdir() as tmpdir:
        output_file = tmpdir / "roundtrip.spacy"
        data = DocBin(docs=[doc]).to_bytes()
        with output_file.open("wb") as file_:
            file_.write(data)
        goldcorpus = Corpus(train_loc=str(output_file), dev_loc=str(output_file))

        # due to randomness, test only that this runs with no errors for now
        train_example = next(goldcorpus.train_dataset(nlp))
        variant_example = make_orth_variants_example(
            nlp, train_example, orth_variant_level=0.2
        )


@pytest.mark.parametrize(
    "tokens_a,tokens_b,expected",
    [
        (["a", "b", "c"], ["ab", "c"], (3, [-1, -1, 1], [-1, 2], {0: 0, 1: 0}, {})),
        (
            ["a", "b", '"', "c"],
            ['ab"', "c"],
            (4, [-1, -1, -1, 1], [-1, 3], {0: 0, 1: 0, 2: 0}, {}),
        ),
        (["a", "bc"], ["ab", "c"], (4, [-1, -1], [-1, -1], {0: 0}, {1: 1})),
        (
            ["ab", "c", "d"],
            ["a", "b", "cd"],
            (6, [-1, -1, -1], [-1, -1, -1], {1: 2, 2: 2}, {0: 0, 1: 0}),
        ),
        (
            ["a", "b", "cd"],
            ["a", "b", "c", "d"],
            (3, [0, 1, -1], [0, 1, -1, -1], {}, {2: 2, 3: 2}),
        ),
        ([" ", "a"], ["a"], (1, [-1, 0], [1], {}, {})),
    ],
)
def test_align(tokens_a, tokens_b, expected):
    cost, a2b, b2a, a2b_multi, b2a_multi = align(tokens_a, tokens_b)
    assert (cost, list(a2b), list(b2a), a2b_multi, b2a_multi) == expected
    # check symmetry
    cost, a2b, b2a, a2b_multi, b2a_multi = align(tokens_b, tokens_a)
    assert (cost, list(b2a), list(a2b), b2a_multi, a2b_multi) == expected


def test_goldparse_startswith_space(en_tokenizer):
    text = " a"
    doc = en_tokenizer(text)
    gold_words = ["a"]
    entities = ["U-DATE"]
    deps = ["ROOT"]
    heads = [0]
    example = Example.from_dict(
        doc, {"words": gold_words, "entities": entities, "deps": deps, "heads": heads}
    )
    assert example.get_aligned("ENT_IOB") == [None, 3]
    assert example.get_aligned("ENT_TYPE", as_string=True) == [None, "DATE"]
    assert example.get_aligned("DEP", as_string=True) == [None, "ROOT"]


def test_gold_constructor():
    """Test that the Example constructor works fine"""
    nlp = English()
    doc = nlp("This is a sentence")
    example = Example.from_dict(doc, {"cats": {"cat1": 1.0, "cat2": 0.0}})
    assert example.get_aligned("ORTH", as_string=True) == [
        "This",
        "is",
        "a",
        "sentence",
    ]
    assert example.reference.cats["cat1"]
    assert not example.reference.cats["cat2"]


def test_tuple_format_implicit():
    """Test tuple format"""

    train_data = [
        ("Uber blew through $1 million a week", {"entities": [(0, 4, "ORG")]}),
        (
            "Spotify steps up Asia expansion",
            {"entities": [(0, 8, "ORG"), (17, 21, "LOC")]},
        ),
        ("Google rebrands its business apps", {"entities": [(0, 6, "ORG")]}),
    ]

    _train(train_data)


def test_tuple_format_implicit_invalid():
    """Test that an error is thrown for an implicit invalid field"""

    train_data = [
        ("Uber blew through $1 million a week", {"frumble": [(0, 4, "ORG")]}),
        (
            "Spotify steps up Asia expansion",
            {"entities": [(0, 8, "ORG"), (17, 21, "LOC")]},
        ),
        ("Google rebrands its business apps", {"entities": [(0, 6, "ORG")]}),
    ]

    with pytest.raises(KeyError):
        _train(train_data)


def _train(train_data):
    nlp = English()
    ner = nlp.create_pipe("ner")
    ner.add_label("ORG")
    ner.add_label("LOC")
    nlp.add_pipe(ner)

    optimizer = nlp.begin_training()
    for i in range(5):
        losses = {}
        batches = minibatch(train_data, size=compounding(4.0, 32.0, 1.001))
        for batch in batches:
            nlp.update(batch, sgd=optimizer, losses=losses)


def test_split_sents(merged_dict):
    nlp = English()
    example = Example.from_dict(
        Doc(nlp.vocab, words=merged_dict["words"], spaces=merged_dict["spaces"]),
        merged_dict,
    )
    assert example.text == "Hi there everyone It is just me"

    split_examples = example.split_sents()
    assert len(split_examples) == 2
    assert split_examples[0].text == "Hi there everyone "
    assert split_examples[1].text == "It is just me"

    token_annotation_1 = split_examples[0].to_dict()["token_annotation"]
    assert token_annotation_1["words"] == ["Hi", "there", "everyone"]
    assert token_annotation_1["tags"] == ["INTJ", "ADV", "PRON"]
    assert token_annotation_1["sent_starts"] == [1, 0, 0]

    token_annotation_2 = split_examples[1].to_dict()["token_annotation"]
    assert token_annotation_2["words"] == ["It", "is", "just", "me"]
    assert token_annotation_2["tags"] == ["PRON", "AUX", "ADV", "PRON"]
    assert token_annotation_2["sent_starts"] == [1, 0, 0, 0]
