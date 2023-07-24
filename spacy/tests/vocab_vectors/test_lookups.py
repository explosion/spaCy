import pytest

from spacy.lookups import Lookups, Table
from spacy.strings import get_string_id
from spacy.vocab import Vocab

from ..util import make_tempdir


def test_lookups_api():
    table_name = "test"
    data = {"foo": "bar", "hello": "world"}
    lookups = Lookups()
    lookups.add_table(table_name, data)
    assert len(lookups) == 1
    assert table_name in lookups
    assert lookups.has_table(table_name)
    table = lookups.get_table(table_name)
    assert table.name == table_name
    assert len(table) == 2
    assert table["hello"] == "world"
    table["a"] = "b"
    assert table["a"] == "b"
    table = lookups.get_table(table_name)
    assert len(table) == 3
    with pytest.raises(KeyError):
        lookups.get_table("xyz")
    with pytest.raises(ValueError):
        lookups.add_table(table_name)
    table = lookups.remove_table(table_name)
    assert table.name == table_name
    assert len(lookups) == 0
    assert table_name not in lookups
    with pytest.raises(KeyError):
        lookups.get_table(table_name)


def test_table_api():
    table = Table(name="table")
    assert table.name == "table"
    assert len(table) == 0
    assert "abc" not in table
    data = {"foo": "bar", "hello": "world"}
    table = Table(name="table", data=data)
    assert len(table) == len(data)
    assert "foo" in table
    assert get_string_id("foo") in table
    assert table["foo"] == "bar"
    assert table[get_string_id("foo")] == "bar"
    assert table.get("foo") == "bar"
    assert table.get("abc") is None
    table["abc"] = 123
    assert table["abc"] == 123
    assert table[get_string_id("abc")] == 123
    table.set("def", 456)
    assert table["def"] == 456
    assert table[get_string_id("def")] == 456


def test_table_api_to_from_bytes():
    data = {"foo": "bar", "hello": "world", "abc": 123}
    table = Table(name="table", data=data)
    table_bytes = table.to_bytes()
    new_table = Table().from_bytes(table_bytes)
    assert new_table.name == "table"
    assert len(new_table) == 3
    assert new_table["foo"] == "bar"
    assert new_table[get_string_id("foo")] == "bar"
    new_table2 = Table(data={"def": 456})
    new_table2.from_bytes(table_bytes)
    assert len(new_table2) == 3
    assert "def" not in new_table2


def test_lookups_to_from_bytes():
    lookups = Lookups()
    lookups.add_table("table1", {"foo": "bar", "hello": "world"})
    lookups.add_table("table2", {"a": 1, "b": 2, "c": 3})
    lookups_bytes = lookups.to_bytes()
    new_lookups = Lookups()
    new_lookups.from_bytes(lookups_bytes)
    assert len(new_lookups) == 2
    assert "table1" in new_lookups
    assert "table2" in new_lookups
    table1 = new_lookups.get_table("table1")
    assert len(table1) == 2
    assert table1["foo"] == "bar"
    table2 = new_lookups.get_table("table2")
    assert len(table2) == 3
    assert table2["b"] == 2
    assert new_lookups.to_bytes() == lookups_bytes


def test_lookups_to_from_disk():
    lookups = Lookups()
    lookups.add_table("table1", {"foo": "bar", "hello": "world"})
    lookups.add_table("table2", {"a": 1, "b": 2, "c": 3})
    with make_tempdir() as tmpdir:
        lookups.to_disk(tmpdir)
        new_lookups = Lookups()
        new_lookups.from_disk(tmpdir)
    assert len(new_lookups) == 2
    assert "table1" in new_lookups
    assert "table2" in new_lookups
    table1 = new_lookups.get_table("table1")
    assert len(table1) == 2
    assert table1["foo"] == "bar"
    table2 = new_lookups.get_table("table2")
    assert len(table2) == 3
    assert table2["b"] == 2


def test_lookups_to_from_bytes_via_vocab():
    table_name = "test"
    vocab = Vocab()
    vocab.lookups.add_table(table_name, {"foo": "bar", "hello": "world"})
    assert table_name in vocab.lookups
    vocab_bytes = vocab.to_bytes()
    new_vocab = Vocab()
    new_vocab.from_bytes(vocab_bytes)
    assert len(new_vocab.lookups) == len(vocab.lookups)
    assert table_name in new_vocab.lookups
    table = new_vocab.lookups.get_table(table_name)
    assert len(table) == 2
    assert table["hello"] == "world"
    assert new_vocab.to_bytes() == vocab_bytes


def test_lookups_to_from_disk_via_vocab():
    table_name = "test"
    vocab = Vocab()
    vocab.lookups.add_table(table_name, {"foo": "bar", "hello": "world"})
    assert table_name in vocab.lookups
    with make_tempdir() as tmpdir:
        vocab.to_disk(tmpdir)
        new_vocab = Vocab()
        new_vocab.from_disk(tmpdir)
    assert len(new_vocab.lookups) == len(vocab.lookups)
    assert table_name in new_vocab.lookups
    table = new_vocab.lookups.get_table(table_name)
    assert len(table) == 2
    assert table["hello"] == "world"
