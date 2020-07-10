import numpy
from spacy.errors import AlignmentError
from spacy.gold import biluo_tags_from_offsets, offsets_from_biluo_tags
from spacy.gold import spans_from_biluo_tags, iob_to_biluo
from spacy.gold import Corpus, docs_to_json
from spacy.gold.example import Example
from spacy.gold.converters import json2docs
from spacy.lang.en import English
from spacy.pipeline import EntityRuler
from spacy.tokens import Doc, DocBin
from spacy.util import get_words_and_spaces, minibatch
from thinc.api import compounding
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


def test_example_constructor(en_vocab):
    words = ["I", "like", "stuff"]
    tags = ["NOUN", "VERB", "NOUN"]
    tag_ids = [en_vocab.strings.add(tag) for tag in tags]
    predicted = Doc(en_vocab, words=words)
    reference = Doc(en_vocab, words=words)
    reference = reference.from_array("TAG", numpy.array(tag_ids, dtype="uint64"))
    example = Example(predicted, reference)
    tags = example.get_aligned("TAG", as_string=True)
    assert tags == ["NOUN", "VERB", "NOUN"]


def test_example_from_dict_tags(en_vocab):
    words = ["I", "like", "stuff"]
    tags = ["NOUN", "VERB", "NOUN"]
    predicted = Doc(en_vocab, words=words)
    example = Example.from_dict(predicted, {"TAGS": tags})
    tags = example.get_aligned("TAG", as_string=True)
    assert tags == ["NOUN", "VERB", "NOUN"]


def test_example_from_dict_no_ner(en_vocab):
    words = ["a", "b", "c", "d"]
    spaces = [True, True, False, True]
    predicted = Doc(en_vocab, words=words, spaces=spaces)
    example = Example.from_dict(predicted, {"words": words})
    ner_tags = example.get_aligned_ner()
    assert ner_tags == [None, None, None, None]


def test_example_from_dict_some_ner(en_vocab):
    words = ["a", "b", "c", "d"]
    spaces = [True, True, False, True]
    predicted = Doc(en_vocab, words=words, spaces=spaces)
    example = Example.from_dict(
        predicted, {"words": words, "entities": ["U-LOC", None, None, None]}
    )
    ner_tags = example.get_aligned_ner()
    assert ner_tags == ["U-LOC", None, None, None]


def test_json2docs_no_ner(en_vocab):
    data = [
        {
            "id": 1,
            "paragraphs": [
                {
                    "sentences": [
                        {
                            "tokens": [
                                {"dep": "nn", "head": 1, "tag": "NNP", "orth": "Ms."},
                                {
                                    "dep": "nsubj",
                                    "head": 1,
                                    "tag": "NNP",
                                    "orth": "Haag",
                                },
                                {
                                    "dep": "ROOT",
                                    "head": 0,
                                    "tag": "VBZ",
                                    "orth": "plays",
                                },
                                {
                                    "dep": "dobj",
                                    "head": -1,
                                    "tag": "NNP",
                                    "orth": "Elianti",
                                },
                                {"dep": "punct", "head": -2, "tag": ".", "orth": "."},
                            ]
                        }
                    ]
                }
            ],
        }
    ]
    docs = json2docs(data)
    assert len(docs) == 1
    for doc in docs:
        assert not doc.is_nered
    for token in doc:
        assert token.ent_iob == 0
    eg = Example(
        Doc(
            doc.vocab,
            words=[w.text for w in doc],
            spaces=[bool(w.whitespace_) for w in doc],
        ),
        doc,
    )
    ner_tags = eg.get_aligned_ner()
    assert ner_tags == [None, None, None, None, None]


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


def test_gold_biluo_one_to_many(en_vocab, en_tokenizer):
    words = ["Mr and ", "Mrs Smith", "flew to", "San Francisco Valley", "."]
    spaces = [True, True, True, False, False]
    doc = Doc(en_vocab, words=words, spaces=spaces)
    prefix = "Mr and Mrs Smith flew to "
    entities = [(len(prefix), len(prefix + "San Francisco Valley"), "LOC")]
    gold_words = ["Mr and Mrs Smith", "flew", "to", "San", "Francisco", "Valley", "."]
    example = Example.from_dict(doc, {"words": gold_words, "entities": entities})
    ner_tags = example.get_aligned_ner()
    assert ner_tags == ["O", "O", "O", "U-LOC", "O"]

    entities = [
        (len("Mr and "), len("Mr and Mrs Smith"), "PERSON"),  # "Mrs Smith" is a PERSON
        (len(prefix), len(prefix + "San Francisco Valley"), "LOC"),
    ]
    gold_words = ["Mr and", "Mrs", "Smith", "flew", "to", "San", "Francisco", "Valley", "."]
    example = Example.from_dict(doc, {"words": gold_words, "entities": entities})
    ner_tags = example.get_aligned_ner()
    assert ner_tags == ["O", "U-PERSON", "O", "U-LOC", "O"]

    entities = [
        (len("Mr and "), len("Mr and Mrs"), "PERSON"),  # "Mrs" is a Person
        (len(prefix), len(prefix + "San Francisco Valley"), "LOC"),
    ]
    gold_words = ["Mr and", "Mrs", "Smith", "flew", "to", "San", "Francisco", "Valley", "."]
    example = Example.from_dict(doc, {"words": gold_words, "entities": entities})
    ner_tags = example.get_aligned_ner()
    assert ner_tags == ["O", None, "O", "U-LOC", "O"]


def test_gold_biluo_many_to_one(en_vocab, en_tokenizer):
    words = ["Mr and", "Mrs", "Smith", "flew", "to", "San", "Francisco", "Valley", "."]
    spaces = [True, True, True, True, True, True, True, False, False]
    doc = Doc(en_vocab, words=words, spaces=spaces)
    prefix = "Mr and Mrs Smith flew to "
    entities = [(len(prefix), len(prefix + "San Francisco Valley"), "LOC")]
    gold_words = ["Mr and Mrs Smith", "flew to", "San Francisco Valley", "."]
    example = Example.from_dict(doc, {"words": gold_words, "entities": entities})
    ner_tags = example.get_aligned_ner()
    assert ner_tags == ["O", "O", "O", "O", "O", "B-LOC", "I-LOC", "L-LOC", "O"]

    entities = [
        (len("Mr and "), len("Mr and Mrs Smith"), "PERSON"),  # "Mrs Smith" is a PERSON
        (len(prefix), len(prefix + "San Francisco Valley"), "LOC"),
    ]
    gold_words = ["Mr and", "Mrs Smith", "flew to", "San Francisco Valley", "."]
    example = Example.from_dict(doc, {"words": gold_words, "entities": entities})
    ner_tags = example.get_aligned_ner()
    assert ner_tags == ["O", "B-PERSON", "L-PERSON", "O", "O", "B-LOC", "I-LOC", "L-LOC", "O"]


def test_gold_biluo_misaligned(en_vocab, en_tokenizer):
    words = ["Mr and Mrs", "Smith", "flew", "to", "San Francisco", "Valley", "."]
    spaces = [True, True, True, True, True, False, False]
    doc = Doc(en_vocab, words=words, spaces=spaces)
    prefix = "Mr and Mrs Smith flew to "
    entities = [(len(prefix), len(prefix + "San Francisco Valley"), "LOC")]
    gold_words = ["Mr", "and Mrs Smith", "flew to", "San", "Francisco Valley", "."]
    example = Example.from_dict(doc, {"words": gold_words, "entities": entities})
    ner_tags = example.get_aligned_ner()
    assert ner_tags == ["O", "O", "O", "O", "B-LOC", "L-LOC", "O"]

    entities = [
        (len("Mr and "), len("Mr and Mrs Smith"), "PERSON"),  # "Mrs Smith" is a PERSON
        (len(prefix), len(prefix + "San Francisco Valley"), "LOC"),
    ]
    gold_words = ["Mr and", "Mrs Smith", "flew to", "San", "Francisco Valley", "."]
    example = Example.from_dict(doc, {"words": gold_words, "entities": entities})
    ner_tags = example.get_aligned_ner()
    assert ner_tags == [None, None, "O", "O", "B-LOC", "L-LOC", "O"]


def test_gold_biluo_additional_whitespace(en_vocab, en_tokenizer):
    # additional whitespace tokens in GoldParse words
    words, spaces = get_words_and_spaces(
        ["I", "flew", "to", "San Francisco", "Valley", "."],
        "I flew  to San Francisco Valley.",
    )
    doc = Doc(en_vocab, words=words, spaces=spaces)
    prefix = "I flew  to "
    entities = [(len(prefix), len(prefix + "San Francisco Valley"), "LOC")]
    gold_words = ["I", "flew", " ", "to", "San Francisco Valley", "."]
    gold_spaces = [True, True, False, True, False, False]
    example = Example.from_dict(
        doc, {"words": gold_words, "spaces": gold_spaces, "entities": entities}
    )
    ner_tags = example.get_aligned_ner()
    assert ner_tags == ["O", "O", "O", "O", "B-LOC", "L-LOC", "O"]


def test_gold_biluo_4791(en_vocab, en_tokenizer):
    doc = en_tokenizer("I'll return the ₹54 amount")
    gold_words = ["I", "'ll", "return", "the", "₹", "54", "amount"]
    gold_spaces = [False, True, True, True, False, True, False]
    entities = [(16, 19, "MONEY")]
    example = Example.from_dict(
        doc, {"words": gold_words, "spaces": gold_spaces, "entities": entities}
    )
    ner_tags = example.get_aligned_ner()
    assert ner_tags == ["O", "O", "O", "O", "U-MONEY", "O"]

    doc = en_tokenizer("I'll return the $54 amount")
    gold_words = ["I", "'ll", "return", "the", "$", "54", "amount"]
    gold_spaces = [False, True, True, True, False, True, False]
    entities = [(16, 19, "MONEY")]
    example = Example.from_dict(
        doc, {"words": gold_words, "spaces": gold_spaces, "entities": entities}
    )
    ner_tags = example.get_aligned_ner()
    assert ner_tags == ["O", "O", "O", "O", "B-MONEY", "L-MONEY", "O"]


def test_roundtrip_offsets_biluo_conversion(en_tokenizer):
    text = "I flew to Silicon Valley via London."
    biluo_tags = ["O", "O", "O", "B-LOC", "L-LOC", "O", "U-GPE", "O"]
    offsets = [(10, 24, "LOC"), (29, 35, "GPE")]
    doc = en_tokenizer(text)
    biluo_tags_converted = biluo_tags_from_offsets(doc, offsets)
    assert biluo_tags_converted == biluo_tags
    offsets_converted = offsets_from_biluo_tags(doc, biluo_tags)
    offsets_converted = [ent for ent in offsets if ent[2]]
    assert offsets_converted == offsets


def test_biluo_spans(en_tokenizer):
    doc = en_tokenizer("I flew to Silicon Valley via London.")
    biluo_tags = ["O", "O", "O", "B-LOC", "L-LOC", "O", "U-GPE", "O"]
    spans = spans_from_biluo_tags(doc, biluo_tags)
    spans = [span for span in spans if span.label_]
    assert len(spans) == 2
    assert spans[0].text == "Silicon Valley"
    assert spans[0].label_ == "LOC"
    assert spans[1].text == "London"
    assert spans[1].label_ == "GPE"


def test_aligned_spans_y2x(en_vocab, en_tokenizer):
    words = ["Mr and Mrs Smith", "flew", "to", "San Francisco Valley", "."]
    spaces = [True, True, True, False, False]
    doc = Doc(en_vocab, words=words, spaces=spaces)
    prefix = "Mr and Mrs Smith flew to "
    entities = [
        (0, len("Mr and Mrs Smith"), "PERSON"),
        (len(prefix), len(prefix + "San Francisco Valley"), "LOC"),
    ]
    tokens_ref = ["Mr", "and", "Mrs", "Smith", "flew", "to", "San", "Francisco", "Valley", "."]
    example = Example.from_dict(doc, {"words": tokens_ref, "entities": entities})
    ents_ref = example.reference.ents
    assert [(ent.start, ent.end) for ent in ents_ref] == [(0, 4), (6, 9)]
    ents_y2x = example.get_aligned_spans_y2x(ents_ref)
    assert [(ent.start, ent.end) for ent in ents_y2x] == [(0, 1), (3, 4)]


def test_aligned_spans_x2y(en_vocab, en_tokenizer):
    text = "Mr and Mrs Smith flew to San Francisco Valley"
    nlp = English()
    ruler = EntityRuler(nlp)
    patterns = [{"label": "PERSON", "pattern": "Mr and Mrs Smith"},
                {"label": "LOC", "pattern": "San Francisco Valley"}]
    ruler.add_patterns(patterns)
    nlp.add_pipe(ruler)
    doc = nlp(text)
    assert [(ent.start, ent.end) for ent in doc.ents] == [(0, 4), (6, 9)]
    prefix = "Mr and Mrs Smith flew to "
    entities = [
        (0, len("Mr and Mrs Smith"), "PERSON"),
        (len(prefix), len(prefix + "San Francisco Valley"), "LOC"),
    ]
    tokens_ref = ["Mr and Mrs", "Smith", "flew", "to", "San Francisco", "Valley"]
    example = Example.from_dict(doc, {"words": tokens_ref, "entities": entities})
    assert [(ent.start, ent.end) for ent in example.reference.ents] == [(0, 2), (4, 6)]

    # Ensure that 'get_aligned_spans_x2y' has the aligned entities correct
    ents_pred = example.predicted.ents
    assert [(ent.start, ent.end) for ent in ents_pred] == [(0, 4), (6, 9)]
    ents_x2y = example.get_aligned_spans_x2y(ents_pred)
    assert [(ent.start, ent.end) for ent in ents_x2y] == [(0, 2), (4, 6)]


def test_gold_ner_missing_tags(en_tokenizer):
    doc = en_tokenizer("I flew to Silicon Valley via London.")
    biluo_tags = [None, "O", "O", "B-LOC", "L-LOC", "O", "U-GPE", "O"]
    example = Example.from_dict(doc, {"entities": biluo_tags})
    assert example.get_aligned("ENT_IOB") == [0, 2, 2, 3, 1, 2, 3, 2]


def test_projectivize(en_tokenizer):
    doc = en_tokenizer("He pretty quickly walks away")
    heads = [3, 2, 3, 0, 2]
    example = Example.from_dict(doc, {"heads": heads})
    proj_heads, proj_labels = example.get_aligned_parse(projectivize=True)
    nonproj_heads, nonproj_labels = example.get_aligned_parse(projectivize=False)
    assert proj_heads == [3, 2, 3, 0, 3]
    assert nonproj_heads == [3, 2, 3, 0, 2]


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
        make_orth_variants_example(nlp, train_example, orth_variant_level=0.2)


@pytest.mark.skip("Outdated")
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
def test_align(tokens_a, tokens_b, expected):  # noqa
    cost, a2b, b2a, a2b_multi, b2a_multi = align(tokens_a, tokens_b)  # noqa
    assert (cost, list(a2b), list(b2a), a2b_multi, b2a_multi) == expected  # noqa
    # check symmetry
    cost, a2b, b2a, a2b_multi, b2a_multi = align(tokens_b, tokens_a)  # noqa
    assert (cost, list(b2a), list(a2b), b2a_multi, a2b_multi) == expected  # noqa


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
    ner_tags = example.get_aligned_ner()
    assert ner_tags == ["O", "U-DATE"]
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

    _train_tuples(train_data)


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
        _train_tuples(train_data)


def _train_tuples(train_data):
    nlp = English()
    ner = nlp.create_pipe("ner")
    ner.add_label("ORG")
    ner.add_label("LOC")
    nlp.add_pipe(ner)

    train_examples = []
    for t in train_data:
        train_examples.append(Example.from_dict(nlp.make_doc(t[0]), t[1]))

    optimizer = nlp.begin_training()
    for i in range(5):
        losses = {}
        batches = minibatch(train_examples, size=compounding(4.0, 32.0, 1.001))
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
