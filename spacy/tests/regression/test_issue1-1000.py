import pytest
import random
from spacy import util
from spacy.training import Example
from spacy.matcher import Matcher
from spacy.attrs import IS_PUNCT, ORTH, LOWER
from spacy.vocab import Vocab
from spacy.lang.en import English
from spacy.lookups import Lookups
from spacy.tokens import Doc, Span

from ..util import make_tempdir


@pytest.mark.parametrize(
    "patterns",
    [
        [[{"LOWER": "celtics"}], [{"LOWER": "boston"}, {"LOWER": "celtics"}]],
        [[{"LOWER": "boston"}, {"LOWER": "celtics"}], [{"LOWER": "celtics"}]],
    ],
)
def test_issue118(en_tokenizer, patterns):
    """Test a bug that arose from having overlapping matches"""
    text = (
        "how many points did lebron james score against the boston celtics last night"
    )
    doc = en_tokenizer(text)
    ORG = doc.vocab.strings["ORG"]
    matcher = Matcher(doc.vocab)
    matcher.add("BostonCeltics", patterns)
    assert len(list(doc.ents)) == 0
    matches = [(ORG, start, end) for _, start, end in matcher(doc)]
    assert matches == [(ORG, 9, 11), (ORG, 10, 11)]
    doc.ents = matches[:1]
    ents = list(doc.ents)
    assert len(ents) == 1
    assert ents[0].label == ORG
    assert ents[0].start == 9
    assert ents[0].end == 11


@pytest.mark.parametrize(
    "patterns",
    [
        [[{"LOWER": "boston"}], [{"LOWER": "boston"}, {"LOWER": "celtics"}]],
        [[{"LOWER": "boston"}, {"LOWER": "celtics"}], [{"LOWER": "boston"}]],
    ],
)
def test_issue118_prefix_reorder(en_tokenizer, patterns):
    """Test a bug that arose from having overlapping matches"""
    text = (
        "how many points did lebron james score against the boston celtics last night"
    )
    doc = en_tokenizer(text)
    ORG = doc.vocab.strings["ORG"]
    matcher = Matcher(doc.vocab)
    matcher.add("BostonCeltics", patterns)
    assert len(list(doc.ents)) == 0
    matches = [(ORG, start, end) for _, start, end in matcher(doc)]
    doc.ents += tuple(matches)[1:]
    assert matches == [(ORG, 9, 10), (ORG, 9, 11)]
    ents = doc.ents
    assert len(ents) == 1
    assert ents[0].label == ORG
    assert ents[0].start == 9
    assert ents[0].end == 11


def test_issue242(en_tokenizer):
    """Test overlapping multi-word phrases."""
    text = "There are different food safety standards in different countries."
    patterns = [
        [{"LOWER": "food"}, {"LOWER": "safety"}],
        [{"LOWER": "safety"}, {"LOWER": "standards"}],
    ]
    doc = en_tokenizer(text)
    matcher = Matcher(doc.vocab)
    matcher.add("FOOD", patterns)
    matches = [(ent_type, start, end) for ent_type, start, end in matcher(doc)]
    match1, match2 = matches
    assert match1[1] == 3
    assert match1[2] == 5
    assert match2[1] == 4
    assert match2[2] == 6
    with pytest.raises(ValueError):
        # One token can only be part of one entity, so test that the matches
        # can't be added as entities
        doc.ents += tuple(matches)


def test_issue309(en_vocab):
    """Test Issue #309: SBD fails on empty string"""
    doc = Doc(en_vocab, words=[" "], heads=[0], deps=["ROOT"])
    assert len(doc) == 1
    sents = list(doc.sents)
    assert len(sents) == 1


def test_issue351(en_tokenizer):
    doc = en_tokenizer("   This is a cat.")
    assert doc[0].idx == 0
    assert len(doc[0]) == 3
    assert doc[1].idx == 3


def test_issue360(en_tokenizer):
    """Test tokenization of big ellipsis"""
    tokens = en_tokenizer("$45...............Asking")
    assert len(tokens) > 2


@pytest.mark.parametrize("text1,text2", [("cat", "dog")])
def test_issue361(en_vocab, text1, text2):
    """Test Issue #361: Equality of lexemes"""
    assert en_vocab[text1] == en_vocab[text1]
    assert en_vocab[text1] != en_vocab[text2]


def test_issue587(en_tokenizer):
    """Test that Matcher doesn't segfault on particular input"""
    doc = en_tokenizer("a b; c")
    matcher = Matcher(doc.vocab)
    matcher.add("TEST1", [[{ORTH: "a"}, {ORTH: "b"}]])
    matches = matcher(doc)
    assert len(matches) == 1
    matcher.add("TEST2", [[{ORTH: "a"}, {ORTH: "b"}, {IS_PUNCT: True}, {ORTH: "c"}]])
    matches = matcher(doc)
    assert len(matches) == 2
    matcher.add("TEST3", [[{ORTH: "a"}, {ORTH: "b"}, {IS_PUNCT: True}, {ORTH: "d"}]])
    matches = matcher(doc)
    assert len(matches) == 2


def test_issue588(en_vocab):
    matcher = Matcher(en_vocab)
    with pytest.raises(ValueError):
        matcher.add("TEST", [[]])


def test_issue590(en_vocab):
    """Test overlapping matches"""
    doc = Doc(en_vocab, words=["n", "=", "1", ";", "a", ":", "5", "%"])
    matcher = Matcher(en_vocab)
    matcher.add(
        "ab", [[{"IS_ALPHA": True}, {"ORTH": ":"}, {"LIKE_NUM": True}, {"ORTH": "%"}]]
    )
    matcher.add("ab", [[{"IS_ALPHA": True}, {"ORTH": "="}, {"LIKE_NUM": True}]])
    matches = matcher(doc)
    assert len(matches) == 2


@pytest.mark.skip(reason="Old vocab-based lemmatization")
def test_issue595():
    """Test lemmatization of base forms"""
    words = ["Do", "n't", "feed", "the", "dog"]
    lookups = Lookups()
    lookups.add_table("lemma_rules", {"verb": [["ed", "e"]]})
    lookups.add_table("lemma_index", {"verb": {}})
    lookups.add_table("lemma_exc", {"verb": {}})
    vocab = Vocab()
    doc = Doc(vocab, words=words)
    doc[2].tag_ = "VB"
    assert doc[2].text == "feed"
    assert doc[2].lemma_ == "feed"


def test_issue599(en_vocab):
    doc = Doc(en_vocab)
    doc2 = Doc(doc.vocab)
    doc2.from_bytes(doc.to_bytes())
    assert doc2.has_annotation("DEP")


def test_issue600():
    vocab = Vocab(tag_map={"NN": {"pos": "NOUN"}})
    doc = Doc(vocab, words=["hello"])
    doc[0].tag_ = "NN"


def test_issue615(en_tokenizer):
    def merge_phrases(matcher, doc, i, matches):
        """Merge a phrase. We have to be careful here because we'll change the
        token indices. To avoid problems, merge all the phrases once we're called
        on the last match."""
        if i != len(matches) - 1:
            return None
        spans = [Span(doc, start, end, label=label) for label, start, end in matches]
        with doc.retokenize() as retokenizer:
            for span in spans:
                tag = "NNP" if span.label_ else span.root.tag_
                attrs = {"tag": tag, "lemma": span.text}
                retokenizer.merge(span, attrs=attrs)
                doc.ents = doc.ents + (span,)

    text = "The golf club is broken"
    pattern = [{"ORTH": "golf"}, {"ORTH": "club"}]
    label = "Sport_Equipment"
    doc = en_tokenizer(text)
    matcher = Matcher(doc.vocab)
    matcher.add(label, [pattern], on_match=merge_phrases)
    matcher(doc)
    entities = list(doc.ents)
    assert entities != []
    assert entities[0].label != 0


@pytest.mark.parametrize("text,number", [("7am", "7"), ("11p.m.", "11")])
def test_issue736(en_tokenizer, text, number):
    """Test that times like "7am" are tokenized correctly and that numbers are
    converted to string."""
    tokens = en_tokenizer(text)
    assert len(tokens) == 2
    assert tokens[0].text == number


@pytest.mark.parametrize("text", ["3/4/2012", "01/12/1900"])
def test_issue740(en_tokenizer, text):
    """Test that dates are not split and kept as one token. This behaviour is
    currently inconsistent, since dates separated by hyphens are still split.
    This will be hard to prevent without causing clashes with numeric ranges."""
    tokens = en_tokenizer(text)
    assert len(tokens) == 1


def test_issue743():
    doc = Doc(Vocab(), ["hello", "world"])
    token = doc[0]
    s = set([token])
    items = list(s)
    assert items[0] is token


@pytest.mark.parametrize("text", ["We were scared", "We Were Scared"])
def test_issue744(en_tokenizer, text):
    """Test that 'were' and 'Were' are excluded from the contractions
    generated by the English tokenizer exceptions."""
    tokens = en_tokenizer(text)
    assert len(tokens) == 3
    assert tokens[1].text.lower() == "were"


@pytest.mark.parametrize(
    "text,is_num", [("one", True), ("ten", True), ("teneleven", False)]
)
def test_issue759(en_tokenizer, text, is_num):
    tokens = en_tokenizer(text)
    assert tokens[0].like_num == is_num


@pytest.mark.parametrize("text", ["Shell", "shell", "Shed", "shed"])
def test_issue775(en_tokenizer, text):
    """Test that 'Shell' and 'shell' are excluded from the contractions
    generated by the English tokenizer exceptions."""
    tokens = en_tokenizer(text)
    assert len(tokens) == 1
    assert tokens[0].text == text


@pytest.mark.parametrize("text", ["This is a string ", "This is a string\u0020"])
def test_issue792(en_tokenizer, text):
    """Test for Issue #792: Trailing whitespace is removed after tokenization."""
    doc = en_tokenizer(text)
    assert "".join([token.text_with_ws for token in doc]) == text


@pytest.mark.parametrize("text", ["This is a string", "This is a string\n"])
def test_control_issue792(en_tokenizer, text):
    """Test base case for Issue #792: Non-trailing whitespace"""
    doc = en_tokenizer(text)
    assert "".join([token.text_with_ws for token in doc]) == text


@pytest.mark.skip(
    reason="Can not be fixed unless with variable-width lookbehinds, cf. PR #3218"
)
@pytest.mark.parametrize(
    "text,tokens",
    [
        ('"deserve,"--and', ['"', "deserve", ',"--', "and"]),
        ("exception;--exclusive", ["exception", ";--", "exclusive"]),
        ("day.--Is", ["day", ".--", "Is"]),
        ("refinement:--just", ["refinement", ":--", "just"]),
        ("memories?--To", ["memories", "?--", "To"]),
        ("Useful.=--Therefore", ["Useful", ".=--", "Therefore"]),
        ("=Hope.=--Pandora", ["=", "Hope", ".=--", "Pandora"]),
    ],
)
def test_issue801(en_tokenizer, text, tokens):
    """Test that special characters + hyphens are split correctly."""
    doc = en_tokenizer(text)
    assert len(doc) == len(tokens)
    assert [t.text for t in doc] == tokens


@pytest.mark.parametrize(
    "text,expected_tokens",
    [
        (
            "Smörsåsen används bl.a. till fisk",
            ["Smörsåsen", "används", "bl.a.", "till", "fisk"],
        ),
        (
            "Jag kommer först kl. 13 p.g.a. diverse förseningar",
            ["Jag", "kommer", "först", "kl.", "13", "p.g.a.", "diverse", "förseningar"],
        ),
    ],
)
def test_issue805(sv_tokenizer, text, expected_tokens):
    tokens = sv_tokenizer(text)
    token_list = [token.text for token in tokens if not token.is_space]
    assert expected_tokens == token_list


def test_issue850():
    """The variable-length pattern matches the succeeding token. Check we
    handle the ambiguity correctly."""
    vocab = Vocab(lex_attr_getters={LOWER: lambda string: string.lower()})
    matcher = Matcher(vocab)
    pattern = [{"LOWER": "bob"}, {"OP": "*"}, {"LOWER": "frank"}]
    matcher.add("FarAway", [pattern])
    doc = Doc(matcher.vocab, words=["bob", "and", "and", "frank"])
    match = matcher(doc)
    assert len(match) == 1
    ent_id, start, end = match[0]
    assert start == 0
    assert end == 4


def test_issue850_basic():
    """Test Matcher matches with '*' operator and Boolean flag"""
    vocab = Vocab(lex_attr_getters={LOWER: lambda string: string.lower()})
    matcher = Matcher(vocab)
    pattern = [{"LOWER": "bob"}, {"OP": "*", "LOWER": "and"}, {"LOWER": "frank"}]
    matcher.add("FarAway", [pattern])
    doc = Doc(matcher.vocab, words=["bob", "and", "and", "frank"])
    match = matcher(doc)
    assert len(match) == 1
    ent_id, start, end = match[0]
    assert start == 0
    assert end == 4


@pytest.mark.skip(
    reason="French exception list is not enabled in the default tokenizer anymore"
)
@pytest.mark.parametrize(
    "text", ["au-delàs", "pair-programmâmes", "terra-formées", "σ-compacts"]
)
def test_issue852(fr_tokenizer, text):
    """Test that French tokenizer exceptions are imported correctly."""
    tokens = fr_tokenizer(text)
    assert len(tokens) == 1


@pytest.mark.parametrize(
    "text", ["aaabbb@ccc.com\nThank you!", "aaabbb@ccc.com \nThank you!"]
)
def test_issue859(en_tokenizer, text):
    """Test that no extra space is added in doc.text method."""
    doc = en_tokenizer(text)
    assert doc.text == text


@pytest.mark.parametrize("text", ["Datum:2014-06-02\nDokument:76467"])
def test_issue886(en_tokenizer, text):
    """Test that token.idx matches the original text index for texts with newlines."""
    doc = en_tokenizer(text)
    for token in doc:
        assert len(token.text) == len(token.text_with_ws)
        assert text[token.idx] == token.text[0]


@pytest.mark.parametrize("text", ["want/need"])
def test_issue891(en_tokenizer, text):
    """Test that / infixes are split correctly."""
    tokens = en_tokenizer(text)
    assert len(tokens) == 3
    assert tokens[1].text == "/"


@pytest.mark.skip(reason="Old vocab-based lemmatization")
@pytest.mark.parametrize(
    "text,tag,lemma",
    [("anus", "NN", "anus"), ("princess", "NN", "princess"), ("inner", "JJ", "inner")],
)
def test_issue912(en_vocab, text, tag, lemma):
    """Test base-forms are preserved."""
    doc = Doc(en_vocab, words=[text])
    doc[0].tag_ = tag
    assert doc[0].lemma_ == lemma


@pytest.mark.slow
def test_issue957(en_tokenizer):
    """Test that spaCy doesn't hang on many punctuation characters.
    If this test hangs, check (new) regular expressions for conflicting greedy operators
    """
    # Skip test if pytest-timeout is not installed
    pytest.importorskip("pytest_timeout")
    for punct in [".", ",", "'", '"', ":", "?", "!", ";", "-"]:
        string = "0"
        for i in range(1, 100):
            string += punct + str(i)
        doc = en_tokenizer(string)
        assert doc


def test_issue999():
    """Test that adding entities and resuming training works passably OK.
    There are two issues here:
    1) We have to re-add labels. This isn't very nice.
    2) There's no way to set the learning rate for the weight update, so we
        end up out-of-scale, causing it to learn too fast.
    """
    TRAIN_DATA = [
        ["hey", []],
        ["howdy", []],
        ["hey there", []],
        ["hello", []],
        ["hi", []],
        ["i'm looking for a place to eat", []],
        ["i'm looking for a place in the north of town", [(31, 36, "LOCATION")]],
        ["show me chinese restaurants", [(8, 15, "CUISINE")]],
        ["show me chines restaurants", [(8, 14, "CUISINE")]],
    ]
    nlp = English()
    ner = nlp.add_pipe("ner")
    for _, offsets in TRAIN_DATA:
        for start, end, label in offsets:
            ner.add_label(label)
    nlp.initialize()
    for itn in range(20):
        random.shuffle(TRAIN_DATA)
        for raw_text, entity_offsets in TRAIN_DATA:
            example = Example.from_dict(
                nlp.make_doc(raw_text), {"entities": entity_offsets}
            )
            nlp.update([example])

    with make_tempdir() as model_dir:
        nlp.to_disk(model_dir)
        nlp2 = util.load_model_from_path(model_dir)

    for raw_text, entity_offsets in TRAIN_DATA:
        doc = nlp2(raw_text)
        ents = {(ent.start_char, ent.end_char): ent.label_ for ent in doc.ents}
        for start, end, label in entity_offsets:
            if (start, end) in ents:
                assert ents[(start, end)] == label
                break
            else:
                if entity_offsets:
                    raise Exception(ents)
