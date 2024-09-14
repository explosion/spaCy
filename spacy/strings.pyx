# cython: infer_types=True
# cython: profile=False
cimport cython

from contextlib import contextmanager
from typing import List, Optional

from libc.stdint cimport uint32_t
from libc.string cimport memcpy
from murmurhash.mrmr cimport hash32, hash64
from preshed.maps cimport map_clear

import srsly

from .typedefs cimport hash_t

from . import util
from .errors import Errors
from .symbols import IDS as SYMBOLS_BY_STR
from .symbols import NAMES as SYMBOLS_BY_INT


# Not particularly elegant, but this is faster than `isinstance(key, numbers.Integral)`
cdef inline bint _try_coerce_to_hash(object key, hash_t* out_hash):
    try:
        out_hash[0] = key
        return True
    except:  # no-cython-lint
        return False


def get_string_id(key):
    """Get a string ID, handling the reserved symbols correctly. If the key is
    already an ID, return it.

    This function optimises for convenience over performance, so shouldn't be
    used in tight loops.
    """
    cdef hash_t str_hash
    if isinstance(key, str):
        if len(key) == 0:
            return 0

        symbol = SYMBOLS_BY_STR.get(key, None)
        if symbol is not None:
            return symbol
        else:
            chars = key.encode("utf8")
            return hash_utf8(chars, len(chars))
    elif _try_coerce_to_hash(key, &str_hash):
        # Coerce the integral key to the expected primitive hash type.
        # This ensures that custom/overloaded "primitive" data types
        # such as those implemented by numpy are not inadvertently used
        # downsteam (as these are internally implemented as custom PyObjects
        # whose comparison operators can incur a significant overhead).
        return str_hash
    else:
        # TODO: Raise an error instead
        return key


cpdef hash_t hash_string(str string) except 0:
    chars = string.encode("utf8")
    return hash_utf8(chars, len(chars))


cdef hash_t hash_utf8(char* utf8_string, int length) nogil:
    return hash64(utf8_string, length, 1)


cdef uint32_t hash32_utf8(char* utf8_string, int length) nogil:
    return hash32(utf8_string, length, 1)


cdef str decode_Utf8Str(const Utf8Str* string):
    cdef int i, length
    if string.s[0] < sizeof(string.s) and string.s[0] != 0:
        return string.s[1:string.s[0]+1].decode("utf8")
    elif string.p[0] < 255:
        return string.p[1:string.p[0]+1].decode("utf8")
    else:
        i = 0
        length = 0
        while string.p[i] == 255:
            i += 1
            length += 255
        length += string.p[i]
        i += 1
        return string.p[i:length + i].decode("utf8")


cdef Utf8Str* _allocate(Pool mem, const unsigned char* chars, uint32_t length) except *:
    cdef int n_length_bytes
    cdef int i
    cdef Utf8Str* string = <Utf8Str*>mem.alloc(1, sizeof(Utf8Str))
    if length < sizeof(string.s):
        string.s[0] = <unsigned char>length
        memcpy(&string.s[1], chars, length)
        return string
    elif length < 255:
        string.p = <unsigned char*>mem.alloc(length + 1, sizeof(unsigned char))
        string.p[0] = length
        memcpy(&string.p[1], chars, length)
        return string
    else:
        i = 0
        n_length_bytes = (length // 255) + 1
        string.p = <unsigned char*>mem.alloc(length + n_length_bytes, sizeof(unsigned char))
        for i in range(n_length_bytes-1):
            string.p[i] = 255
        string.p[n_length_bytes-1] = length % 255
        memcpy(&string.p[n_length_bytes], chars, length)
        return string


cdef class StringStore:
    """Look up strings by 64-bit hashes.

    DOCS: https://spacy.io/api/stringstore
    """
    def __init__(self, strings=None, freeze=False):
        """Create the StringStore.

        strings (iterable): A sequence of unicode strings to add to the store.
        """
        self.mem = Pool()
        self._non_temp_mem = self.mem
        self._map = PreshMap()
        if strings is not None:
            for string in strings:
                self.add(string, allow_transient=False)

    def __getitem__(self, object string_or_id):
        """Retrieve a string from a given hash, or vice versa.

        string_or_id (bytes, str or uint64): The value to encode.
        Returns (str / uint64): The value to be retrieved.
        """
        cdef hash_t str_hash
        cdef Utf8Str* utf8str = NULL

        if isinstance(string_or_id, str):
            if len(string_or_id) == 0:
                return 0

            # Return early if the string is found in the symbols LUT.
            symbol = SYMBOLS_BY_STR.get(string_or_id, None)
            if symbol is not None:
                return symbol
            else:
                return hash_string(string_or_id)
        elif isinstance(string_or_id, bytes):
            return hash_utf8(string_or_id, len(string_or_id))
        elif _try_coerce_to_hash(string_or_id, &str_hash):
            if str_hash == 0:
                return ""
            elif str_hash < len(SYMBOLS_BY_INT):
                return SYMBOLS_BY_INT[str_hash]
            else:
                utf8str = <Utf8Str*>self._map.get(str_hash)
                if utf8str is NULL:
                    raise KeyError(Errors.E018.format(hash_value=string_or_id))
                else:
                    return decode_Utf8Str(utf8str)
        else:
            # TODO: Raise an error instead
            utf8str = <Utf8Str*>self._map.get(string_or_id)
            if utf8str is NULL:
                raise KeyError(Errors.E018.format(hash_value=string_or_id))
            else:
                return decode_Utf8Str(utf8str)

    def as_int(self, key):
        """If key is an int, return it; otherwise, get the int value."""
        if not isinstance(key, str):
            return key
        else:
            return self[key]

    def as_string(self, key):
        """If key is a string, return it; otherwise, get the string value."""
        if isinstance(key, str):
            return key
        else:
            return self[key]

    def __len__(self) -> int:
        """The number of strings in the store.

        RETURNS (int): The number of strings in the store.
        """
        return self.keys.size() + self._transient_keys.size()

    @contextmanager
    def memory_zone(self, mem: Optional[Pool] = None) -> Pool:
        """Begin a block where all resources allocated during the block will
        be freed at the end of it. If a resources was created within the
        memory zone block, accessing it outside the block is invalid.
        Behaviour of this invalid access is undefined. Memory zones should
        not be nested.

        The memory zone is helpful for services that need to process large
        volumes of text with a defined memory budget.
        """
        if mem is None:
            mem = Pool()
        self.mem = mem
        yield mem
        for key in self._transient_keys:
            map_clear(self._map.c_map, key)
        self._transient_keys.clear()
        self.mem = self._non_temp_mem

    def add(self, string: str, allow_transient: Optional[bool] = None) -> int:
        """Add a string to the StringStore.

        string (str): The string to add.
        allow_transient (bool): Allow the string to be stored in the 'transient'
          map, which will be flushed at the end of the memory zone. Strings
          encountered during arbitrary text processing should be added
          with allow_transient=True, while labels and other strings used
          internally should not.
        RETURNS (uint64): The string's hash value.
        """
        if allow_transient is None:
            allow_transient = self.mem is not self._non_temp_mem
        cdef hash_t str_hash
        if isinstance(string, str):
            if string in SYMBOLS_BY_STR:
                return SYMBOLS_BY_STR[string]

            string = string.encode("utf8")
            str_hash = hash_utf8(string, len(string))
            self._intern_utf8(string, len(string), &str_hash, allow_transient)
        elif isinstance(string, bytes):
            if string in SYMBOLS_BY_STR:
                return SYMBOLS_BY_STR[string]
            str_hash = hash_utf8(string, len(string))
            self._intern_utf8(string, len(string), &str_hash, allow_transient)
        else:
            raise TypeError(Errors.E017.format(value_type=type(string)))
        return str_hash

    def __len__(self):
        """The number of strings in the store.
        if string in SYMBOLS_BY_STR:
            return SYMBOLS_BY_STR[string]
        else:
            return self._intern_str(string, allow_transient)

        RETURNS (int): The number of strings in the store.
        """
        return self.keys.size() + self._transient_keys.size()

    def __contains__(self, string_or_id not None):
        """Check whether a string or ID is in the store.

        string_or_id (str or int): The string to check.
        RETURNS (bool): Whether the store contains the string.
        """
        cdef hash_t str_hash
        if isinstance(string_or_id, str):
            if len(string_or_id) == 0:
                return True
            elif string_or_id in SYMBOLS_BY_STR:
                return True
            str_hash = hash_string(string_or_id)
        elif _try_coerce_to_hash(string_or_id, &str_hash):
            pass
        else:
            # TODO: Raise an error instead
            if self._map.get(string_or_id) is not NULL:
                return True
            else:
                return False
        if str_hash < len(SYMBOLS_BY_INT):
            return True
        else:
            if self._map.get(str_hash) is not NULL:
                return True
            else:
                return False

    def __iter__(self):
        """Iterate over the strings in the store, in order.

        YIELDS (str): A string in the store.
        """
        cdef int i
        cdef hash_t key
        for i in range(self.keys.size()):
            key = self.keys[i]
            utf8str = <Utf8Str*>self._map.get(key)
            yield decode_Utf8Str(utf8str)
        for i in range(self._transient_keys.size()):
            key = self._transient_keys[i]
            utf8str = <Utf8Str*>self._map.get(key)
            yield decode_Utf8Str(utf8str)

    def __reduce__(self):
        strings = list(self)
        return (StringStore, (strings,), None, None, None)

    def values(self) -> List[int]:
        """Iterate over the stored strings hashes in insertion order.

        RETURNS: A list of string hashs.
        """
        cdef int i
        hashes = [None] * self._keys.size()
        for i in range(self._keys.size()):
            hashes[i] = self._keys[i]
        transient_hashes = [None] * self._transient_keys.size()
        for i in range(self._transient_keys.size()):
            transient_hashes[i] = self._transient_keys[i]
        return hashes + transient_hashes

    def to_disk(self, path):
        """Save the current state to a directory.

        path (str / Path): A path to a directory, which will be created if
            it doesn't exist. Paths may be either strings or Path-like objects.
        """
        path = util.ensure_path(path)
        strings = sorted(self)
        srsly.write_json(path, strings)

    def from_disk(self, path):
        """Loads state from a directory. Modifies the object in place and
        returns it.

        path (str / Path): A path to a directory. Paths may be either
            strings or `Path`-like objects.
        RETURNS (StringStore): The modified `StringStore` object.
        """
        path = util.ensure_path(path)
        strings = srsly.read_json(path)
        prev = list(self)
        self._reset_and_load(strings)
        for word in prev:
            self.add(word, allow_transient=False)
        return self

    def to_bytes(self, **kwargs):
        """Serialize the current state to a binary string.

        RETURNS (bytes): The serialized form of the `StringStore` object.
        """
        return srsly.json_dumps(sorted(self))

    def from_bytes(self, bytes_data, **kwargs):
        """Load state from a binary string.

        bytes_data (bytes): The data to load from.
        RETURNS (StringStore): The `StringStore` object.
        """
        strings = srsly.json_loads(bytes_data)
        prev = list(self)
        self._reset_and_load(strings)
        for word in prev:
            self.add(word, allow_transient=False)
        return self

    def _reset_and_load(self, strings):
        self.mem = Pool()
        self._non_temp_mem = self.mem
        self._map = PreshMap()
        self.keys.clear()
        self._transient_keys.clear()
        for string in strings:
            self.add(string, allow_transient=False)

    cdef const Utf8Str* intern_unicode(self, str py_string, bint allow_transient):
        # 0 means missing, but we don't bother offsetting the index.
        cdef bytes byte_string = py_string.encode("utf8")
        return self._intern_utf8(byte_string, len(byte_string), NULL, allow_transient)

    @cython.final
    cdef const Utf8Str* _intern_utf8(self, char* utf8_string, int length, hash_t* precalculated_hash, bint allow_transient):
        # TODO: This function's API/behaviour is an unholy mess...
        # 0 means missing, but we don't bother offsetting the index.
        cdef hash_t key = precalculated_hash[0] if precalculated_hash is not NULL else hash_utf8(utf8_string, length)
        cdef Utf8Str* value = <Utf8Str*>self._map.get(key)
        if value is not NULL:
            return value
        value = _allocate(self.mem, <unsigned char*>utf8_string, length)
        self._map.set(key, value)
        if allow_transient and self.mem is not self._non_temp_mem:
            self._transient_keys.push_back(key)
        else:
            self.keys.push_back(key)
        return value
