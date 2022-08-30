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
> spans = [doc[0:1], doc[1:3]]
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
> doc.spans["errors"] = [doc[0:1], doc[1:3]]
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
> doc.spans["errors"] = [doc[0:1], doc[1:3]]
> assert not doc.spans["errors"].has_overlap
> doc.spans["errors"].append(doc[2:4])
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
> doc.spans["errors"] = [doc[0:1], doc[1:3]]
> assert len(doc.spans["errors"]) == 2
> ```

| Name        | Description                               |
| ----------- | ----------------------------------------- |
| **RETURNS** | The number of spans in the group. ~~int~~ |

## SpanGroup.\_\_getitem\_\_ {#getitem tag="method"}

Get a span from the group. Note that a copy of the span is returned, so if any
changes are made to this span, they are not reflected in the corresponding
member of the span group. The item or group will need to be reassigned for
changes to be reflected in the span group.

> #### Example
>
> ```python
> doc = nlp("Their goi ng home")
> doc.spans["errors"] = [doc[0:1], doc[1:3]]
> span = doc.spans["errors"][1]
> assert span.text == "goi ng"
> span.label_ = 'LABEL'
> assert doc.spans["errors"][1].label_ != 'LABEL' # The span within the group was not updated
> ```

| Name        | Description                           |
| ----------- | ------------------------------------- |
| `i`         | The item index. ~~int~~               |
| **RETURNS** | The span at the given index. ~~Span~~ |

## SpanGroup.\_\_setitem\_\_ {#setitem tag="method", new="3.3"}

Set a span in the span group.

> #### Example
>
> ```python
> doc = nlp("Their goi ng home")
> doc.spans["errors"] = [doc[0:1], doc[1:3]]
> span = doc[0:2]
> doc.spans["errors"][0] = span
> assert doc.spans["errors"][0].text == "Their goi"
> ```

| Name   | Description             |
| ------ | ----------------------- |
| `i`    | The item index. ~~int~~ |
| `span` | The new value. ~~Span~~ |

## SpanGroup.\_\_delitem\_\_ {#delitem tag="method", new="3.3"}

Delete a span from the span group.

> #### Example
>
> ```python
> doc = nlp("Their goi ng home")
> doc.spans["errors"] = [doc[0:1], doc[1:3]]
> del doc.spans[0]
> assert len(doc.spans["errors"]) == 1
> ```

| Name | Description             |
| ---- | ----------------------- |
| `i`  | The item index. ~~int~~ |

## SpanGroup.\_\_add\_\_ {#add tag="method", new="3.3"}

Concatenate the current span group with another span group and return the result
in a new span group. Any `attrs` from the first span group will have precedence
over `attrs` in the second.

> #### Example
>
> ```python
> doc = nlp("Their goi ng home")
> doc.spans["errors"] = [doc[0:1], doc[1:3]]
> doc.spans["other"] = [doc[0:2], doc[2:4]]
> span_group = doc.spans["errors"] + doc.spans["other"]
> assert len(span_group) == 4
> ```

| Name        | Description                                                                  |
| ----------- | ---------------------------------------------------------------------------- |
| `other`     | The span group or spans to concatenate. ~~Union[SpanGroup, Iterable[Span]]~~ |
| **RETURNS** | The new span group. ~~SpanGroup~~                                            |

## SpanGroup.\_\_iadd\_\_ {#iadd tag="method", new="3.3"}

Append an iterable of spans or the content of a span group to the current span
group. Any `attrs` in the other span group will be added for keys that are not
already present in the current span group.

> #### Example
>
> ```python
> doc = nlp("Their goi ng home")
> doc.spans["errors"] = [doc[0:1], doc[1:3]]
> doc.spans["errors"] += [doc[3:4], doc[2:3]]
> assert len(doc.spans["errors"]) == 4
> ```

| Name        | Description                                                             |
| ----------- | ----------------------------------------------------------------------- |
| `other`     | The span group or spans to append. ~~Union[SpanGroup, Iterable[Span]]~~ |
| **RETURNS** | The span group. ~~SpanGroup~~                                           |

## SpanGroup.append {#append tag="method"}

Add a [`Span`](/api/span) object to the group. The span must refer to the same
[`Doc`](/api/doc) object as the span group.

> #### Example
>
> ```python
> doc = nlp("Their goi ng home")
> doc.spans["errors"] = [doc[0:1]]
> doc.spans["errors"].append(doc[1:3])
> assert len(doc.spans["errors"]) == 2
> ```

| Name   | Description                  |
| ------ | ---------------------------- |
| `span` | The span to append. ~~Span~~ |

## SpanGroup.extend {#extend tag="method"}

Add multiple [`Span`](/api/span) objects or contents of another `SpanGroup` to
the group. All spans must refer to the same [`Doc`](/api/doc) object as the span
group.

> #### Example
>
> ```python
> doc = nlp("Their goi ng home")
> doc.spans["errors"] = []
> doc.spans["errors"].extend([doc[1:3], doc[0:1]])
> assert len(doc.spans["errors"]) == 2
> span_group = SpanGroup(doc, spans=[doc[1:4], doc[0:3]])
> doc.spans["errors"].extend(span_group)
> ```

| Name    | Description                                              |
| ------- | -------------------------------------------------------- |
| `spans` | The spans to add. ~~Union[SpanGroup, Iterable["Span"]]~~ |

## SpanGroup.copy {#copy tag="method", new="3.3"}

Return a copy of the span group.

> #### Example
>
> ```python
> from spacy.tokens import SpanGroup
>
> doc = nlp("Their goi ng home")
> doc.spans["errors"] = [doc[1:3], doc[0:3]]
> new_group = doc.spans["errors"].copy()
> ```

| Name        | Description                                                                                        |
| ----------- | -------------------------------------------------------------------------------------------------- |
| `doc`       | The document to which the copy is bound. Defaults to `None` for the current doc. ~~Optional[Doc]~~ |
| **RETURNS** | A copy of the `SpanGroup` object. ~~SpanGroup~~                                                    |

## SpanGroup.to_bytes {#to_bytes tag="method"}

Serialize the span group to a bytestring.

> #### Example
>
> ```python
> doc = nlp("Their goi ng home")
> doc.spans["errors"] = [doc[0:1], doc[1:3]]
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
> doc.spans["errors"] = [doc[0:1], doc[1:3]]
> group_bytes = doc.spans["errors"].to_bytes()
> new_group = SpanGroup()
> new_group.from_bytes(group_bytes)
> ```

| Name         | Description                           |
| ------------ | ------------------------------------- |
| `bytes_data` | The data to load from. ~~bytes~~      |
| **RETURNS**  | The `SpanGroup` object. ~~SpanGroup~~ |
