# coding: utf8
from __future__ import unicode_literals

from .util import SimpleFrozenDict


class Lookups(object):
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
        raise NotImplementedError

    def from_bytes(self, bytes_data, exclude=tuple(), **kwargs):
        raise NotImplementedError

    def to_disk(self, path, exclude=tuple(), **kwargs):
        raise NotImplementedError

    def from_disk(self, path, exclude=tuple(), **kwargs):
        raise NotImplementedError


class Table(dict):
    def __init__(self, name=None):
        self.name = name

    def set(self, key, value):
        self[key] = value
