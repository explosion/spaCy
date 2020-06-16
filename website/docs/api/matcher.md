---
title: Matcher
teaser: Match sequences of tokens, based on pattern rules
tag: class
source: spacy/matcher/matcher.pyx
---

<Infobox title="Changed in v2.0" variant="warning">

As of spaCy 2.0, `Matcher.add_pattern` and `Matcher.add_entity` are deprecated
and have been replaced with a simpler [`Matcher.add`](/api/matcher#add) that
lets you add a list of patterns and a callback for a given match ID.
`Matcher.get_entity` is now called [`matcher.get`](/api/matcher#get).
`Matcher.load` (not useful, as it didn't allow specifying callbacks), and
`Matcher.has_entity` (now redundant) have been removed. The concept of "acceptor
functions" has also been retired – this logic can now be handled in the callback
functions.

</Infobox>

## Matcher.\_\_init\_\_ {#init tag="method"}

Create the rule-based `Matcher`. If `validate=True` is set, all patterns added
to the matcher will be validated against a JSON schema and a `MatchPatternError`
is raised if problems are found. Those can include incorrect types (e.g. a
string where an integer is expected) or unexpected property names.

> #### Example
>
> ```python
> from spacy.matcher import Matcher
> matcher = Matcher(nlp.vocab)
> ```

| Name                                    | Type      | Description                                                                                 |
| --------------------------------------- | --------- | ------------------------------------------------------------------------------------------- |
| `vocab`                                 | `Vocab`   | The vocabulary object, which must be shared with the documents the matcher will operate on. |
| `validate` <Tag variant="new">2.1</Tag> | bool      | Validate all patterns added to this matcher.                                                |
| **RETURNS**                             | `Matcher` | The newly constructed object.                                                               |

## Matcher.\_\_call\_\_ {#call tag="method"}

Find all token sequences matching the supplied patterns on the `Doc`. As of
spaCy v2.3, the `Matcher` can also be called on `Span` objects.

> #### Example
>
> ```python
> from spacy.matcher import Matcher
>
> matcher = Matcher(nlp.vocab)
> pattern = [{"LOWER": "hello"}, {"LOWER": "world"}]
> matcher.add("HelloWorld", None, pattern)
> doc = nlp("hello world!")
> matches = matcher(doc)
> ```

| Name        | Type         | Description                                                                                                                                                              |
| ----------- | ------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `doclike`   | `Doc`/`Span` | The document to match over or a `Span` (as of v2.3).                                                                                                                     |
| **RETURNS** | list         | A list of `(match_id, start, end)` tuples, describing the matches. A match tuple describes a span `doc[start:end`]. The `match_id` is the ID of the added match pattern. |

<Infobox title="Important note" variant="warning">

By default, the matcher **does not perform any action** on matches, like tagging
matched phrases with entity types. Instead, actions need to be specified when
**adding patterns or entities**, by passing in a callback function as the
`on_match` argument on [`add`](/api/matcher#add). This allows you to define
custom actions per pattern within the same matcher. For example, you might only
want to merge some entity types, and set custom flags for other matched
patterns. For more details and examples, see the usage guide on
[rule-based matching](/usage/rule-based-matching).

</Infobox>

## Matcher.pipe {#pipe tag="method"}

Match a stream of documents, yielding them in turn.

> #### Example
>
> ```python
> from spacy.matcher import Matcher
> matcher = Matcher(nlp.vocab)
> for doc in matcher.pipe(docs, batch_size=50):
>     pass
> ```

| Name                                          | Type     | Description                                                                                                                                                                                                                |
| --------------------------------------------- | -------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `docs`                                        | iterable | A stream of documents.                                                                                                                                                                                                     |
| `batch_size`                                  | int      | The number of documents to accumulate into a working set.                                                                                                                                                                  |
| `return_matches` <Tag variant="new">2.1</Tag> | bool     | Yield the match lists along with the docs, making results `(doc, matches)` tuples.                                                                                                                                         |
| `as_tuples`                                   | bool     | Interpret the input stream as `(doc, context)` tuples, and yield `(result, context)` tuples out. If both `return_matches` and `as_tuples` are `True`, the output will be a sequence of `((doc, matches), context)` tuples. |
| **YIELDS**                                    | `Doc`    | Documents, in order.                                                                                                                                                                                                       |

## Matcher.\_\_len\_\_ {#len tag="method" new="2"}

Get the number of rules added to the matcher. Note that this only returns the
number of rules (identical with the number of IDs), not the number of individual
patterns.

> #### Example
>
> ```python
> matcher = Matcher(nlp.vocab)
> assert len(matcher) == 0
> matcher.add("Rule", None, [{"ORTH": "test"}])
> assert len(matcher) == 1
> ```

| Name        | Type | Description          |
| ----------- | ---- | -------------------- |
| **RETURNS** | int  | The number of rules. |

## Matcher.\_\_contains\_\_ {#contains tag="method" new="2"}

Check whether the matcher contains rules for a match ID.

> #### Example
>
> ```python
> matcher = Matcher(nlp.vocab)
> assert 'Rule' not in matcher
> matcher.add('Rule', None, [{'ORTH': 'test'}])
> assert 'Rule' in matcher
> ```

| Name        | Type    | Description                                           |
| ----------- | ------- | ----------------------------------------------------- |
| `key`       | unicode | The match ID.                                         |
| **RETURNS** | bool    | Whether the matcher contains rules for this match ID. |

## Matcher.add {#add tag="method" new="2"}

Add a rule to the matcher, consisting of an ID key, one or more patterns, and a
callback function to act on the matches. The callback function will receive the
arguments `matcher`, `doc`, `i` and `matches`. If a pattern already exists for
the given ID, the patterns will be extended. An `on_match` callback will be
overwritten.

> #### Example
>
> ```python
>   def on_match(matcher, doc, id, matches):
>       print('Matched!', matches)
>
>   matcher = Matcher(nlp.vocab)
>   matcher.add("HelloWorld", on_match, [{"LOWER": "hello"}, {"LOWER": "world"}])
>   matcher.add("GoogleMaps", on_match, [{"ORTH": "Google"}, {"ORTH": "Maps"}])
>   doc = nlp("HELLO WORLD on Google Maps.")
>   matches = matcher(doc)
> ```

| Name        | Type               | Description                                                                                   |
| ----------- | ------------------ | --------------------------------------------------------------------------------------------- |
| `match_id`  | unicode            | An ID for the thing you're matching.                                                          |
| `on_match`  | callable or `None` | Callback function to act on matches. Takes the arguments `matcher`, `doc`, `i` and `matches`. |
| `*patterns` | list               | Match pattern. A pattern consists of a list of dicts, where each dict describes a token.      |

<Infobox title="Changed in v2.2.2" variant="warning">

As of spaCy 2.2.2, `Matcher.add` also supports the new API, which will become
the default in the future. The patterns are now the second argument and a list
(instead of a variable number of arguments). The `on_match` callback becomes an
optional keyword argument.

```diff
patterns = [[{"TEXT": "Google"}, {"TEXT": "Now"}], [{"TEXT": "GoogleNow"}]]
- matcher.add("GoogleNow", None, *patterns)
+ matcher.add("GoogleNow", patterns)
- matcher.add("GoogleNow", on_match, *patterns)
+ matcher.add("GoogleNow", patterns, on_match=on_match)
```

</Infobox>

## Matcher.remove {#remove tag="method" new="2"}

Remove a rule from the matcher. A `KeyError` is raised if the match ID does not
exist.

> #### Example
>
> ```python
> matcher.add("Rule", None, [{"ORTH": "test"}])
> assert "Rule" in matcher
> matcher.remove("Rule")
> assert "Rule" not in matcher
> ```

| Name  | Type    | Description               |
| ----- | ------- | ------------------------- |
| `key` | unicode | The ID of the match rule. |

## Matcher.get {#get tag="method" new="2"}

Retrieve the pattern stored for a key. Returns the rule as an
`(on_match, patterns)` tuple containing the callback and available patterns.

> #### Example
>
> ```python
> matcher.add("Rule", None, [{"ORTH": "test"}])
> on_match, patterns = matcher.get("Rule")
> ```

| Name        | Type    | Description                                   |
| ----------- | ------- | --------------------------------------------- |
| `key`       | unicode | The ID of the match rule.                     |
| **RETURNS** | tuple   | The rule, as an `(on_match, patterns)` tuple. |
