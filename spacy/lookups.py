# coding: utf8
from __future__ import unicode_literals

import srsly
from collections import OrderedDict

from .errors import Errors
from .util import SimpleFrozenDict, ensure_path


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
        self._tables = OrderedDict()

    def __contains__(self, name):
        """Check if the lookups contain a table of a given name. Delegates to
        Lookups.has_table.

        name (unicode): Name of the table.
        RETURNS (bool): Whether a table of that name exists.
        """
        return self.has_table(name)

    def __len__(self):
        """RETURNS (int): The number of tables in the lookups."""
        return len(self._tables)

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
            raise ValueError(Errors.E158.format(name=name))
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
            raise KeyError(Errors.E159.format(name=name, tables=self.tables))
        return self._tables[name]

    def remove_table(self, name):
        """Remove a table. Raises an error if the table doesn't exist.

        name (unicode): The name to remove.
        RETURNS (Table): The removed table.
        """
        if name not in self._tables:
            raise KeyError(Errors.E159.format(name=name, tables=self.tables))
        return self._tables.pop(name)

    def has_table(self, name):
        """Check if the lookups contain a table of a given name.

        name (unicode): Name of the table.
        RETURNS (bool): Whether a table of that name exists.
        """
        return name in self._tables

    def to_bytes(self, exclude=tuple(), **kwargs):
        """Serialize the lookups to a bytestring.

        exclude (list): String names of serialization fields to exclude.
        RETURNS (bytes): The serialized Lookups.
        """
        return srsly.msgpack_dumps(self._tables)

    def from_bytes(self, bytes_data, exclude=tuple(), **kwargs):
        """Load the lookups from a bytestring.

        exclude (list): String names of serialization fields to exclude.
        RETURNS (bytes): The loaded Lookups.
        """
        self._tables = OrderedDict()
        msg = srsly.msgpack_loads(bytes_data)
        for key, value in msg.items():
            self._tables[key] = Table.from_dict(value)
        return self

    def to_disk(self, path, **kwargs):
        """Save the lookups to a directory as lookups.bin.

        path (unicode / Path): The file path.
        """
        if len(self._tables):
            path = ensure_path(path)
            filepath = path / "lookups.bin"
            with filepath.open("wb") as file_:
                file_.write(self.to_bytes())

    def from_disk(self, path, **kwargs):
        """Load lookups from a directory containing a lookups.bin.

        path (unicode / Path): The file path.
        RETURNS (Lookups): The loaded lookups.
        """
        path = ensure_path(path)
        filepath = path / "lookups.bin"
        if filepath.exists():
            with filepath.open("rb") as file_:
                data = file_.read()
            return self.from_bytes(data)
        return self


class Table(OrderedDict):
    """A table in the lookups. Subclass of builtin dict that implements a
    slightly more consistent and unified API.
    """
    @classmethod
    def from_dict(cls, data, name=None):
        self = cls(name=name)
        self.update(data)
        return self

    def __init__(self, name=None):
        """Initialize a new table.

        name (unicode): Optional table name for reference.
        RETURNS (Table): The newly created object.
        """
        OrderedDict.__init__(self)
        self.name = name

    def set(self, key, value):
        """Set new key/value pair. Same as table[key] = value."""
        self[key] = value
