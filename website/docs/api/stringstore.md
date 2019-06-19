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
> stringstore = StringStore([u"apple", u"orange"])
> ```

| Name        | Type          | Description                                        |
| ----------- | ------------- | -------------------------------------------------- |
| `strings`   | iterable      | A sequence of unicode strings to add to the store. |
| **RETURNS** | `StringStore` | The newly constructed object.                      |

## StringStore.\_\_len\_\_ {#len tag="method"}

Get the number of strings in the store.

> #### Example
>
> ```python
> stringstore = StringStore([u"apple", u"orange"])
> assert len(stringstore) == 2
> ```

| Name        | Type | Description                         |
| ----------- | ---- | ----------------------------------- |
| **RETURNS** | int  | The number of strings in the store. |

## StringStore.\_\_getitem\_\_ {#getitem tag="method"}

Retrieve a string from a given hash, or vice versa.

> #### Example
>
> ```python
> stringstore = StringStore([u"apple", u"orange"])
> apple_hash = stringstore[u"apple"]
> assert apple_hash == 8566208034543834098
> assert stringstore[apple_hash] == u"apple"
> ```

| Name           | Type                     | Description                |
| -------------- | ------------------------ | -------------------------- |
| `string_or_id` | bytes, unicode or uint64 | The value to encode.       |
| **RETURNS**    | unicode or int           | The value to be retrieved. |

## StringStore.\_\_contains\_\_ {#contains tag="method"}

Check whether a string is in the store.

> #### Example
>
> ```python
> stringstore = StringStore([u"apple", u"orange"])
> assert u"apple" in stringstore
> assert not u"cherry" in stringstore
> ```

| Name        | Type    | Description                            |
| ----------- | ------- | -------------------------------------- |
| `string`    | unicode | The string to check.                   |
| **RETURNS** | bool    | Whether the store contains the string. |

## StringStore.\_\_iter\_\_ {#iter tag="method"}

Iterate over the strings in the store, in order. Note that a newly initialized
store will always include an empty string `''` at position `0`.

> #### Example
>
> ```python
> stringstore = StringStore([u"apple", u"orange"])
> all_strings = [s for s in stringstore]
> assert all_strings == [u"apple", u"orange"]
> ```

| Name       | Type    | Description            |
| ---------- | ------- | ---------------------- |
| **YIELDS** | unicode | A string in the store. |

## StringStore.add {#add tag="method" new="2"}

Add a string to the `StringStore`.

> #### Example
>
> ```python
> stringstore = StringStore([u"apple", u"orange"])
> banana_hash = stringstore.add(u"banana")
> assert len(stringstore) == 3
> assert banana_hash == 2525716904149915114
> assert stringstore[banana_hash] == u"banana"
> assert stringstore[u"banana"] == banana_hash
> ```

| Name        | Type    | Description              |
| ----------- | ------- | ------------------------ |
| `string`    | unicode | The string to add.       |
| **RETURNS** | uint64  | The string's hash value. |

## StringStore.to_disk {#to_disk tag="method" new="2"}

Save the current state to a directory.

> #### Example
>
> ```python
> stringstore.to_disk("/path/to/strings")
> ```

| Name   | Type             | Description                                                                                                           |
| ------ | ---------------- | --------------------------------------------------------------------------------------------------------------------- |
| `path` | unicode / `Path` | A path to a directory, which will be created if it doesn't exist. Paths may be either strings or `Path`-like objects. |

## StringStore.from_disk {#from_disk tag="method" new="2"}

Loads state from a directory. Modifies the object in place and returns it.

> #### Example
>
> ```python
> from spacy.strings import StringStore
> stringstore = StringStore().from_disk("/path/to/strings")
> ```

| Name        | Type             | Description                                                                |
| ----------- | ---------------- | -------------------------------------------------------------------------- |
| `path`      | unicode / `Path` | A path to a directory. Paths may be either strings or `Path`-like objects. |
| **RETURNS** | `StringStore`    | The modified `StringStore` object.                                         |

## StringStore.to_bytes {#to_bytes tag="method"}

Serialize the current state to a binary string.

> #### Example
>
> ```python
> store_bytes = stringstore.to_bytes()
> ```

| Name        | Type  | Description                                      |
| ----------- | ----- | ------------------------------------------------ |
| **RETURNS** | bytes | The serialized form of the `StringStore` object. |

## StringStore.from_bytes {#from_bytes tag="method"}

Load state from a binary string.

> #### Example
>
> ```python
> fron spacy.strings import StringStore
> store_bytes = stringstore.to_bytes()
> new_store = StringStore().from_bytes(store_bytes)
> ```

| Name         | Type          | Description               |
| ------------ | ------------- | ------------------------- |
| `bytes_data` | bytes         | The data to load from.    |
| **RETURNS**  | `StringStore` | The `StringStore` object. |

## Utilities {#util}

### strings.hash_string {#hash_string tag="function"}

Get a 64-bit hash for a given string.

> #### Example
>
> ```python
> from spacy.strings import hash_string
> assert hash_string(u"apple") == 8566208034543834098
> ```

| Name        | Type    | Description         |
| ----------- | ------- | ------------------- |
| `string`    | unicode | The string to hash. |
| **RETURNS** | uint64  | The hash.           |
