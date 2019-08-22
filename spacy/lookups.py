# coding: utf8
from __future__ import unicode_literals

from .util import SimpleFrozenDict


class Lookups(object):
    """Container for large lookup tables and dictionaries, e.g. lemmatization
    data or tokenizer exception lists. Lookups are available via vocab.lookups,
    so they can be accessed before the pipeline components are applied (e.g.
    in the tokenizer and lemmatizer), as well as within the pipeline components
    via doc.vocab.lookups.

    Important note: At the moment, this class only performs a very basic
    dictionary lookup. We're planning to replace this with a more efficient
    implementation. See #3971 for details.
    """

    def __init__(self):
        """Initialize the Lookups object.

        RETURNS (Lookups): The newly created object.
        """
        self._tables = {}

    def __contains__(self, name):
        """Check if the lookups contain a table of a given name. Delegates to
        Lookups.has_table.

        name (unicode): Name of the table.
        RETURNS (bool): Whether a table of that name exists.
        """
        return self.has_table(name)

    @property
    def tables(self):
        """RETURNS (list): Names of all tables in the lookups."""
        return list(self._tables.keys())

    def add_table(self, name, data=SimpleFrozenDict()):
        """Add a new table to the lookups. Raises an error if the table exists.

        name (unicode): Unique name of table.
        data (dict): Optional data to add to the table.
        RETURNS (Table): The newly added table.
        """
        if name in self.tables:
            raise ValueError("Table '{}' already exists".format(name))
        table = Table(name=name)
        table.update(data)
        self._tables[name] = table
        return table

    def get_table(self, name):
        """Get a table. Raises an error if the table doesn't exist.

        name (unicode): Name of the table.
        RETURNS (Table): The table.
        """
        if name not in self._tables:
            raise KeyError("Can't find table '{}'".format(name))
        return self._tables[name]

    def has_table(self, name):
        """Check if the lookups contain a table of a given name.

        name (unicode): Name of the table.
        RETURNS (bool): Whether a table of that name exists.
        """
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
    """A table in the lookups. Subclass of builtin dict that implements a
    slightly more consistent and unified API.
    """

    def __init__(self, name=None):
        """Initialize a new table.

        name (unicode): Optional table name for reference.
        RETURNS (Table): The newly created object.
        """
        self.name = name

    def set(self, key, value):
        """Set new key/value pair. Same as table[key] = value."""
        self[key] = value
