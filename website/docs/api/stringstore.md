---
title: StringStore
tag: class
source: spacy/strings.pyx
---

Look up strings by 64-bit hashes. As of v2.0, spaCy uses hash values instead of
integer IDs. This ensures that strings always map to the same ID, even from
different `StringStores`.

## StringStore.\_\_init\_\_ {#init tag="method"}

Create the `StringStore`.

> #### Example
>
> ```python
> from spacy.strings import StringStore
> stringstore = StringStore(["apple", "orange"])
> ```

| Name      | Description                                                            |
| --------- | ---------------------------------------------------------------------- |
| `strings` | A sequence of strings to add to the store. ~~Optional[Iterable[str]]~~ |

## StringStore.\_\_len\_\_ {#len tag="method"}

Get the number of strings in the store.

> #### Example
>
> ```python
> stringstore = StringStore(["apple", "orange"])
> assert len(stringstore) == 2
> ```

| Name        | Description                                 |
| ----------- | ------------------------------------------- |
| **RETURNS** | The number of strings in the store. ~~int~~ |

## StringStore.\_\_getitem\_\_ {#getitem tag="method"}

Retrieve a string from a given hash, or vice versa.

> #### Example
>
> ```python
> stringstore = StringStore(["apple", "orange"])
> apple_hash = stringstore["apple"]
> assert apple_hash == 8566208034543834098
> assert stringstore[apple_hash] == "apple"
> ```

| Name           | Description                                     |
| -------------- | ----------------------------------------------- |
| `string_or_id` | The value to encode. ~~Union[bytes, str, int]~~ |
| **RETURNS**    | The value to be retrieved. ~~Union[str, int]~~  |

## StringStore.\_\_contains\_\_ {#contains tag="method"}

Check whether a string is in the store.

> #### Example
>
> ```python
> stringstore = StringStore(["apple", "orange"])
> assert "apple" in stringstore
> assert not "cherry" in stringstore
> ```

| Name        | Description                                     |
| ----------- | ----------------------------------------------- |
| `string`    | The string to check. ~~str~~                    |
| **RETURNS** | Whether the store contains the string. ~~bool~~ |

## StringStore.\_\_iter\_\_ {#iter tag="method"}

Iterate over the strings in the store, in order. Note that a newly initialized
store will always include an empty string `""` at position `0`.

> #### Example
>
> ```python
> stringstore = StringStore(["apple", "orange"])
> all_strings = [s for s in stringstore]
> assert all_strings == ["apple", "orange"]
> ```

| Name       | Description                    |
| ---------- | ------------------------------ |
| **YIELDS** | A string in the store. ~~str~~ |

## StringStore.add {#add tag="method" new="2"}

Add a string to the `StringStore`.

> #### Example
>
> ```python
> stringstore = StringStore(["apple", "orange"])
> banana_hash = stringstore.add("banana")
> assert len(stringstore) == 3
> assert banana_hash == 2525716904149915114
> assert stringstore[banana_hash] == "banana"
> assert stringstore["banana"] == banana_hash
> ```

| Name        | Description                      |
| ----------- | -------------------------------- |
| `string`    | The string to add. ~~str~~       |
| **RETURNS** | The string's hash value. ~~int~~ |

## StringStore.to_disk {#to_disk tag="method" new="2"}

Save the current state to a directory.

> #### Example
>
> ```python
> stringstore.to_disk("/path/to/strings")
> ```

| Name   | Description                                                                                                                                |
| ------ | ------------------------------------------------------------------------------------------------------------------------------------------ |
| `path` | A path to a directory, which will be created if it doesn't exist. Paths may be either strings or `Path`-like objects. ~~Union[str, Path]~~ |

## StringStore.from_disk {#from_disk tag="method" new="2"}

Loads state from a directory. Modifies the object in place and returns it.

> #### Example
>
> ```python
> from spacy.strings import StringStore
> stringstore = StringStore().from_disk("/path/to/strings")
> ```

| Name        | Description                                                                                     |
| ----------- | ----------------------------------------------------------------------------------------------- |
| `path`      | A path to a directory. Paths may be either strings or `Path`-like objects. ~~Union[str, Path]~~ |
| **RETURNS** | The modified `StringStore` object. ~~StringStore~~                                              |

## StringStore.to_bytes {#to_bytes tag="method"}

Serialize the current state to a binary string.

> #### Example
>
> ```python
> store_bytes = stringstore.to_bytes()
> ```

| Name        | Description                                                |
| ----------- | ---------------------------------------------------------- |
| **RETURNS** | The serialized form of the `StringStore` object. ~~bytes~~ |

## StringStore.from_bytes {#from_bytes tag="method"}

Load state from a binary string.

> #### Example
>
> ```python
> fron spacy.strings import StringStore
> store_bytes = stringstore.to_bytes()
> new_store = StringStore().from_bytes(store_bytes)
> ```

| Name         | Description                               |
| ------------ | ----------------------------------------- |
| `bytes_data` | The data to load from. ~~bytes~~          |
| **RETURNS**  | The `StringStore` object. ~~StringStore~~ |

## Utilities {#util}

### strings.hash_string {#hash_string tag="function"}

Get a 64-bit hash for a given string.

> #### Example
>
> ```python
> from spacy.strings import hash_string
> assert hash_string("apple") == 8566208034543834098
> ```

| Name        | Description                 |
| ----------- | --------------------------- |
| `string`    | The string to hash. ~~str~~ |
| **RETURNS** | The hash. ~~int~~           |
