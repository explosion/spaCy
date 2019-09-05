# coding: utf8
from __future__ import unicode_literals

from .util import SimpleFrozenDict

from . import util

import srsly
from preshed.bloom import BloomFilter

class Lookups(object):
    """Lookup tables for language data such as lemmas.

    This is a thin wrapper around a dictionary of names to Tables, where a
    Table is itself just a dictionary with a bloom filter for faster miss
    handling.
    """
    def __init__(self):
        self._tables = {}

    def __contains__(self, name):
        return self.has_table(name)

    @property
    def tables(self):
        return list(self._tables.keys())

    def add_table(self, name, data=SimpleFrozenDict()):
        if name in self.tables:
            raise ValueError("Table '{}' already exists".format(name))
        table = Table(name=name)
        table.update(data)
        self._tables[name] = table
        return table

    def get_table(self, name):
        if name not in self._tables:
            raise KeyError("Can't find table '{}'".format(name))
        return self._tables[name]

    def has_table(self, name):
        return name in self._tables

    def to_bytes(self, exclude=tuple(), **kwargs):
        serializers = dict(
            ( (tt.name, tt.to_bytes) for tt in self._tables.values() )
        )
            
        return util.to_bytes(serializers, [])

    def from_bytes(self, bytes_data, exclude=tuple(), **kwargs):
        msg = srsly.msgpack_loads(bytes_data)
        for name, val in msg.items():
            table = Table(name=name)
            table.from_bytes(val)
            self._tables[name] = table
        return self

    def to_disk(self, path, exclude=tuple(), **kwargs):
        path = util.ensure_path(path)

        with path.open('wb') as file_:
            file_.write(self.to_bytes())

    def from_disk(self, path, exclude=tuple(), **kwargs):
        path = util.ensure_path(path)
        with path.open('rb') as file_:
            self.from_bytes(file_.read())
        return self

class Table(object):
    """A dict with a bloom filter to check for misses.

    The main use case for this is checking for specific terms, so the miss rate
    will be high. Since bloom filter access is fast and gives no false
    negatives this should be faster than just using a dict."""

    def __init__(self, name=None):
        self.name = name
        self.bloom = BloomFilter()
        self.dict = dict()

    def set(self, key, value):
        self.dict[key] = value
        self.bloom.add(key)

    def update(self, data):
        for key, val in data.items():
            self.set(key, val)

    def __getitem__(self, key):
        return self.dict[key]

    def __contains__(self, key):
        # This can give a false positive, so we need to check it after
        if key not in self.bloom: 
            return False
        return key in self.dict

    def to_bytes(self):
        # TODO: serialize bloom too. For now just reconstruct it.
        return srsly.msgpack_dumps({'name': self.name, 'dict': self.dict})

    def from_bytes(self, data):
        loaded = srsly.msgpack_loads(data)
        self.name = loaded['name']
        self.dict = loaded['dict']
        for key, val in self.dict.items():
            self.bloom.add(key)

        return self

