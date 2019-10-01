# coding: utf-8
from __future__ import unicode_literals

import srsly
from collections import OrderedDict
from preshed.bloom import BloomFilter

from .errors import Errors
from .util import SimpleFrozenDict, ensure_path
from .strings import get_string_id


UNSET = object()


class Lookups(object):
    """Container for large lookup tables and dictionaries, e.g. lemmatization
    data or tokenizer exception lists. Lookups are available via vocab.lookups,
    so they can be accessed before the pipeline components are applied (e.g.
    in the tokenizer and lemmatizer), as well as within the pipeline components
    via doc.vocab.lookups.
    """

    def __init__(self):
        """Initialize the Lookups object.

        RETURNS (Lookups): The newly created object.

        DOCS: https://spacy.io/api/lookups#init
        """
        self._tables = OrderedDict()

    def __contains__(self, name):
        """Check if the lookups contain a table of a given name. Delegates to
        Lookups.has_table.

        name (unicode): Name of the table.
        RETURNS (bool): Whether a table of that name is in the lookups.
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

        DOCS: https://spacy.io/api/lookups#add_table
        """
        if name in self.tables:
            raise ValueError(Errors.E158.format(name=name))
        table = Table(name=name, data=data)
        self._tables[name] = table
        return table

    def get_table(self, name, default=UNSET):
        """Get a table. Raises an error if the table doesn't exist and no
        default value is provided.

        name (unicode): Name of the table.
        default: Optional default value to return if table doesn't exist.
        RETURNS (Table): The table.

        DOCS: https://spacy.io/api/lookups#get_table
        """
        if name not in self._tables:
            if default == UNSET:
                raise KeyError(Errors.E159.format(name=name, tables=self.tables))
            return default
        return self._tables[name]

    def remove_table(self, name):
        """Remove a table. Raises an error if the table doesn't exist.

        name (unicode): Name of the table to remove.
        RETURNS (Table): The removed table.

        DOCS: https://spacy.io/api/lookups#remove_table
        """
        if name not in self._tables:
            raise KeyError(Errors.E159.format(name=name, tables=self.tables))
        return self._tables.pop(name)

    def has_table(self, name):
        """Check if the lookups contain a table of a given name.

        name (unicode): Name of the table.
        RETURNS (bool): Whether a table of that name exists.

        DOCS: https://spacy.io/api/lookups#has_table
        """
        return name in self._tables

    def to_bytes(self, **kwargs):
        """Serialize the lookups to a bytestring.

        RETURNS (bytes): The serialized Lookups.

        DOCS: https://spacy.io/api/lookups#to_bytes
        """
        return srsly.msgpack_dumps(self._tables)

    def from_bytes(self, bytes_data, **kwargs):
        """Load the lookups from a bytestring.

        bytes_data (bytes): The data to load.
        RETURNS (Lookups): The loaded Lookups.

        DOCS: https://spacy.io/api/lookups#from_bytes
        """
        self._tables = OrderedDict()
        for key, value in srsly.msgpack_loads(bytes_data).items():
            self._tables[key] = Table(key)
            self._tables[key].update(value)
        return self

    def to_disk(self, path, **kwargs):
        """Save the lookups to a directory as lookups.bin. Expects a path to a
        directory, which will be created if it doesn't exist.

        path (unicode / Path): The file path.

        DOCS: https://spacy.io/api/lookups#to_disk
        """
        if len(self._tables):
            path = ensure_path(path)
            if not path.exists():
                path.mkdir()
            filepath = path / "lookups.bin"
            with filepath.open("wb") as file_:
                file_.write(self.to_bytes())

    def from_disk(self, path, **kwargs):
        """Load lookups from a directory containing a lookups.bin. Will skip
        loading if the file doesn't exist.

        path (unicode / Path): The directory path.
        RETURNS (Lookups): The loaded lookups.

        DOCS: https://spacy.io/api/lookups#from_disk
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

    Includes a Bloom filter to speed up missed lookups.
    """

    @classmethod
    def from_dict(cls, data, name=None):
        """Initialize a new table from a dict.

        data (dict): The dictionary.
        name (unicode): Optional table name for reference.
        RETURNS (Table): The newly created object.

        DOCS: https://spacy.io/api/lookups#table.from_dict
        """
        self = cls(name=name)
        self.update(data)
        return self

    def __init__(self, name=None, data=None):
        """Initialize a new table.

        name (unicode): Optional table name for reference.
        data (dict): Initial data, used to hint Bloom Filter.
        RETURNS (Table): The newly created object.

        DOCS: https://spacy.io/api/lookups#table.init
        """
        OrderedDict.__init__(self)
        self.name = name
        # Assume a default size of 1M items
        self.default_size = 1e6
        size = len(data) if data and len(data) > 0 else self.default_size
        self.bloom = BloomFilter.from_error_rate(size)
        if data:
            self.update(data)

    def __setitem__(self, key, value):
        """Set new key/value pair. String keys will be hashed.

        key (unicode / int): The key to set.
        value: The value to set.
        """
        key = get_string_id(key)
        OrderedDict.__setitem__(self, key, value)
        self.bloom.add(key)

    def set(self, key, value):
        """Set new key/value pair. String keys will be hashed.
        Same as table[key] = value.

        key (unicode / int): The key to set.
        value: The value to set.
        """
        self[key] = value

    def __getitem__(self, key):
        """Get the value for a given key. String keys will be hashed.

        key (unicode / int): The key to get.
        RETURNS: The value.
        """
        key = get_string_id(key)
        return OrderedDict.__getitem__(self, key)

    def get(self, key, default=None):
        """Get the value for a given key. String keys will be hashed.

        key (unicode / int): The key to get.
        default: The default value to return.
        RETURNS: The value.
        """
        key = get_string_id(key)
        return OrderedDict.get(self, key, default)

    def __contains__(self, key):
        """Check whether a key is in the table. String keys will be hashed.

        key (unicode / int): The key to check.
        RETURNS (bool): Whether the key is in the table.
        """
        key = get_string_id(key)
        # This can give a false positive, so we need to check it after
        if key not in self.bloom:
            return False
        return OrderedDict.__contains__(self, key)

    def to_bytes(self):
        """Serialize table to a bytestring.

        RETURNS (bytes): The serialized table.

        DOCS: https://spacy.io/api/lookups#table.to_bytes
        """
        data = [
            ("name", self.name),
            ("dict", dict(self.items())),
            ("bloom", self.bloom.to_bytes()),
        ]
        return srsly.msgpack_dumps(OrderedDict(data))

    def from_bytes(self, bytes_data):
        """Load a table from a bytestring.

        bytes_data (bytes): The data to load.
        RETURNS (Table): The loaded table.

        DOCS: https://spacy.io/api/lookups#table.from_bytes
        """
        loaded = srsly.msgpack_loads(bytes_data)
        data = loaded.get("dict", {})
        self.name = loaded["name"]
        self.bloom = BloomFilter().from_bytes(loaded["bloom"])
        self.clear()
        self.update(data)
        return self
