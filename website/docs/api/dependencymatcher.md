---
title: DependencyMatcher
teaser: Match sequences of tokens, based on the dependency parse
tag: class
source: spacy/matcher/dependencymatcher.pyx
---

The `DependencyMatcher` follows the same API as the [`Matcher`](/api/matcher)
and [`PhraseMatcher`](/api/phrasematcher) and lets you match on dependency trees
using the
[Semgrex syntax](https://nlp.stanford.edu/nlp/javadoc/javanlp/edu/stanford/nlp/semgraph/semgrex/SemgrexPattern.html).
It requires a pretrained [`DependencyParser`](/api/parser) or other component
that sets the `Token.dep` attribute.

## Pattern format {#patterns}

> ```json
> ### Example
> [
>   {
>     "SPEC": {"NODE_NAME": "founded"},
>     "PATTERN": {"ORTH": "founded"}
>   },
>   {
>     "SPEC": {
>       "NODE_NAME": "founder",
>       "NBOR_RELOP": ">",
>       "NBOR_NAME": "founded"
>   },
>     "PATTERN": {"DEP": "nsubj"}
>   },
>   {
>     "SPEC": {
>       "NODE_NAME": "object",
>       "NBOR_RELOP": ">",
>       "NBOR_NAME": "founded"
>   },
>     "PATTERN": {"DEP": "dobj"}
>   }
> ]
> ```

A pattern added to the `DependencyMatcher` consists of a list of dictionaries,
with each dictionary describing a node to match. Each pattern should have the
following top-level keys:

| Name      | Type | Description                                                                                                                 |
| --------- | ---- | --------------------------------------------------------------------------------------------------------------------------- |
| `PATTERN` | dict | The token attributes to match in the same format as patterns provided to the regular token-based [`Matcher`](/api/matcher). |
| `SPEC`    | dict | The relationships of the nodes in the subtree that should be matched.                                                       |

The `SPEC` includes the following fields:

| Name         | Type | Description                                                                                                                                                            |
| ------------ | ---- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `NODE_NAME`  | str  | A unique name for this node to refer to it in other specs.                                                                                                             |
| `NBOR_RELOP` | str  | A [Semgrex](https://nlp.stanford.edu/nlp/javadoc/javanlp/edu/stanford/nlp/semgraph/semgrex/SemgrexPattern.html) operator that describes how the two nodes are related. |
| `NBOR_NAME`  | str  | The unique name of the node that this node is connected to.                                                                                                            |

## DependencyMatcher.\_\_init\_\_ {#init tag="method"}

Create a rule-based `DependencyMatcher`.

> #### Example
>
> ```python
> from spacy.matcher import DependencyMatcher
> matcher = DependencyMatcher(nlp.vocab)
> ```

| Name    | Type    | Description                                                                                 |
| ------- | ------- | ------------------------------------------------------------------------------------------- |
| `vocab` | `Vocab` | The vocabulary object, which must be shared with the documents the matcher will operate on. |

## DependencyMatcher.\_\call\_\_ {#call tag="method"}

Find all token sequences matching the supplied patterns on the `Doc` or `Span`.

> #### Example
>
> ```python
> from spacy.matcher import Matcher
>
> matcher = Matcher(nlp.vocab)
> pattern = [
>     {"SPEC": {"NODE_NAME": "founded"}, "PATTERN": {"ORTH": "founded"}},
>     {"SPEC": {"NODE_NAME": "founder", "NBOR_RELOP": ">", "NBOR_NAME": "founded"}, "PATTERN": {"DEP": "nsubj"}},
> ]
> matcher.add("Founder", [pattern])
> doc = nlp("Bill Gates founded Microsoft.")
> matches = matcher(doc)
> ```

| Name        | Type         | Description                                                                                                                                                              |
| ----------- | ------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `doclike`   | `Doc`/`Span` | The `Doc` or `Span` to match over.                                                                                                                                       |
| **RETURNS** | list         | A list of `(match_id, start, end)` tuples, describing the matches. A match tuple describes a span `doc[start:end`]. The `match_id` is the ID of the added match pattern. |

## DependencyMatcher.\_\_len\_\_ {#len tag="method"}

Get the number of rules (edges) added to the dependency matcher. Note that this
only returns the number of rules (identical with the number of IDs), not the
number of individual patterns.

> #### Example
>
> ```python
> matcher = DependencyMatcher(nlp.vocab)
> assert len(matcher) == 0
> pattern = [
>     {"SPEC": {"NODE_NAME": "founded"}, "PATTERN": {"ORTH": "founded"}},
>     {"SPEC": {"NODE_NAME": "START_ENTITY", "NBOR_RELOP": ">", "NBOR_NAME": "founded"}, "PATTERN": {"DEP": "nsubj"}},
> ]
> matcher.add("Rule", [pattern])
> assert len(matcher) == 1
> ```

| Name        | Type | Description          |
| ----------- | ---- | -------------------- |
| **RETURNS** | int  | The number of rules. |

## DependencyMatcher.\_\_contains\_\_ {#contains tag="method"}

Check whether the matcher contains rules for a match ID.

> #### Example
>
> ```python
> matcher = Matcher(nlp.vocab)
> assert "Rule" not in matcher
> matcher.add("Rule", [pattern])
> assert "Rule" in matcher
> ```

| Name        | Type | Description                                           |
| ----------- | ---- | ----------------------------------------------------- |
| `key`       | str  | The match ID.                                         |
| **RETURNS** | bool | Whether the matcher contains rules for this match ID. |

## DependencyMatcher.add {#add tag="method"}

Add a rule to the matcher, consisting of an ID key, one or more patterns, and an
optional callback function to act on the matches. The callback function will
receive the arguments `matcher`, `doc`, `i` and `matches`. If a pattern already
exists for the given ID, the patterns will be extended. An `on_match` callback
will be overwritten.

> #### Example
>
> ```python
> def on_match(matcher, doc, id, matches):
>     print('Matched!', matches)
>
> matcher = Matcher(nlp.vocab)
> matcher.add("TEST_PATTERNS", patterns)
> ```

| Name           | Type               | Description                                                                                   |
| -------------- | ------------------ | --------------------------------------------------------------------------------------------- |
| `match_id`     | str                | An ID for the thing you're matching.                                                          |
| `patterns`     | list               | Match pattern. A pattern consists of a list of dicts, where each dict describes a token.      |
| _keyword-only_ |                    |                                                                                               |
| `on_match`     | callable or `None` | Callback function to act on matches. Takes the arguments `matcher`, `doc`, `i` and `matches`. |

## DependencyMatcher.remove {#remove tag="method"}

Remove a rule from the matcher. A `KeyError` is raised if the match ID does not
exist.

> #### Example
>
> ```python
> matcher.add("Rule", [pattern]])
> assert "Rule" in matcher
> matcher.remove("Rule")
> assert "Rule" not in matcher
> ```

| Name  | Type | Description               |
| ----- | ---- | ------------------------- |
| `key` | str  | The ID of the match rule. |

## DependencyMatcher.get {#get tag="method"}

Retrieve the pattern stored for a key. Returns the rule as an
`(on_match, patterns)` tuple containing the callback and available patterns.

> #### Example
>
> ```python
> matcher.add("Rule", [pattern], on_match=on_match)
> on_match, patterns = matcher.get("Rule")
> ```

| Name        | Type  | Description                                   |
| ----------- | ----- | --------------------------------------------- |
| `key`       | str   | The ID of the match rule.                     |
| **RETURNS** | tuple | The rule, as an `(on_match, patterns)` tuple. |
