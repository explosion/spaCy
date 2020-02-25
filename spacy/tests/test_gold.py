from spacy.errors import AlignmentError
from spacy.gold import biluo_tags_from_offsets, offsets_from_biluo_tags
from spacy.gold import spans_from_biluo_tags, GoldParse, iob_to_biluo, align
from spacy.gold import GoldCorpus, docs_to_json, Example, DocAnnotation
from spacy.lang.en import English
from spacy.syntax.nonproj import is_nonproj_tree
from spacy.tokens import Doc
from spacy.util import compounding, minibatch
from .util import make_tempdir
import pytest
import srsly


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
        "tags": ["INTJ", "ADV", "PRON", "PRON", "AUX", "ADV", "PRON"],
        "sent_starts": [1, 0, 0, 1, 0, 0, 0, 0],
    }


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


def test_roundtrip_docs_to_json(doc):
    nlp = English()
    text = doc.text
    tags = [t.tag_ for t in doc]
    pos = [t.pos_ for t in doc]
    morphs = [t.morph_ for t in doc]
    lemmas = [t.lemma_ for t in doc]
    deps = [t.dep_ for t in doc]
    heads = [t.head.i for t in doc]
    biluo_tags = iob_to_biluo(
        [t.ent_iob_ + "-" + t.ent_type_ if t.ent_type_ else "O" for t in doc]
    )
    cats = doc.cats

    # roundtrip to JSON
    with make_tempdir() as tmpdir:
        json_file = tmpdir / "roundtrip.json"
        srsly.write_json(json_file, [docs_to_json(doc)])
        goldcorpus = GoldCorpus(train=str(json_file), dev=str(json_file))

    reloaded_example = next(goldcorpus.dev_dataset(nlp))
    goldparse = reloaded_example.gold

    assert len(doc) == goldcorpus.count_train()
    assert text == reloaded_example.text
    assert tags == goldparse.tags
    assert pos == goldparse.pos
    assert morphs == goldparse.morphs
    assert lemmas == goldparse.lemmas
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

    reloaded_example = next(goldcorpus.dev_dataset(nlp))
    goldparse = reloaded_example.gold

    assert len(doc) == goldcorpus.count_train()
    assert text == reloaded_example.text
    assert tags == goldparse.tags
    assert pos == goldparse.pos
    assert morphs == goldparse.morphs
    assert lemmas == goldparse.lemmas
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
        srsly.write_jsonl(jsonl_file, goldcorpus.train_examples)
        goldcorpus = GoldCorpus(str(jsonl_file), str(jsonl_file))

    reloaded_example = next(goldcorpus.dev_dataset(nlp))
    goldparse = reloaded_example.gold

    assert len(doc) == goldcorpus.count_train()
    assert text == reloaded_example.text
    assert tags == goldparse.tags
    assert deps == goldparse.labels
    assert heads == goldparse.heads
    assert lemmas == goldparse.lemmas
    assert biluo_tags == goldparse.ner
    assert "TRAVEL" in goldparse.cats
    assert "BAKING" in goldparse.cats
    assert cats["TRAVEL"] == goldparse.cats["TRAVEL"]
    assert cats["BAKING"] == goldparse.cats["BAKING"]


def test_projective_train_vs_nonprojective_dev(doc):
    nlp = English()
    deps = [t.dep_ for t in doc]
    heads = [t.head.i for t in doc]

    with make_tempdir() as tmpdir:
        jsonl_file = tmpdir / "test.jsonl"
        # write to JSONL train dicts
        srsly.write_jsonl(jsonl_file, [docs_to_json(doc)])
        goldcorpus = GoldCorpus(str(jsonl_file), str(jsonl_file))

    train_reloaded_example = next(goldcorpus.train_dataset(nlp))
    train_goldparse = train_reloaded_example.gold

    dev_reloaded_example = next(goldcorpus.dev_dataset(nlp))
    dev_goldparse = dev_reloaded_example.gold

    assert is_nonproj_tree([t.head.i for t in doc]) is True
    assert is_nonproj_tree(train_goldparse.heads) is False
    assert heads[:-1] == train_goldparse.heads[:-1]
    assert heads[-1] != train_goldparse.heads[-1]
    assert deps[:-1] == train_goldparse.labels[:-1]
    assert deps[-1] != train_goldparse.labels[-1]

    assert heads == dev_goldparse.heads
    assert deps == dev_goldparse.labels


def test_ignore_misaligned(doc):
    nlp = English()
    text = doc.text
    with make_tempdir() as tmpdir:
        jsonl_file = tmpdir / "test.jsonl"
        data = [docs_to_json(doc)]
        data[0]["paragraphs"][0]["raw"] = text.replace("Sarah", "Jane")
        # write to JSONL train dicts
        srsly.write_jsonl(jsonl_file, data)
        goldcorpus = GoldCorpus(str(jsonl_file), str(jsonl_file))

    with pytest.raises(AlignmentError):
        train_reloaded_example = next(goldcorpus.train_dataset(nlp))

    with make_tempdir() as tmpdir:
        jsonl_file = tmpdir / "test.jsonl"
        data = [docs_to_json(doc)]
        data[0]["paragraphs"][0]["raw"] = text.replace("Sarah", "Jane")
        # write to JSONL train dicts
        srsly.write_jsonl(jsonl_file, data)
        goldcorpus = GoldCorpus(str(jsonl_file), str(jsonl_file))

    # doesn't raise an AlignmentError, but there is nothing to iterate over
    # because the only example can't be aligned
    train_reloaded_example = list(goldcorpus.train_dataset(nlp, ignore_misaligned=True))
    assert len(train_reloaded_example) == 0


def test_make_orth_variants(doc):
    nlp = English()
    with make_tempdir() as tmpdir:
        jsonl_file = tmpdir / "test.jsonl"
        # write to JSONL train dicts
        srsly.write_jsonl(jsonl_file, [docs_to_json(doc)])
        goldcorpus = GoldCorpus(str(jsonl_file), str(jsonl_file))

    # due to randomness, test only that this runs with no errors for now
    train_reloaded_example = next(goldcorpus.train_dataset(nlp, orth_variant_level=0.2))
    train_goldparse = train_reloaded_example.gold  # noqa: F841


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
    g = GoldParse(doc, words=["a"], entities=["U-DATE"], deps=["ROOT"], heads=[0])
    assert g.words == [" ", "a"]
    assert g.ner == [None, "U-DATE"]
    assert g.labels == [None, "ROOT"]


def test_gold_constructor():
    """Test that the GoldParse constructor works fine"""
    nlp = English()
    doc = nlp("This is a sentence")
    gold = GoldParse(doc, cats={"cat1": 1.0, "cat2": 0.0})

    assert gold.cats["cat1"]
    assert not gold.cats["cat2"]
    assert gold.words == ["This", "is", "a", "sentence"]


def test_gold_orig_annot():
    nlp = English()
    doc = nlp("This is a sentence")
    gold = GoldParse(doc, cats={"cat1": 1.0, "cat2": 0.0})

    assert gold.orig.words == ["This", "is", "a", "sentence"]
    assert gold.cats["cat1"]

    doc_annotation = DocAnnotation(cats={"cat1": 0.0, "cat2": 1.0})
    gold2 = GoldParse.from_annotation(doc, doc_annotation, gold.orig)
    assert gold2.orig.words == ["This", "is", "a", "sentence"]
    assert not gold2.cats["cat1"]


def test_tuple_format_implicit():
    """Test tuple format with implicit GoldParse creation"""

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
    """Test that an error is thrown for an implicit invalid GoldParse field"""

    train_data = [
        ("Uber blew through $1 million a week", {"frumble": [(0, 4, "ORG")]}),
        (
            "Spotify steps up Asia expansion",
            {"entities": [(0, 8, "ORG"), (17, 21, "LOC")]},
        ),
        ("Google rebrands its business apps", {"entities": [(0, 6, "ORG")]}),
    ]

    with pytest.raises(TypeError):
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
    example = Example()
    example.set_token_annotation(**merged_dict)
    assert len(example.get_gold_parses(merge=False, vocab=nlp.vocab)) == 2
    assert len(example.get_gold_parses(merge=True, vocab=nlp.vocab)) == 1

    split_examples = example.split_sents()
    assert len(split_examples) == 2

    token_annotation_1 = split_examples[0].token_annotation
    assert token_annotation_1.ids == [1, 2, 3]
    assert token_annotation_1.words == ["Hi", "there", "everyone"]
    assert token_annotation_1.tags == ["INTJ", "ADV", "PRON"]
    assert token_annotation_1.sent_starts == [1, 0, 0]

    token_annotation_2 = split_examples[1].token_annotation
    assert token_annotation_2.ids == [4, 5, 6, 7]
    assert token_annotation_2.words == ["It", "is", "just", "me"]
    assert token_annotation_2.tags == ["PRON", "AUX", "ADV", "PRON"]
    assert token_annotation_2.sent_starts == [1, 0, 0, 0]


def test_tuples_to_example(merged_dict):
    ex = Example()
    ex.set_token_annotation(**merged_dict)
    cats = {"TRAVEL": 1.0, "BAKING": 0.0}
    ex.set_doc_annotation(cats=cats)
    ex_dict = ex.to_dict()

    assert ex_dict["token_annotation"]["ids"] == merged_dict["ids"]
    assert ex_dict["token_annotation"]["words"] == merged_dict["words"]
    assert ex_dict["token_annotation"]["tags"] == merged_dict["tags"]
    assert ex_dict["token_annotation"]["sent_starts"] == merged_dict["sent_starts"]
    assert ex_dict["doc_annotation"]["cats"] == cats
