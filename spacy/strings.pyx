# cython: infer_types=True
# cython: profile=False
from typing import Iterable, Iterator, List, Optional, Tuple, Union

from libc.stdint cimport uint32_t
from libc.string cimport memcpy
from murmurhash.mrmr cimport hash64

import srsly

from .typedefs cimport hash_t

from . import util
from .errors import Errors
from .symbols import IDS as SYMBOLS_BY_STR
from .symbols import NAMES as SYMBOLS_BY_INT


cdef class StringStore:
    """Look up strings by 64-bit hashes. Implicitly handles reserved symbols.

    DOCS: https://spacy.io/api/stringstore
    """
    def __init__(self, strings: Optional[Iterable[str]] = None):
        """Create the StringStore.

        strings (iterable): A sequence of unicode strings to add to the store.
        """
        self.mem = Pool()
        self._map = PreshMap()
        if strings is not None:
            for string in strings:
                self.add(string)

    def __getitem__(self, string_or_hash: Union[str, int]) -> Union[str, int]:
        """Retrieve a string from a given hash. If a string
        is passed as the input, add it to the store and return
        its hash.

        string_or_hash (int / str): The hash value to lookup or the string to store.
        RETURNS (str / int): The stored string or the hash of the newly added string.
        """
        if isinstance(string_or_hash, str):
            return self.add(string_or_hash)
        else:
            return self._get_interned_str(string_or_hash)

    def __contains__(self, string_or_hash: Union[str, int]) -> bool:
        """Check whether a string or a hash is in the store.

        string (str / int): The string/hash to check.
        RETURNS (bool): Whether the store contains the string.
        """
        cdef hash_t str_hash = get_string_id(string_or_hash)
        if str_hash in SYMBOLS_BY_INT:
            return True
        else:
            return self._map.get(str_hash) is not NULL

    def __iter__(self) -> Iterator[str]:
        """Iterate over the strings in the store in insertion order.

        RETURNS: An iterable collection of strings.
        """
        return iter(self.keys())

    def __reduce__(self):
        strings = list(self)
        return (StringStore, (strings,), None, None, None)

    def __len__(self) -> int:
        """The number of strings in the store.

        RETURNS (int): The number of strings in the store.
        """
        return self._keys.size()

    def add(self, string: str) -> int:
        """Add a string to the StringStore.

        string (str): The string to add.
        RETURNS (uint64): The string's hash value.
        """
        if not isinstance(string, str):
            raise TypeError(Errors.E017.format(value_type=type(string)))

        if string in SYMBOLS_BY_STR:
            return SYMBOLS_BY_STR[string]
        else:
            return self._intern_str(string)

    def as_int(self, string_or_hash: Union[str, int]) -> str:
        """If a hash value is passed as the input, return it as-is. If the input
        is a string, return its corresponding hash.

        string_or_hash (str / int): The string to hash or a hash value.
        RETURNS (int): The hash of the string or the input hash value.
        """
        if isinstance(string_or_hash, int):
            return string_or_hash
        else:
            return get_string_id(string_or_hash)

    def as_string(self, string_or_hash: Union[str, int]) -> str:
        """If a string is passed as the input, return it as-is. If the input
        is a hash value, return its corresponding string.

        string_or_hash (str / int): The hash value to lookup or a string.
        RETURNS (str): The stored string or the input string.
        """
        if isinstance(string_or_hash, str):
            return string_or_hash
        else:
            return self._get_interned_str(string_or_hash)

    def items(self) -> List[Tuple[str, int]]:
        """Iterate over the stored strings and their hashes in insertion order.

        RETURNS: A list of string-hash pairs.
        """
        # Even though we internally store the hashes as keys and the strings as
        # values, we invert the order in the public API to keep it consistent with
        # the implementation of the `__iter__` method (where we wish to iterate over
        # the strings in the store).
        cdef int i
        pairs = [None] * self._keys.size()
        for i in range(self._keys.size()):
            str_hash = self._keys[i]
            utf8str = <Utf8Str*>self._map.get(str_hash)
            pairs[i] = (self._decode_str_repr(utf8str), str_hash)
        return pairs

    def keys(self) -> List[str]:
        """Iterate over the stored strings in insertion order.

        RETURNS: A list of strings.
        """
        cdef int i
        strings = [None] * self._keys.size()
        for i in range(self._keys.size()):
            utf8str = <Utf8Str*>self._map.get(self._keys[i])
            strings[i] = self._decode_str_repr(utf8str)
        return strings

    def values(self) -> List[int]:
        """Iterate over the stored strings hashes in insertion order.

        RETURNS: A list of string hashs.
        """
        cdef int i
        hashes = [None] * self._keys.size()
        for i in range(self._keys.size()):
            hashes[i] = self._keys[i]
        return hashes

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
            self.add(word)
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
            self.add(word)
        return self

    def _reset_and_load(self, strings):
        self.mem = Pool()
        self._map = PreshMap()
        self._keys.clear()
        for string in strings:
            self.add(string)

    def _get_interned_str(self, hash_value: int) -> str:
        cdef hash_t str_hash
        if not _try_coerce_to_hash(hash_value, &str_hash):
            raise TypeError(Errors.E4001.format(expected_types="'int'", received_type=type(hash_value)))

        # Handle reserved symbols and empty strings correctly.
        if str_hash == 0:
            return ""

        symbol = SYMBOLS_BY_INT.get(str_hash)
        if symbol is not None:
            return symbol

        utf8str = <Utf8Str*>self._map.get(str_hash)
        if utf8str is NULL:
            raise KeyError(Errors.E018.format(hash_value=str_hash))
        else:
            return self._decode_str_repr(utf8str)

    cdef hash_t _intern_str(self, str string):
        # TODO: This function's API/behaviour is an unholy mess...
        # 0 means missing, but we don't bother offsetting the index.
        chars = string.encode('utf-8')
        cdef hash_t key = hash64(<unsigned char*>chars, len(chars), 1)
        cdef Utf8Str* value = <Utf8Str*>self._map.get(key)
        if value is not NULL:
            return key

        value = self._allocate_str_repr(<unsigned char*>chars, len(chars))
        self._map.set(key, value)
        self._keys.push_back(key)
        return key

    cdef Utf8Str* _allocate_str_repr(self, const unsigned char* chars, uint32_t length) except *:
        cdef int n_length_bytes
        cdef int i
        cdef Utf8Str* string = <Utf8Str*>self.mem.alloc(1, sizeof(Utf8Str))
        if length < sizeof(string.s):
            string.s[0] = <unsigned char>length
            memcpy(&string.s[1], chars, length)
            return string
        elif length < 255:
            string.p = <unsigned char*>self.mem.alloc(length + 1, sizeof(unsigned char))
            string.p[0] = length
            memcpy(&string.p[1], chars, length)
            return string
        else:
            i = 0
            n_length_bytes = (length // 255) + 1
            string.p = <unsigned char*>self.mem.alloc(length + n_length_bytes, sizeof(unsigned char))
            for i in range(n_length_bytes-1):
                string.p[i] = 255
            string.p[n_length_bytes-1] = length % 255
            memcpy(&string.p[n_length_bytes], chars, length)
            return string

    cdef str _decode_str_repr(self, const Utf8Str* string):
        cdef int i, length
        if string.s[0] < sizeof(string.s) and string.s[0] != 0:
            return string.s[1:string.s[0]+1].decode('utf-8')
        elif string.p[0] < 255:
            return string.p[1:string.p[0]+1].decode('utf-8')
        else:
            i = 0
            length = 0
            while string.p[i] == 255:
                i += 1
                length += 255
            length += string.p[i]
            i += 1
            return string.p[i:length + i].decode('utf-8')


cpdef hash_t hash_string(object string) except -1:
    if not isinstance(string, str):
        raise TypeError(Errors.E4001.format(expected_types="'str'", received_type=type(string)))

    # Handle reserved symbols and empty strings correctly.
    if len(string) == 0:
        return 0

    symbol = SYMBOLS_BY_STR.get(string)
    if symbol is not None:
        return symbol

    chars = string.encode('utf-8')
    return hash64(<unsigned char*>chars, len(chars), 1)


cpdef hash_t get_string_id(object string_or_hash) except -1:
    cdef hash_t str_hash

    try:
        return hash_string(string_or_hash)
    except:   # no-cython-lint
        if _try_coerce_to_hash(string_or_hash, &str_hash):
            # Coerce the integral key to the expected primitive hash type.
            # This ensures that custom/overloaded "primitive" data types
            # such as those implemented by numpy are not inadvertently used
            # downsteam (as these are internally implemented as custom PyObjects
            # whose comparison operators can incur a significant overhead).
            return str_hash
        else:
            raise TypeError(Errors.E4001.format(expected_types="'str','int'", received_type=type(string_or_hash)))


# Not particularly elegant, but this is faster than `isinstance(key, numbers.Integral)`
cdef inline bint _try_coerce_to_hash(object key, hash_t* out_hash):
    try:
        out_hash[0] = key
        return True
    except:  # no-cython-lint
        return False
