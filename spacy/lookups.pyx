# coding: utf-8
from __future__ import unicode_literals

from libc.stdint cimport uint64_t

from .util import SimpleFrozenDict

from . import util

import srsly
from preshed.bloom import BloomFilter

cdef class Lookups(object):
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

    def add_table(self, str name, data=SimpleFrozenDict()):
        if name in self.tables:
            raise ValueError("Table '{}' already exists".format(name))
        table = Table(name=name, data=data)
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
            ( (key, val.to_bytes) for key, val in self._tables.items() )
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

cdef class Table(dict):
    """A dict with a bloom filter to check for misses.

    The main use case for this is checking for specific terms, so the miss rate
    will be high. Since bloom filter access is fast and gives no false
    negatives this should be faster than just using a dict."""

    def __init__(self, str name, data=None):
        self.name = name
        # assume a default size of 1M items
        datacount = 1E6
        if data:
            datacount = len(data)
        self.bloom = BloomFilter.from_error_rate(len(data))
        self.update(data)

    def set(self, uint64_t key, value):
        self[key] = value
        self.bloom.add(key)

    def update(self, data):
        for key, val in data.items():
            self.set(key, val)

    def __contains__(self, uint64_t key):
        # This can give a false positive, so we need to check it after
        if key not in self.bloom: 
            return False
        return self[key]

    def to_bytes(self):
        # TODO: serialize bloom too. For now just reconstruct it.
        return srsly.msgpack_dumps({'name': self.name, 'dict': dict(self)})

    def from_bytes(self, bytes data):
        loaded = srsly.msgpack_loads(data)
        self.name = loaded['name']
        for key, val in loaded['dict'].items():
            self[key] = val
            self.bloom.add(key)

        return self

