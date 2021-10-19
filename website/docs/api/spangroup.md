---
title: SpanGroup
tag: class
source: spacy/tokens/span_group.pyx
new: 3
---

A group of arbitrary, potentially overlapping [`Span`](/api/span) objects that
all belong to the same [`Doc`](/api/doc) object. The group can be named, and you
can attach additional attributes to it. Span groups are generally accessed via
the [`Doc.spans`](/api/doc#spans) attribute, which will convert lists of spans
into a `SpanGroup` object for you automatically on assignment. `SpanGroup`
objects behave similar to `list`s, so you can append `Span` objects to them or
access a member at a given index.

## SpanGroup.\_\_init\_\_ {#init tag="method"}

Create a `SpanGroup`.

> #### Example
>
> ```python
> doc = nlp("Their goi ng home")
> spans = [doc[0:1], doc[2:4]]
>
> # Construction 1
> from spacy.tokens import SpanGroup
>
> group = SpanGroup(doc, name="errors", spans=spans, attrs={"annotator": "matt"})
> doc.spans["errors"] = group
>
> # Construction 2
> doc.spans["errors"] = spans
> assert isinstance(doc.spans["errors"], SpanGroup)
> ```

| Name           | Description                                                                                                                                          |
| -------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------- |
| `doc`          | The document the span group belongs to. ~~Doc~~                                                                                                      |
| _keyword-only_ |                                                                                                                                                      |
| `name`         | The name of the span group. If the span group is created automatically on assignment to `doc.spans`, the key name is used. Defaults to `""`. ~~str~~ |
| `attrs`        | Optional JSON-serializable attributes to attach to the span group. ~~Dict[str, Any]~~                                                                |
| `spans`        | The spans to add to the span group. ~~Iterable[Span]~~                                                                                               |

## SpanGroup.doc {#doc tag="property"}

The [`Doc`](/api/doc) object the span group is referring to.

<Infobox title="SpanGroup and Doc lifecycle" variant="warning">

When a `Doc` object is garbage collected, any related `SpanGroup` object won't
be functional anymore, as these objects use a `weakref` to refer to the
document. An error will be raised as the internal `doc` object will be `None`.
To avoid this, make sure that the original `Doc` objects are still available in
the scope of your function.

</Infobox>

> #### Example
>
> ```python
> doc = nlp("Their goi ng home")
> doc.spans["errors"] = [doc[0:1], doc[2:4]]
> assert doc.spans["errors"].doc == doc
> ```

| Name        | Description                     |
| ----------- | ------------------------------- |
| **RETURNS** | The reference document. ~~Doc~~ |

## SpanGroup.has_overlap {#has_overlap tag="property"}

Check whether the span group contains overlapping spans.

> #### Example
>
> ```python
> doc = nlp("Their goi ng home")
> doc.spans["errors"] = [doc[0:1], doc[2:4]]
> assert not doc.spans["errors"].has_overlap
> doc.spans["errors"].append(doc[1:2])
> assert doc.spans["errors"].has_overlap
> ```

| Name        | Description                                        |
| ----------- | -------------------------------------------------- |
| **RETURNS** | Whether the span group contains overlaps. ~~bool~~ |

## SpanGroup.\_\_len\_\_ {#len tag="method"}

Get the number of spans in the group.

> #### Example
>
> ```python
> doc = nlp("Their goi ng home")
> doc.spans["errors"] = [doc[0:1], doc[2:4]]
> assert len(doc.spans["errors"]) == 2
> ```

| Name        | Description                               |
| ----------- | ----------------------------------------- |
| **RETURNS** | The number of spans in the group. ~~int~~ |

## SpanGroup.\_\_getitem\_\_ {#getitem tag="method"}

Get a span from the group.

> #### Example
>
> ```python
> doc = nlp("Their goi ng home")
> doc.spans["errors"] = [doc[0:1], doc[2:4]]
> span = doc.spans["errors"][1]
> assert span.text == "goi ng"
> ```

| Name        | Description                           |
| ----------- | ------------------------------------- |
| `i`         | The item index. ~~int~~               |
| **RETURNS** | The span at the given index. ~~Span~~ |

## SpanGroup.append {#append tag="method"}

Add a [`Span`](/api/span) object to the group. The span must refer to the same
[`Doc`](/api/doc) object as the span group.

> #### Example
>
> ```python
> doc = nlp("Their goi ng home")
> doc.spans["errors"] = [doc[0:1]]
> doc.spans["errors"].append(doc[2:4])
> assert len(doc.spans["errors"]) == 2
> ```

| Name   | Description                  |
| ------ | ---------------------------- |
| `span` | The span to append. ~~Span~~ |

## SpanGroup.extend {#extend tag="method"}

Add multiple [`Span`](/api/span) objects to the group. All spans must refer to
the same [`Doc`](/api/doc) object as the span group.

> #### Example
>
> ```python
> doc = nlp("Their goi ng home")
> doc.spans["errors"] = []
> doc.spans["errors"].extend([doc[2:4], doc[0:1]])
> assert len(doc.spans["errors"]) == 2
> ```

| Name    | Description                          |
| ------- | ------------------------------------ |
| `spans` | The spans to add. ~~Iterable[Span]~~ |

## SpanGroup.to_bytes {#to_bytes tag="method"}

Serialize the span group to a bytestring.

> #### Example
>
> ```python
> doc = nlp("Their goi ng home")
> doc.spans["errors"] = [doc[0:1], doc[2:4]]
> group_bytes = doc.spans["errors"].to_bytes()
> ```

| Name        | Description                           |
| ----------- | ------------------------------------- |
| **RETURNS** | The serialized `SpanGroup`. ~~bytes~~ |

## SpanGroup.from_bytes {#from_bytes tag="method"}

Load the span group from a bytestring. Modifies the object in place and returns
it.

> #### Example
>
> ```python
> from spacy.tokens import SpanGroup
>
> doc = nlp("Their goi ng home")
> doc.spans["errors"] = [doc[0:1], doc[2:4]]
> group_bytes = doc.spans["errors"].to_bytes()
> new_group = SpanGroup()
> new_group.from_bytes(group_bytes)
> ```

| Name         | Description                           |
| ------------ | ------------------------------------- |
| `bytes_data` | The data to load from. ~~bytes~~      |
| **RETURNS**  | The `SpanGroup` object. ~~SpanGroup~~ |
