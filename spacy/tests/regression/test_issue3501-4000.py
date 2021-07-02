import pytest
from spacy.language import Language
from spacy.vocab import Vocab
from spacy.pipeline import EntityRuler, DependencyParser
from spacy.pipeline.dep_parser import DEFAULT_PARSER_MODEL
from spacy import displacy, load
from spacy.displacy import parse_deps
from spacy.tokens import Doc, Token
from spacy.matcher import Matcher, PhraseMatcher
from spacy.errors import MatchPatternError
from spacy.util import minibatch
from spacy.training import Example
from spacy.lang.hi import Hindi
from spacy.lang.es import Spanish
from spacy.lang.en import English
from spacy.attrs import IS_ALPHA
from spacy import registry
from thinc.api import compounding
import spacy
import srsly
import numpy

from ..util import make_tempdir


@pytest.mark.parametrize("word", ["don't", "don’t", "I'd", "I’d"])
def test_issue3521(en_tokenizer, word):
    tok = en_tokenizer(word)[1]
    # 'not' and 'would' should be stopwords, also in their abbreviated forms
    assert tok.is_stop


def test_issue_3526_1(en_vocab):
    patterns = [
        {"label": "HELLO", "pattern": "hello world"},
        {"label": "BYE", "pattern": [{"LOWER": "bye"}, {"LOWER": "bye"}]},
        {"label": "HELLO", "pattern": [{"ORTH": "HELLO"}]},
        {"label": "COMPLEX", "pattern": [{"ORTH": "foo", "OP": "*"}]},
        {"label": "TECH_ORG", "pattern": "Apple", "id": "a1"},
    ]
    nlp = Language(vocab=en_vocab)
    ruler = EntityRuler(nlp, patterns=patterns, overwrite_ents=True)
    ruler_bytes = ruler.to_bytes()
    assert len(ruler) == len(patterns)
    assert len(ruler.labels) == 4
    assert ruler.overwrite
    new_ruler = EntityRuler(nlp)
    new_ruler = new_ruler.from_bytes(ruler_bytes)
    assert len(new_ruler) == len(ruler)
    assert len(new_ruler.labels) == 4
    assert new_ruler.overwrite == ruler.overwrite
    assert new_ruler.ent_id_sep == ruler.ent_id_sep


def test_issue_3526_2(en_vocab):
    patterns = [
        {"label": "HELLO", "pattern": "hello world"},
        {"label": "BYE", "pattern": [{"LOWER": "bye"}, {"LOWER": "bye"}]},
        {"label": "HELLO", "pattern": [{"ORTH": "HELLO"}]},
        {"label": "COMPLEX", "pattern": [{"ORTH": "foo", "OP": "*"}]},
        {"label": "TECH_ORG", "pattern": "Apple", "id": "a1"},
    ]
    nlp = Language(vocab=en_vocab)
    ruler = EntityRuler(nlp, patterns=patterns, overwrite_ents=True)
    bytes_old_style = srsly.msgpack_dumps(ruler.patterns)
    new_ruler = EntityRuler(nlp)
    new_ruler = new_ruler.from_bytes(bytes_old_style)
    assert len(new_ruler) == len(ruler)
    for pattern in ruler.patterns:
        assert pattern in new_ruler.patterns
    assert new_ruler.overwrite is not ruler.overwrite


def test_issue_3526_3(en_vocab):
    patterns = [
        {"label": "HELLO", "pattern": "hello world"},
        {"label": "BYE", "pattern": [{"LOWER": "bye"}, {"LOWER": "bye"}]},
        {"label": "HELLO", "pattern": [{"ORTH": "HELLO"}]},
        {"label": "COMPLEX", "pattern": [{"ORTH": "foo", "OP": "*"}]},
        {"label": "TECH_ORG", "pattern": "Apple", "id": "a1"},
    ]
    nlp = Language(vocab=en_vocab)
    ruler = EntityRuler(nlp, patterns=patterns, overwrite_ents=True)
    with make_tempdir() as tmpdir:
        out_file = tmpdir / "entity_ruler"
        srsly.write_jsonl(out_file.with_suffix(".jsonl"), ruler.patterns)
        new_ruler = EntityRuler(nlp).from_disk(out_file)
        for pattern in ruler.patterns:
            assert pattern in new_ruler.patterns
        assert len(new_ruler) == len(ruler)
        assert new_ruler.overwrite is not ruler.overwrite


def test_issue_3526_4(en_vocab):
    nlp = Language(vocab=en_vocab)
    patterns = [{"label": "ORG", "pattern": "Apple"}]
    config = {"overwrite_ents": True}
    ruler = nlp.add_pipe("entity_ruler", config=config)
    ruler.add_patterns(patterns)
    with make_tempdir() as tmpdir:
        nlp.to_disk(tmpdir)
        ruler = nlp.get_pipe("entity_ruler")
        assert ruler.patterns == [{"label": "ORG", "pattern": "Apple"}]
        assert ruler.overwrite is True
        nlp2 = load(tmpdir)
        new_ruler = nlp2.get_pipe("entity_ruler")
        assert new_ruler.patterns == [{"label": "ORG", "pattern": "Apple"}]
        assert new_ruler.overwrite is True


def test_issue3531():
    """Test that displaCy renderer doesn't require "settings" key."""
    example_dep = {
        "words": [
            {"text": "But", "tag": "CCONJ"},
            {"text": "Google", "tag": "PROPN"},
            {"text": "is", "tag": "VERB"},
            {"text": "starting", "tag": "VERB"},
            {"text": "from", "tag": "ADP"},
            {"text": "behind.", "tag": "ADV"},
        ],
        "arcs": [
            {"start": 0, "end": 3, "label": "cc", "dir": "left"},
            {"start": 1, "end": 3, "label": "nsubj", "dir": "left"},
            {"start": 2, "end": 3, "label": "aux", "dir": "left"},
            {"start": 3, "end": 4, "label": "prep", "dir": "right"},
            {"start": 4, "end": 5, "label": "pcomp", "dir": "right"},
        ],
    }
    example_ent = {
        "text": "But Google is starting from behind.",
        "ents": [{"start": 4, "end": 10, "label": "ORG"}],
    }
    dep_html = displacy.render(example_dep, style="dep", manual=True)
    assert dep_html
    ent_html = displacy.render(example_ent, style="ent", manual=True)
    assert ent_html


def test_issue3540(en_vocab):
    words = ["I", "live", "in", "NewYork", "right", "now"]
    tensor = numpy.asarray(
        [[1.0, 1.1], [2.0, 2.1], [3.0, 3.1], [4.0, 4.1], [5.0, 5.1], [6.0, 6.1]],
        dtype="f",
    )
    doc = Doc(en_vocab, words=words)
    doc.tensor = tensor
    gold_text = ["I", "live", "in", "NewYork", "right", "now"]
    assert [token.text for token in doc] == gold_text
    gold_lemma = ["I", "live", "in", "NewYork", "right", "now"]
    for i, lemma in enumerate(gold_lemma):
        doc[i].lemma_ = lemma
    assert [token.lemma_ for token in doc] == gold_lemma
    vectors_1 = [token.vector for token in doc]
    assert len(vectors_1) == len(doc)

    with doc.retokenize() as retokenizer:
        heads = [(doc[3], 1), doc[2]]
        attrs = {
            "POS": ["PROPN", "PROPN"],
            "LEMMA": ["New", "York"],
            "DEP": ["pobj", "compound"],
        }
        retokenizer.split(doc[3], ["New", "York"], heads=heads, attrs=attrs)

    gold_text = ["I", "live", "in", "New", "York", "right", "now"]
    assert [token.text for token in doc] == gold_text
    gold_lemma = ["I", "live", "in", "New", "York", "right", "now"]
    assert [token.lemma_ for token in doc] == gold_lemma
    vectors_2 = [token.vector for token in doc]
    assert len(vectors_2) == len(doc)
    assert vectors_1[0].tolist() == vectors_2[0].tolist()
    assert vectors_1[1].tolist() == vectors_2[1].tolist()
    assert vectors_1[2].tolist() == vectors_2[2].tolist()
    assert vectors_1[4].tolist() == vectors_2[5].tolist()
    assert vectors_1[5].tolist() == vectors_2[6].tolist()


def test_issue3549(en_vocab):
    """Test that match pattern validation doesn't raise on empty errors."""
    matcher = Matcher(en_vocab, validate=True)
    pattern = [{"LOWER": "hello"}, {"LOWER": "world"}]
    matcher.add("GOOD", [pattern])
    with pytest.raises(MatchPatternError):
        matcher.add("BAD", [[{"X": "Y"}]])


@pytest.mark.skip("Matching currently only works on strings and integers")
def test_issue3555(en_vocab):
    """Test that custom extensions with default None don't break matcher."""
    Token.set_extension("issue3555", default=None)
    matcher = Matcher(en_vocab)
    pattern = [{"ORTH": "have"}, {"_": {"issue3555": True}}]
    matcher.add("TEST", [pattern])
    doc = Doc(en_vocab, words=["have", "apple"])
    matcher(doc)


def test_issue3611():
    """Test whether adding n-grams in the textcat works even when n > token length of some docs"""
    unique_classes = ["offensive", "inoffensive"]
    x_train = [
        "This is an offensive text",
        "This is the second offensive text",
        "inoff",
    ]
    y_train = ["offensive", "offensive", "inoffensive"]
    nlp = spacy.blank("en")
    # preparing the data
    train_data = []
    for text, train_instance in zip(x_train, y_train):
        cat_dict = {label: label == train_instance for label in unique_classes}
        train_data.append(Example.from_dict(nlp.make_doc(text), {"cats": cat_dict}))
    # add a text categorizer component
    model = {
        "@architectures": "spacy.TextCatBOW.v1",
        "exclusive_classes": True,
        "ngram_size": 2,
        "no_output_layer": False,
    }
    textcat = nlp.add_pipe("textcat", config={"model": model}, last=True)
    for label in unique_classes:
        textcat.add_label(label)
    # training the network
    with nlp.select_pipes(enable="textcat"):
        optimizer = nlp.initialize()
        for i in range(3):
            losses = {}
            batches = minibatch(train_data, size=compounding(4.0, 32.0, 1.001))

            for batch in batches:
                nlp.update(examples=batch, sgd=optimizer, drop=0.1, losses=losses)


def test_issue3625():
    """Test that default punctuation rules applies to hindi unicode characters"""
    nlp = Hindi()
    doc = nlp("hi. how हुए. होटल, होटल")
    expected = ["hi", ".", "how", "हुए", ".", "होटल", ",", "होटल"]
    assert [token.text for token in doc] == expected


def test_issue3803():
    """Test that spanish num-like tokens have True for like_num attribute."""
    nlp = Spanish()
    text = "2 dos 1000 mil 12 doce"
    doc = nlp(text)

    assert [t.like_num for t in doc] == [True, True, True, True, True, True]


def _parser_example(parser):
    doc = Doc(parser.vocab, words=["a", "b", "c", "d"])
    gold = {"heads": [1, 1, 3, 3], "deps": ["right", "ROOT", "left", "ROOT"]}
    return Example.from_dict(doc, gold)


def test_issue3830_no_subtok():
    """Test that the parser doesn't have subtok label if not learn_tokens"""
    config = {
        "learn_tokens": False,
    }
    model = registry.resolve({"model": DEFAULT_PARSER_MODEL}, validate=True)["model"]
    parser = DependencyParser(Vocab(), model, **config)
    parser.add_label("nsubj")
    assert "subtok" not in parser.labels
    parser.initialize(lambda: [_parser_example(parser)])
    assert "subtok" not in parser.labels


def test_issue3830_with_subtok():
    """Test that the parser does have subtok label if learn_tokens=True."""
    config = {
        "learn_tokens": True,
    }
    model = registry.resolve({"model": DEFAULT_PARSER_MODEL}, validate=True)["model"]
    parser = DependencyParser(Vocab(), model, **config)
    parser.add_label("nsubj")
    assert "subtok" not in parser.labels
    parser.initialize(lambda: [_parser_example(parser)])
    assert "subtok" in parser.labels


def test_issue3839(en_vocab):
    """Test that match IDs returned by the matcher are correct, are in the string"""
    doc = Doc(en_vocab, words=["terrific", "group", "of", "people"])
    matcher = Matcher(en_vocab)
    match_id = "PATTERN"
    pattern1 = [{"LOWER": "terrific"}, {"OP": "?"}, {"LOWER": "group"}]
    pattern2 = [{"LOWER": "terrific"}, {"OP": "?"}, {"OP": "?"}, {"LOWER": "group"}]
    matcher.add(match_id, [pattern1])
    matches = matcher(doc)
    assert matches[0][0] == en_vocab.strings[match_id]
    matcher = Matcher(en_vocab)
    matcher.add(match_id, [pattern2])
    matches = matcher(doc)
    assert matches[0][0] == en_vocab.strings[match_id]


@pytest.mark.parametrize(
    "sentence",
    [
        "The story was to the effect that a young American student recently called on Professor Christlieb with a letter of introduction.",
        "The next month Barry Siddall joined Stoke City on a free transfer, after Chris Pearce had established himself as the Vale's #1.",
        "The next month Barry Siddall joined Stoke City on a free transfer, after Chris Pearce had established himself as the Vale's number one",
        "Indeed, making the one who remains do all the work has installed him into a position of such insolent tyranny, it will take a month at least to reduce him to his proper proportions.",
        "It was a missed assignment, but it shouldn't have resulted in a turnover ...",
    ],
)
def test_issue3869(sentence):
    """Test that the Doc's count_by function works consistently"""
    nlp = English()
    doc = nlp(sentence)
    count = 0
    for token in doc:
        count += token.is_alpha
    assert count == doc.count_by(IS_ALPHA).get(1, 0)


def test_issue3879(en_vocab):
    doc = Doc(en_vocab, words=["This", "is", "a", "test", "."])
    assert len(doc) == 5
    pattern = [{"ORTH": "This", "OP": "?"}, {"OP": "?"}, {"ORTH": "test"}]
    matcher = Matcher(en_vocab)
    matcher.add("TEST", [pattern])
    assert len(matcher(doc)) == 2  # fails because of a FP match 'is a test'


def test_issue3880():
    """Test that `nlp.pipe()` works when an empty string ends the batch.

    Fixed in v7.0.5 of Thinc.
    """
    texts = ["hello", "world", "", ""]
    nlp = English()
    nlp.add_pipe("parser").add_label("dep")
    nlp.add_pipe("ner").add_label("PERSON")
    nlp.add_pipe("tagger").add_label("NN")
    nlp.initialize()
    for doc in nlp.pipe(texts):
        pass


def test_issue3882(en_vocab):
    """Test that displaCy doesn't serialize the doc.user_data when making a
    copy of the Doc.
    """
    doc = Doc(en_vocab, words=["Hello", "world"], deps=["dep", "dep"])
    doc.user_data["test"] = set()
    parse_deps(doc)


def test_issue3951(en_vocab):
    """Test that combinations of optional rules are matched correctly."""
    matcher = Matcher(en_vocab)
    pattern = [
        {"LOWER": "hello"},
        {"LOWER": "this", "OP": "?"},
        {"OP": "?"},
        {"LOWER": "world"},
    ]
    matcher.add("TEST", [pattern])
    doc = Doc(en_vocab, words=["Hello", "my", "new", "world"])
    matches = matcher(doc)
    assert len(matches) == 0


def test_issue3959():
    """Ensure that a modified pos attribute is serialized correctly."""
    nlp = English()
    doc = nlp(
        "displaCy uses JavaScript, SVG and CSS to show you how computers understand language"
    )
    assert doc[0].pos_ == ""
    doc[0].pos_ = "NOUN"
    assert doc[0].pos_ == "NOUN"
    # usually this is already True when starting from proper models instead of blank English
    with make_tempdir() as tmp_dir:
        file_path = tmp_dir / "my_doc"
        doc.to_disk(file_path)
        doc2 = nlp("")
        doc2.from_disk(file_path)
        assert doc2[0].pos_ == "NOUN"


def test_issue3962(en_vocab):
    """Ensure that as_doc does not result in out-of-bound access of tokens.
    This is achieved by setting the head to itself if it would lie out of the span otherwise."""
    # fmt: off
    words = ["He", "jests", "at", "scars", ",", "that", "never", "felt", "a", "wound", "."]
    heads = [1, 7, 1, 2, 7, 7, 7, 7, 9, 7, 7]
    deps = ["nsubj", "ccomp", "prep", "pobj", "punct", "nsubj", "neg", "ROOT", "det", "dobj", "punct"]
    # fmt: on
    doc = Doc(en_vocab, words=words, heads=heads, deps=deps)
    span2 = doc[1:5]  # "jests at scars ,"
    doc2 = span2.as_doc()
    doc2_json = doc2.to_json()
    assert doc2_json
    # head set to itself, being the new artificial root
    assert doc2[0].head.text == "jests"
    assert doc2[0].dep_ == "dep"
    assert doc2[1].head.text == "jests"
    assert doc2[1].dep_ == "prep"
    assert doc2[2].head.text == "at"
    assert doc2[2].dep_ == "pobj"
    assert doc2[3].head.text == "jests"  # head set to the new artificial root
    assert doc2[3].dep_ == "dep"
    # We should still have 1 sentence
    assert len(list(doc2.sents)) == 1
    span3 = doc[6:9]  # "never felt a"
    doc3 = span3.as_doc()
    doc3_json = doc3.to_json()
    assert doc3_json
    assert doc3[0].head.text == "felt"
    assert doc3[0].dep_ == "neg"
    assert doc3[1].head.text == "felt"
    assert doc3[1].dep_ == "ROOT"
    assert doc3[2].head.text == "felt"  # head set to ancestor
    assert doc3[2].dep_ == "dep"
    # We should still have 1 sentence as "a" can be attached to "felt" instead of "wound"
    assert len(list(doc3.sents)) == 1


def test_issue3962_long(en_vocab):
    """Ensure that as_doc does not result in out-of-bound access of tokens.
    This is achieved by setting the head to itself if it would lie out of the span otherwise."""
    # fmt: off
    words = ["He", "jests", "at", "scars", ".", "They", "never", "felt", "a", "wound", "."]
    heads = [1, 1, 1, 2, 1, 7, 7, 7, 9, 7, 7]
    deps = ["nsubj", "ROOT", "prep", "pobj", "punct", "nsubj", "neg", "ROOT", "det", "dobj", "punct"]
    # fmt: on
    two_sent_doc = Doc(en_vocab, words=words, heads=heads, deps=deps)
    span2 = two_sent_doc[1:7]  # "jests at scars. They never"
    doc2 = span2.as_doc()
    doc2_json = doc2.to_json()
    assert doc2_json
    # head set to itself, being the new artificial root (in sentence 1)
    assert doc2[0].head.text == "jests"
    assert doc2[0].dep_ == "ROOT"
    assert doc2[1].head.text == "jests"
    assert doc2[1].dep_ == "prep"
    assert doc2[2].head.text == "at"
    assert doc2[2].dep_ == "pobj"
    assert doc2[3].head.text == "jests"
    assert doc2[3].dep_ == "punct"
    # head set to itself, being the new artificial root (in sentence 2)
    assert doc2[4].head.text == "They"
    assert doc2[4].dep_ == "dep"
    # head set to the new artificial head (in sentence 2)
    assert doc2[4].head.text == "They"
    assert doc2[4].dep_ == "dep"
    # We should still have 2 sentences
    sents = list(doc2.sents)
    assert len(sents) == 2
    assert sents[0].text == "jests at scars ."
    assert sents[1].text == "They never"


def test_issue3972(en_vocab):
    """Test that the PhraseMatcher returns duplicates for duplicate match IDs."""
    matcher = PhraseMatcher(en_vocab)
    matcher.add("A", [Doc(en_vocab, words=["New", "York"])])
    matcher.add("B", [Doc(en_vocab, words=["New", "York"])])
    doc = Doc(en_vocab, words=["I", "live", "in", "New", "York"])
    matches = matcher(doc)

    assert len(matches) == 2

    # We should have a match for each of the two rules
    found_ids = [en_vocab.strings[ent_id] for (ent_id, _, _) in matches]
    assert "A" in found_ids
    assert "B" in found_ids
