# coding: utf-8
from __future__ import unicode_literals

from spacy.gold import biluo_tags_from_offsets, offsets_from_biluo_tags
from spacy.gold import spans_from_biluo_tags, GoldParse, iob_to_biluo
from spacy.gold import GoldCorpus, docs_to_json, align
from spacy.lang.en import English
from spacy.tokens import Doc
from .util import make_tempdir
import pytest
import srsly


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
    tags = biluo_tags_from_offsets(doc, entities)
    assert tags == ["O", "O", "O", "-", "-", "-"]


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
    gold = GoldParse(doc, entities=biluo_tags)  # noqa: F841


def test_iob_to_biluo():
    good_iob = ["O", "O", "B-LOC", "I-LOC", "O", "B-PERSON"]
    good_biluo = ["O", "O", "B-LOC", "L-LOC", "O", "U-PERSON"]
    bad_iob = ["O", "O", '"', "B-LOC", "I-LOC"]
    converted_biluo = iob_to_biluo(good_iob)
    assert good_biluo == converted_biluo
    with pytest.raises(ValueError):
        iob_to_biluo(bad_iob)


def test_roundtrip_docs_to_json():
    text = "I flew to Silicon Valley via London."
    tags = ["PRP", "VBD", "IN", "NNP", "NNP", "IN", "NNP", "."]
    heads = [1, 1, 1, 4, 2, 1, 5, 1]
    deps = ["nsubj", "ROOT", "prep", "compound", "pobj", "prep", "pobj", "punct"]
    biluo_tags = ["O", "O", "O", "B-LOC", "L-LOC", "O", "U-GPE", "O"]
    cats = {"TRAVEL": 1.0, "BAKING": 0.0}
    nlp = English()
    doc = nlp(text)
    for i in range(len(tags)):
        doc[i].tag_ = tags[i]
        doc[i].dep_ = deps[i]
        doc[i].head = doc[heads[i]]
    doc.ents = spans_from_biluo_tags(doc, biluo_tags)
    doc.cats = cats
    doc.is_tagged = True
    doc.is_parsed = True

    # roundtrip to JSON
    with make_tempdir() as tmpdir:
        json_file = tmpdir / "roundtrip.json"
        srsly.write_json(json_file, [docs_to_json(doc)])
        goldcorpus = GoldCorpus(str(json_file), str(json_file))

    reloaded_doc, goldparse = next(goldcorpus.train_docs(nlp))

    assert len(doc) == goldcorpus.count_train()
    assert text == reloaded_doc.text
    assert tags == goldparse.tags
    assert deps == goldparse.labels
    assert heads == goldparse.heads
    assert biluo_tags == goldparse.ner
    assert "TRAVEL" in goldparse.cats
    assert "BAKING" in goldparse.cats
    assert cats["TRAVEL"] == goldparse.cats["TRAVEL"]
    assert cats["BAKING"] == goldparse.cats["BAKING"]

    # roundtrip to JSONL train dicts
    with make_tempdir() as tmpdir:
        jsonl_file = tmpdir / "roundtrip.jsonl"
        srsly.write_jsonl(jsonl_file, [docs_to_json(doc)])
        goldcorpus = GoldCorpus(str(jsonl_file), str(jsonl_file))

    reloaded_doc, goldparse = next(goldcorpus.train_docs(nlp))

    assert len(doc) == goldcorpus.count_train()
    assert text == reloaded_doc.text
    assert tags == goldparse.tags
    assert deps == goldparse.labels
    assert heads == goldparse.heads
    assert biluo_tags == goldparse.ner
    assert "TRAVEL" in goldparse.cats
    assert "BAKING" in goldparse.cats
    assert cats["TRAVEL"] == goldparse.cats["TRAVEL"]
    assert cats["BAKING"] == goldparse.cats["BAKING"]

    # roundtrip to JSONL tuples
    with make_tempdir() as tmpdir:
        jsonl_file = tmpdir / "roundtrip.jsonl"
        # write to JSONL train dicts
        srsly.write_jsonl(jsonl_file, [docs_to_json(doc)])
        goldcorpus = GoldCorpus(str(jsonl_file), str(jsonl_file))
        # load and rewrite as JSONL tuples
        srsly.write_jsonl(jsonl_file, goldcorpus.train_tuples)
        goldcorpus = GoldCorpus(str(jsonl_file), str(jsonl_file))

    reloaded_doc, goldparse = next(goldcorpus.train_docs(nlp))

    assert len(doc) == goldcorpus.count_train()
    assert text == reloaded_doc.text
    assert tags == goldparse.tags
    assert deps == goldparse.labels
    assert heads == goldparse.heads
    assert biluo_tags == goldparse.ner
    assert "TRAVEL" in goldparse.cats
    assert "BAKING" in goldparse.cats
    assert cats["TRAVEL"] == goldparse.cats["TRAVEL"]
    assert cats["BAKING"] == goldparse.cats["BAKING"]


@pytest.mark.skip(reason="skip while we have backwards-compatible alignment")
@pytest.mark.parametrize(
    "tokens_a,tokens_b,expected",
    [
        (["a", "b", "c"], ["ab", "c"], (3, [-1, -1, 1], [-1, 2], {0: 0, 1: 0}, {})),
        (
            ["a", "b", "``", "c"],
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
    g = GoldParse(doc, words=["a"], entities=["U-DATE"], deps=["ROOT"], heads=[0])
    assert g.words == [" ", "a"]
    assert g.ner == [None, "U-DATE"]
    assert g.labels == [None, "ROOT"]
