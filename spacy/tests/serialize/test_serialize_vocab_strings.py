import pickle

import pytest
from thinc.api import get_current_ops

import spacy
from spacy.lang.en import English
from spacy.strings import StringStore
from spacy.tokens import Doc
from spacy.util import ensure_path, load_model
from spacy.vectors import Vectors
from spacy.vocab import Vocab

from ..util import make_tempdir

test_strings = [([], []), (["rats", "are", "cute"], ["i", "like", "rats"])]
test_strings_attrs = [(["rats", "are", "cute"], "Hello")]


@pytest.mark.issue(599)
def test_issue599(en_vocab):
    doc = Doc(en_vocab)
    doc2 = Doc(doc.vocab)
    doc2.from_bytes(doc.to_bytes())
    assert doc2.has_annotation("DEP")


@pytest.mark.issue(4054)
def test_issue4054(en_vocab):
    """Test that a new blank model can be made with a vocab from file,
    and that serialization does not drop the language at any point."""
    nlp1 = English()
    vocab1 = nlp1.vocab
    with make_tempdir() as d:
        vocab_dir = ensure_path(d / "vocab")
        if not vocab_dir.exists():
            vocab_dir.mkdir()
        vocab1.to_disk(vocab_dir)
        vocab2 = Vocab().from_disk(vocab_dir)
        nlp2 = spacy.blank("en", vocab=vocab2)
        nlp_dir = ensure_path(d / "nlp")
        if not nlp_dir.exists():
            nlp_dir.mkdir()
        nlp2.to_disk(nlp_dir)
        nlp3 = load_model(nlp_dir)
        assert nlp3.lang == "en"


@pytest.mark.issue(4133)
def test_issue4133(en_vocab):
    nlp = English()
    vocab_bytes = nlp.vocab.to_bytes()
    words = ["Apple", "is", "looking", "at", "buying", "a", "startup"]
    pos = ["NOUN", "VERB", "ADP", "VERB", "PROPN", "NOUN", "ADP"]
    doc = Doc(en_vocab, words=words)
    for i, token in enumerate(doc):
        token.pos_ = pos[i]
    # usually this is already True when starting from proper models instead of blank English
    doc_bytes = doc.to_bytes()
    vocab = Vocab()
    vocab = vocab.from_bytes(vocab_bytes)
    doc = Doc(vocab).from_bytes(doc_bytes)
    actual = []
    for token in doc:
        actual.append(token.pos_)
    assert actual == pos


@pytest.mark.parametrize("text", ["rat"])
def test_serialize_vocab(en_vocab, text):
    text_hash = en_vocab.strings.add(text)
    vocab_bytes = en_vocab.to_bytes(exclude=["lookups"])
    new_vocab = Vocab().from_bytes(vocab_bytes)
    assert new_vocab.strings[text_hash] == text
    assert new_vocab.to_bytes(exclude=["lookups"]) == vocab_bytes


@pytest.mark.parametrize("strings1,strings2", test_strings)
def test_serialize_vocab_roundtrip_bytes(strings1, strings2):
    vocab1 = Vocab(strings=strings1)
    vocab2 = Vocab(strings=strings2)
    vocab1_b = vocab1.to_bytes()
    vocab2_b = vocab2.to_bytes()
    if strings1 == strings2:
        assert vocab1_b == vocab2_b
    else:
        assert vocab1_b != vocab2_b
    vocab1 = vocab1.from_bytes(vocab1_b)
    assert vocab1.to_bytes() == vocab1_b
    new_vocab1 = Vocab().from_bytes(vocab1_b)
    assert new_vocab1.to_bytes() == vocab1_b
    assert len(new_vocab1.strings) == len(strings1)
    assert sorted([s for s in new_vocab1.strings]) == sorted(strings1)


@pytest.mark.parametrize("strings1,strings2", test_strings)
def test_serialize_vocab_roundtrip_disk(strings1, strings2):
    vocab1 = Vocab(strings=strings1)
    vocab2 = Vocab(strings=strings2)
    with make_tempdir() as d:
        file_path1 = d / "vocab1"
        file_path2 = d / "vocab2"
        vocab1.to_disk(file_path1)
        vocab2.to_disk(file_path2)
        vocab1_d = Vocab().from_disk(file_path1)
        vocab2_d = Vocab().from_disk(file_path2)
        # check strings rather than lexemes, which are only reloaded on demand
        assert set(strings1) == set([s for s in vocab1_d.strings])
        assert set(strings2) == set([s for s in vocab2_d.strings])
        if set(strings1) == set(strings2):
            assert [s for s in vocab1_d.strings] == [s for s in vocab2_d.strings]
        else:
            assert [s for s in vocab1_d.strings] != [s for s in vocab2_d.strings]


@pytest.mark.parametrize("strings,lex_attr", test_strings_attrs)
def test_serialize_vocab_lex_attrs_bytes(strings, lex_attr):
    vocab1 = Vocab(strings=strings)
    vocab2 = Vocab()
    vocab1[strings[0]].norm_ = lex_attr
    assert vocab1[strings[0]].norm_ == lex_attr
    assert vocab2[strings[0]].norm_ != lex_attr
    vocab2 = vocab2.from_bytes(vocab1.to_bytes())
    assert vocab2[strings[0]].norm_ == lex_attr


@pytest.mark.parametrize("strings,lex_attr", test_strings_attrs)
def test_deserialize_vocab_seen_entries(strings, lex_attr):
    # Reported in #2153
    vocab = Vocab(strings=strings)
    vocab.from_bytes(vocab.to_bytes())
    assert len(vocab.strings) == len(strings)


@pytest.mark.parametrize("strings,lex_attr", test_strings_attrs)
def test_serialize_vocab_lex_attrs_disk(strings, lex_attr):
    vocab1 = Vocab(strings=strings)
    vocab2 = Vocab()
    vocab1[strings[0]].norm_ = lex_attr
    assert vocab1[strings[0]].norm_ == lex_attr
    assert vocab2[strings[0]].norm_ != lex_attr
    with make_tempdir() as d:
        file_path = d / "vocab"
        vocab1.to_disk(file_path)
        vocab2 = vocab2.from_disk(file_path)
    assert vocab2[strings[0]].norm_ == lex_attr


@pytest.mark.parametrize("strings1,strings2", test_strings)
def test_serialize_stringstore_roundtrip_bytes(strings1, strings2):
    sstore1 = StringStore(strings=strings1)
    sstore2 = StringStore(strings=strings2)
    sstore1_b = sstore1.to_bytes()
    sstore2_b = sstore2.to_bytes()
    if set(strings1) == set(strings2):
        assert sstore1_b == sstore2_b
    else:
        assert sstore1_b != sstore2_b
    sstore1 = sstore1.from_bytes(sstore1_b)
    assert sstore1.to_bytes() == sstore1_b
    new_sstore1 = StringStore().from_bytes(sstore1_b)
    assert new_sstore1.to_bytes() == sstore1_b
    assert set(new_sstore1) == set(strings1)


@pytest.mark.parametrize("strings1,strings2", test_strings)
def test_serialize_stringstore_roundtrip_disk(strings1, strings2):
    sstore1 = StringStore(strings=strings1)
    sstore2 = StringStore(strings=strings2)
    with make_tempdir() as d:
        file_path1 = d / "strings1"
        file_path2 = d / "strings2"
        sstore1.to_disk(file_path1)
        sstore2.to_disk(file_path2)
        sstore1_d = StringStore().from_disk(file_path1)
        sstore2_d = StringStore().from_disk(file_path2)
        assert set(sstore1_d) == set(sstore1)
        assert set(sstore2_d) == set(sstore2)
        if set(strings1) == set(strings2):
            assert set(sstore1_d) == set(sstore2_d)
        else:
            assert set(sstore1_d) != set(sstore2_d)


@pytest.mark.parametrize("strings,lex_attr", test_strings_attrs)
def test_pickle_vocab(strings, lex_attr):
    vocab = Vocab(strings=strings)
    ops = get_current_ops()
    vectors = Vectors(data=ops.xp.zeros((10, 10)), mode="floret", hash_count=1)
    vocab.vectors = vectors
    vocab[strings[0]].norm_ = lex_attr
    vocab_pickled = pickle.dumps(vocab)
    vocab_unpickled = pickle.loads(vocab_pickled)
    assert vocab.to_bytes() == vocab_unpickled.to_bytes()
    assert vocab_unpickled.vectors.mode == "floret"
