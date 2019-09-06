# coding: utf-8
from __future__ import unicode_literals

import pytest
from spacy.lookups import Lookups


def test_lookups_api():
    table_name = "test"
    data = {"foo": "bar", "hello": "world"}
    lookups = Lookups()
    lookups.add_table(table_name, data)
    assert table_name in lookups
    assert lookups.has_table(table_name)
    table = lookups.get_table(table_name)
    assert table.name == table_name
    assert len(table) == 2
    assert table.get("hello") == "world"
    table.set("a", "b")
    assert table.get("a") == "b"
    table = lookups.get_table(table_name)
    assert len(table) == 3
    with pytest.raises(KeyError):
        lookups.get_table("xyz")
    # with pytest.raises(ValueError):
    #     lookups.add_table(table_name)
