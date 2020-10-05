import pytest
from spacy.vocab import Vocab
from spacy.tokens import Doc, Token


def test_doc_retokenize_split(en_vocab):
    words = ["LosAngeles", "start", "."]
    heads = [1, 2, 2]
    doc = Doc(en_vocab, words=words, heads=heads)
    assert len(doc) == 3
    assert len(str(doc)) == 19
    assert doc[0].head.text == "start"
    assert doc[1].head.text == "."
    with doc.retokenize() as retokenizer:
        retokenizer.split(
            doc[0],
            ["Los", "Angeles"],
            [(doc[0], 1), doc[1]],
            attrs={
                "tag": ["NNP"] * 2,
                "lemma": ["Los", "Angeles"],
                "ent_type": ["GPE"] * 2,
                "morph": ["Number=Sing"] * 2,
            },
        )
    assert len(doc) == 4
    assert doc[0].text == "Los"
    assert doc[0].head.text == "Angeles"
    assert doc[0].idx == 0
    assert str(doc[0].morph) == "Number=Sing"
    assert doc[1].idx == 3
    assert doc[1].text == "Angeles"
    assert doc[1].head.text == "start"
    assert str(doc[1].morph) == "Number=Sing"
    assert doc[2].text == "start"
    assert doc[2].head.text == "."
    assert doc[3].text == "."
    assert doc[3].head.text == "."
    assert len(str(doc)) == 19


def test_doc_retokenize_split_dependencies(en_vocab):
    doc = Doc(en_vocab, words=["LosAngeles", "start", "."])
    dep1 = doc.vocab.strings.add("amod")
    dep2 = doc.vocab.strings.add("subject")
    with doc.retokenize() as retokenizer:
        retokenizer.split(
            doc[0],
            ["Los", "Angeles"],
            [(doc[0], 1), doc[1]],
            attrs={"dep": [dep1, dep2]},
        )
    assert doc[0].dep == dep1
    assert doc[1].dep == dep2


def test_doc_retokenize_split_heads_error(en_vocab):
    doc = Doc(en_vocab, words=["LosAngeles", "start", "."])
    # Not enough heads
    with pytest.raises(ValueError):
        with doc.retokenize() as retokenizer:
            retokenizer.split(doc[0], ["Los", "Angeles"], [doc[1]])

    # Too many heads
    with pytest.raises(ValueError):
        with doc.retokenize() as retokenizer:
            retokenizer.split(doc[0], ["Los", "Angeles"], [doc[1], doc[1], doc[1]])


def test_doc_retokenize_spans_entity_split_iob():
    # Test entity IOB stays consistent after merging
    words = ["abc", "d", "e"]
    doc = Doc(Vocab(), words=words)
    doc.ents = [(doc.vocab.strings.add("ent-abcd"), 0, 2)]
    assert doc[0].ent_iob_ == "B"
    assert doc[1].ent_iob_ == "I"
    with doc.retokenize() as retokenizer:
        retokenizer.split(doc[0], ["a", "b", "c"], [(doc[0], 1), (doc[0], 2), doc[1]])
    assert doc[0].ent_iob_ == "B"
    assert doc[1].ent_iob_ == "I"
    assert doc[2].ent_iob_ == "I"
    assert doc[3].ent_iob_ == "I"


def test_doc_retokenize_spans_sentence_update_after_split(en_vocab):
    # fmt: off
    words = ["StewartLee", "is", "a", "stand", "up", "comedian", ".", "He",
             "lives", "in", "England", "and", "loves", "JoePasquale", "."]
    heads = [1, 1, 3, 5, 3, 1, 1, 8, 8, 8, 9, 8, 8, 14, 12]
    deps = ["nsubj", "ROOT", "det", "amod", "prt", "attr", "punct", "nsubj",
            "ROOT", "prep", "pobj", "cc", "conj", "compound", "punct"]
    # fmt: on
    doc = Doc(en_vocab, words=words, heads=heads, deps=deps)
    sent1, sent2 = list(doc.sents)
    init_len = len(sent1)
    init_len2 = len(sent2)
    with doc.retokenize() as retokenizer:
        retokenizer.split(
            doc[0],
            ["Stewart", "Lee"],
            [(doc[0], 1), doc[1]],
            attrs={"dep": ["compound", "nsubj"]},
        )
        retokenizer.split(
            doc[13],
            ["Joe", "Pasquale"],
            [(doc[13], 1), doc[12]],
            attrs={"dep": ["compound", "dobj"]},
        )
    sent1, sent2 = list(doc.sents)
    assert len(sent1) == init_len + 1
    assert len(sent2) == init_len2 + 1


def test_doc_retokenize_split_orths_mismatch(en_vocab):
    """Test that the regular retokenizer.split raises an error if the orths
    don't match the original token text. There might still be a method that
    allows this, but for the default use cases, merging and splitting should
    always conform with spaCy's non-destructive tokenization policy. Otherwise,
    it can lead to very confusing and unexpected results.
    """
    doc = Doc(en_vocab, words=["LosAngeles", "start", "."])
    with pytest.raises(ValueError):
        with doc.retokenize() as retokenizer:
            retokenizer.split(doc[0], ["L", "A"], [(doc[0], 0), (doc[0], 0)])


def test_doc_retokenize_split_extension_attrs(en_vocab):
    Token.set_extension("a", default=False, force=True)
    Token.set_extension("b", default="nothing", force=True)
    doc = Doc(en_vocab, words=["LosAngeles", "start"])
    with doc.retokenize() as retokenizer:
        heads = [(doc[0], 1), doc[1]]
        underscore = [{"a": True, "b": "1"}, {"b": "2"}]
        attrs = {"lemma": ["los", "angeles"], "_": underscore}
        retokenizer.split(doc[0], ["Los", "Angeles"], heads, attrs=attrs)
    assert doc[0].lemma_ == "los"
    assert doc[0]._.a is True
    assert doc[0]._.b == "1"
    assert doc[1].lemma_ == "angeles"
    assert doc[1]._.a is False
    assert doc[1]._.b == "2"


@pytest.mark.parametrize(
    "underscore_attrs",
    [
        [{"a": "x"}, {}],  # Overwriting getter without setter
        [{"b": "x"}, {}],  # Overwriting method
        [{"c": "x"}, {}],  # Overwriting nonexistent attribute
        [{"a": "x"}, {"x": "x"}],  # Combination
        [{"a": "x", "x": "x"}, {"x": "x"}],  # Combination
        {"x": "x"},  # Not a list of dicts
    ],
)
def test_doc_retokenize_split_extension_attrs_invalid(en_vocab, underscore_attrs):
    Token.set_extension("x", default=False, force=True)
    Token.set_extension("a", getter=lambda x: x, force=True)
    Token.set_extension("b", method=lambda x: x, force=True)
    doc = Doc(en_vocab, words=["LosAngeles", "start"])
    attrs = {"_": underscore_attrs}
    with pytest.raises(ValueError):
        with doc.retokenize() as retokenizer:
            heads = [(doc[0], 1), doc[1]]
            retokenizer.split(doc[0], ["Los", "Angeles"], heads, attrs=attrs)


def test_doc_retokenizer_split_lex_attrs(en_vocab):
    """Test that retokenization also sets attributes on the lexeme if they're
    lexical attributes. For example, if a user sets IS_STOP, it should mean that
    "all tokens with that lexeme" are marked as a stop word, so the ambiguity
    here is acceptable. Also see #2390.
    """
    assert not Doc(en_vocab, words=["Los"])[0].is_stop
    assert not Doc(en_vocab, words=["Angeles"])[0].is_stop
    doc = Doc(en_vocab, words=["LosAngeles", "start"])
    assert not doc[0].is_stop
    with doc.retokenize() as retokenizer:
        attrs = {"is_stop": [True, False]}
        heads = [(doc[0], 1), doc[1]]
        retokenizer.split(doc[0], ["Los", "Angeles"], heads, attrs=attrs)
    assert doc[0].is_stop
    assert not doc[1].is_stop


def test_doc_retokenizer_realloc(en_vocab):
    """#4604: realloc correctly when new tokens outnumber original tokens"""
    text = "Hyperglycemic adverse events following antipsychotic drug administration in the"
    doc = Doc(en_vocab, words=text.split()[:-1])
    with doc.retokenize() as retokenizer:
        token = doc[0]
        heads = [(token, 0)] * len(token)
        retokenizer.split(doc[token.i], list(token.text), heads=heads)
    doc = Doc(en_vocab, words=text.split())
    with doc.retokenize() as retokenizer:
        token = doc[0]
        heads = [(token, 0)] * len(token)
        retokenizer.split(doc[token.i], list(token.text), heads=heads)


def test_doc_retokenizer_split_norm(en_vocab):
    """#6060: reset norm in split"""
    text = "The quick brownfoxjumpsoverthe lazy dog w/ white spots"
    doc = Doc(en_vocab, words=text.split())

    # Set custom norm on the w/ token.
    doc[5].norm_ = "with"

    # Retokenize to split out the words in the token at doc[2].
    token = doc[2]
    with doc.retokenize() as retokenizer:
        retokenizer.split(
            token,
            ["brown", "fox", "jumps", "over", "the"],
            heads=[(token, idx) for idx in range(5)],
        )

    assert doc[9].text == "w/"
    assert doc[9].norm_ == "with"
    assert doc[5].text == "over"
    assert doc[5].norm_ == "over"
