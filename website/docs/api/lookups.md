---
title: Lookups
teaser: A container for large lookup tables and dictionaries
tag: class
source: spacy/lookups.py
new: 2.2
---

This class allows convenient accesss to large lookup tables and dictionaries,
e.g. lemmatization data or tokenizer exception lists. Lookups are available via
the [`Vocab`](/api/vocab) as `vocab.lookups`, so they can be accessed before the
pipeline components are applied (e.g. in the tokenizer and lemmatizer), as well
as within the pipeline components via `doc.vocab.lookups`.

## Lookups.\_\_init\_\_ {#init tag="method"}

Create a `Lookups` object.

> #### Example
>
> ```python
> from spacy.lookups import Lookups
> lookups = Lookups()
> ```

| Name        | Type      | Description                   |
| ----------- | --------- | ----------------------------- |
| **RETURNS** | `Lookups` | The newly constructed object. |

## Lookups.\_\_len\_\_ {#len tag="method"}

Get the current number of tables in the lookups.

> #### Example
>
> ```python
> lookups = Lookups()
> assert len(lookups) == 0
> ```

| Name        | Type | Description                          |
| ----------- | ---- | ------------------------------------ |
| **RETURNS** | int  | The number of tables in the lookups. |

## Lookups.\_\contains\_\_ {#contains tag="method"}

Check if the lookups contain a table of a given name. Delegates to
[`Lookups.has_table`](/api/lookups#has_table).

> #### Example
>
> ```python
> lookups = Lookups()
> lookups.add_table("some_table")
> assert "some_table" in lookups
> ```

| Name        | Type    | Description                                     |
| ----------- | ------- | ----------------------------------------------- |
| `name`      | unicode | Name of the table.                              |
| **RETURNS** | bool    | Whether a table of that name is in the lookups. |

## Lookups.tables {#tables tag="property"}

Get the names of all tables in the lookups.

> #### Example
>
> ```python
> lookups = Lookups()
> lookups.add_table("some_table")
> assert lookups.tables == ["some_table"]
> ```

| Name        | Type | Description                         |
| ----------- | ---- | ----------------------------------- |
| **RETURNS** | list | Names of the tables in the lookups. |

## Lookups.add_table {#add_table tag="method"}

Add a new table with optional data to the lookups. Raises an error if the table
exists.

> #### Example
>
> ```python
> lookups = Lookups()
> lookups.add_table("some_table", {"foo": "bar"})
> ```

| Name        | Type                          | Description                        |
| ----------- | ----------------------------- | ---------------------------------- |
| `name`      | unicode                       | Unique name of the table.          |
| `data`      | dict                          | Optional data to add to the table. |
| **RETURNS** | [`Table`](/api/lookups#table) | The newly added table.             |

## Lookups.get_table {#get_table tag="method"}

Get a table from the lookups. Raises an error if the table doesn't exist.

> #### Example
>
> ```python
> lookups = Lookups()
> lookups.add_table("some_table", {"foo": "bar"})
> table = lookups.get_table("some_table")
> assert table["foo"] == "bar"
> ```

| Name        | Type                          | Description        |
| ----------- | ----------------------------- | ------------------ |
| `name`      | unicode                       | Name of the table. |
| **RETURNS** | [`Table`](/api/lookups#table) | The table.         |

## Lookups.remove_table {#remove_table tag="method"}

Remove a table from the lookups. Raises an error if the table doesn't exist.

> #### Example
>
> ```python
> lookups = Lookups()
> lookups.add_table("some_table")
> removed_table = lookups.remove_table("some_table")
> assert "some_table" not in lookups
> ```

| Name        | Type                          | Description                  |
| ----------- | ----------------------------- | ---------------------------- |
| `name`      | unicode                       | Name of the table to remove. |
| **RETURNS** | [`Table`](/api/lookups#table) | The removed table.           |

## Lookups.has_table {#has_table tag="method"}

Check if the lookups contain a table of a given name. Equivalent to
[`Lookups.__contains__`](/api/lookups#contains).

> #### Example
>
> ```python
> lookups = Lookups()
> lookups.add_table("some_table")
> assert lookups.has_table("some_table")
> ```

| Name        | Type    | Description                                     |
| ----------- | ------- | ----------------------------------------------- |
| `name`      | unicode | Name of the table.                              |
| **RETURNS** | bool    | Whether a table of that name is in the lookups. |

## Lookups.to_bytes {#to_bytes tag="method"}

Serialize the lookups to a bytestring.

> #### Example
>
> ```python
> lookup_bytes = lookups.to_bytes()
> ```

| Name        | Type  | Description             |
| ----------- | ----- | ----------------------- |
| **RETURNS** | bytes | The serialized lookups. |

## Lookups.from_bytes {#from_bytes tag="method"}

Load the lookups from a bytestring.

> #### Example
>
> ```python
> lookup_bytes = lookups.to_bytes()
> lookups = Lookups()
> lookups.from_bytes(lookup_bytes)
> ```

| Name         | Type      | Description            |
| ------------ | --------- | ---------------------- |
| `bytes_data` | bytes     | The data to load from. |
| **RETURNS**  | `Lookups` | The loaded lookups.    |

## Lookups.to_disk {#to_disk tag="method"}

Save the lookups to a directory as `lookups.bin`. Expects a path to a directory,
which will be created if it doesn't exist.

> #### Example
>
> ```python
> lookups.to_disk("/path/to/lookups")
> ```

| Name   | Type             | Description                                                                                                           |
| ------ | ---------------- | --------------------------------------------------------------------------------------------------------------------- |
| `path` | unicode / `Path` | A path to a directory, which will be created if it doesn't exist. Paths may be either strings or `Path`-like objects. |

## Lookups.from_disk {#from_disk tag="method"}

Load lookups from a directory containing a `lookups.bin`. Will skip loading if
the file doesn't exist.

> #### Example
>
> ```python
> from spacy.lookups import Lookups
> lookups = Lookups()
> lookups.from_disk("/path/to/lookups")
> ```

| Name        | Type             | Description                                                                |
| ----------- | ---------------- | -------------------------------------------------------------------------- |
| `path`      | unicode / `Path` | A path to a directory. Paths may be either strings or `Path`-like objects. |
| **RETURNS** | `Lookups`        | The loaded lookups.                                                        |

## Table {#table tag="class, ordererddict"}

A table in the lookups. Subclass of `OrderedDict` that implements a slightly
more consistent and unified API. Supports all other methods and attributes of
`OrderedDict` / `dict`, and the customized methods listed here.

### Table.\_\_init\_\_ {#table.init tag="method"}

Initialize a new table.

> #### Example
>
> ```python
> from spacy.lookups import Table
> table = Table(name="some_table")
> ```

| Name        | Type    | Description                        |
| ----------- | ------- | ---------------------------------- |
| `name`      | unicode | Optional table name for reference. |
| **RETURNS** | `Table` | The newly constructed object.      |

### Table.from_dict {#table.from_dict tag="classmethod"}

Initialize a new table from a dict.

> #### Example
>
> ```python
> from spacy.lookups import Table
> data = {"foo": "bar", "baz": 100}
> table = Table.from_dict(data, name="some_table")
> ```

| Name        | Type    | Description                        |
| ----------- | ------- | ---------------------------------- |
| `data`      | dict    | The dictionary.                    |
| `name`      | unicode | Optional table name for reference. |
| **RETURNS** | `Table` | The newly constructed object.      |

### Table.set {#table.set tag="key"}

Set a new key / value pair. Same as `table[key] = value`.

> #### Example
>
> ```python
> from spacy.lookups import Table
> table = Table()
> table.set("foo", "bar")
> assert table["foo"] == "bar"
> ```

| Name    | Type    | Description |
| ------- | ------- | ----------- |
| `key`   | unicode | The key.    |
| `value` | -       | The value.  |
