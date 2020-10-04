---
title: DependencyMatcher
teaser: Match subtrees within a dependency parse
tag: class
new: 3
source: spacy/matcher/dependencymatcher.pyx
---

The `DependencyMatcher` follows the same API as the [`Matcher`](/api/matcher)
and [`PhraseMatcher`](/api/phrasematcher) and lets you match on dependency trees
using
[Semgrex operators](https://nlp.stanford.edu/nlp/javadoc/javanlp/edu/stanford/nlp/semgraph/semgrex/SemgrexPattern.html).
It requires a pretrained [`DependencyParser`](/api/parser) or other component
that sets the `Token.dep` and `Token.head` attributes. See the
[usage guide](/usage/rule-based-matching#dependencymatcher) for examples.

## Pattern format {#patterns}

> ```python
> ### Example
> # pattern: "[subject] ... initially founded"
> [
>   # anchor token: founded
>   {
>     "RIGHT_ID": "founded",
>     "RIGHT_ATTRS": {"ORTH": "founded"}
>   },
>   # founded -> subject
>   {
>     "LEFT_ID": "founded",
>     "REL_OP": ">",
>     "RIGHT_ID": "subject",
>     "RIGHT_ATTRS": {"DEP": "nsubj"}
>   },
>   # "founded" follows "initially"
>   {
>     "LEFT_ID": "founded",
>     "REL_OP": ";",
>     "RIGHT_ID": "initially",
>     "RIGHT_ATTRS": {"ORTH": "initially"}
>   }
> ]
> ```

A pattern added to the `DependencyMatcher` consists of a list of dictionaries,
with each dictionary describing a token to match. Except for the first
dictionary, which defines an anchor token using only `RIGHT_ID` and
`RIGHT_ATTRS`, each pattern should have the following keys:

| Name          | Description                                                                                                                                                            |
| ------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `LEFT_ID`     | The name of the left-hand node in the relation, which has been defined in an earlier node. ~~str~~                                                                     |
| `REL_OP`      | An operator that describes how the two nodes are related. ~~str~~                                                                                                      |
| `RIGHT_ID`    | A unique name for the right-hand node in the relation. ~~str~~                                                                                                         |
| `RIGHT_ATTRS` | The token attributes to match for the right-hand node in the same format as patterns provided to the regular token-based [`Matcher`](/api/matcher). ~~Dict[str, Any]~~ |

<Infobox title="Designing dependency matcher patterns" emoji="📖">

For examples of how to construct dependency matcher patterns for different types
of relations, see the usage guide on
[dependency matching](/usage/rule-based-matching#dependencymatcher).

</Infobox>

### Operators

The following operators are supported by the `DependencyMatcher`, most of which
come directly from
[Semgrex](https://nlp.stanford.edu/nlp/javadoc/javanlp/edu/stanford/nlp/semgraph/semgrex/SemgrexPattern.html):

| Symbol    | Description                                                                                                          |
| --------- | -------------------------------------------------------------------------------------------------------------------- |
| `A < B`   | `A` is the immediate dependent of `B`.                                                                               |
| `A > B`   | `A` is the immediate head of `B`.                                                                                    |
| `A << B`  | `A` is the dependent in a chain to `B` following dep &rarr; head paths.                                              |
| `A >> B`  | `A` is the head in a chain to `B` following head &rarr; dep paths.                                                   |
| `A . B`   | `A` immediately precedes `B`, i.e. `A.i == B.i - 1`, and both are within the same dependency tree.                   |
| `A .* B`  | `A` precedes `B`, i.e. `A.i < B.i`, and both are within the same dependency tree _(not in Semgrex)_.                 |
| `A ; B`   | `A` immediately follows `B`, i.e. `A.i == B.i + 1`, and both are within the same dependency tree _(not in Semgrex)_. |
| `A ;* B`  | `A` follows `B`, i.e. `A.i > B.i`, and both are within the same dependency tree _(not in Semgrex)_.                  |
| `A $+ B`  | `B` is a right immediate sibling of `A`, i.e. `A` and `B` have the same parent and `A.i == B.i - 1`.                 |
| `A $- B`  | `B` is a left immediate sibling of `A`, i.e. `A` and `B` have the same parent and `A.i == B.i + 1`.                  |
| `A $++ B` | `B` is a right sibling of `A`, i.e. `A` and `B` have the same parent and `A.i < B.i`.                                |
| `A $-- B` | `B` is a left sibling of `A`, i.e. `A` and `B` have the same parent and `A.i > B.i`.                                 |

## DependencyMatcher.\_\_init\_\_ {#init tag="method"}

Create a `DependencyMatcher`.

> #### Example
>
> ```python
> from spacy.matcher import DependencyMatcher
> matcher = DependencyMatcher(nlp.vocab)
> ```

| Name           | Description                                                                                           |
| -------------- | ----------------------------------------------------------------------------------------------------- |
| `vocab`        | The vocabulary object, which must be shared with the documents the matcher will operate on. ~~Vocab~~ |
| _keyword-only_ |                                                                                                       |
| `validate`     | Validate all patterns added to this matcher. ~~bool~~                                                 |

## DependencyMatcher.\_\call\_\_ {#call tag="method"}

Find all tokens matching the supplied patterns on the `Doc` or `Span`.

> #### Example
>
> ```python
> from spacy.matcher import DependencyMatcher
>
> matcher = DependencyMatcher(nlp.vocab)
> pattern = [{"RIGHT_ID": "founded_id",
>   "RIGHT_ATTRS": {"ORTH": "founded"}}]
> matcher.add("FOUNDED", [pattern])
> doc = nlp("Bill Gates founded Microsoft.")
> matches = matcher(doc)
> ```

| Name        | Description                                                                                                                                                                                                                                                                                                                           |
| ----------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `doclike`   | The `Doc` or `Span` to match over. ~~Union[Doc, Span]~~                                                                                                                                                                                                                                                                               |
| **RETURNS** | A list of `(match_id, token_ids)` tuples, describing the matches. The `match_id` is the ID of the match pattern and `token_ids` is a list of token indices matched by the pattern, where the position of each token in the list corresponds to the position of the node specification in the pattern. ~~List[Tuple[int, List[int]]]~~ |

## DependencyMatcher.\_\_len\_\_ {#len tag="method"}

Get the number of rules added to the dependency matcher. Note that this only
returns the number of rules (identical with the number of IDs), not the number
of individual patterns.

> #### Example
>
> ```python
> matcher = DependencyMatcher(nlp.vocab)
> assert len(matcher) == 0
> pattern = [{"RIGHT_ID": "founded_id",
>   "RIGHT_ATTRS": {"ORTH": "founded"}}]
> matcher.add("FOUNDED", [pattern])
> assert len(matcher) == 1
> ```

| Name        | Description                  |
| ----------- | ---------------------------- |
| **RETURNS** | The number of rules. ~~int~~ |

## DependencyMatcher.\_\_contains\_\_ {#contains tag="method"}

Check whether the matcher contains rules for a match ID.

> #### Example
>
> ```python
> matcher = DependencyMatcher(nlp.vocab)
> assert "FOUNDED" not in matcher
> matcher.add("FOUNDED", [pattern])
> assert "FOUNDED" in matcher
> ```

| Name        | Description                                                    |
| ----------- | -------------------------------------------------------------- |
| `key`       | The match ID. ~~str~~                                          |
| **RETURNS** | Whether the matcher contains rules for this match ID. ~~bool~~ |

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
> matcher = DependencyMatcher(nlp.vocab)
> matcher.add("FOUNDED", patterns, on_match=on_match)
> ```

| Name           | Description                                                                                                                                                          |
| -------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `match_id`     | An ID for the patterns. ~~str~~                                                                                                                                      |
| `patterns`     | A list of match patterns. A pattern consists of a list of dicts, where each dict describes a token in the tree. ~~List[List[Dict[str, Union[str, Dict]]]]~~          |
| _keyword-only_ |                                                                                                                                                                      |
| `on_match`     | Callback function to act on matches. Takes the arguments `matcher`, `doc`, `i` and `matches`. ~~Optional[Callable[[DependencyMatcher, Doc, int, List[Tuple], Any]]~~ |

## DependencyMatcher.get {#get tag="method"}

Retrieve the pattern stored for a key. Returns the rule as an
`(on_match, patterns)` tuple containing the callback and available patterns.

> #### Example
>
> ```python
> matcher.add("FOUNDED", patterns, on_match=on_match)
> on_match, patterns = matcher.get("FOUNDED")
> ```

| Name        | Description                                                                                                 |
| ----------- | ----------------------------------------------------------------------------------------------------------- |
| `key`       | The ID of the match rule. ~~str~~                                                                           |
| **RETURNS** | The rule, as an `(on_match, patterns)` tuple. ~~Tuple[Optional[Callable], List[List[Union[Dict, Tuple]]]]~~ |

## DependencyMatcher.remove {#remove tag="method"}

Remove a rule from the dependency matcher. A `KeyError` is raised if the match
ID does not exist.

> #### Example
>
> ```python
> matcher.add("FOUNDED", patterns)
> assert "FOUNDED" in matcher
> matcher.remove("FOUNDED")
> assert "FOUNDED" not in matcher
> ```

| Name  | Description                       |
| ----- | --------------------------------- |
| `key` | The ID of the match rule. ~~str~~ |
