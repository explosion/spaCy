---
title: Matcher
teaser: Match sequences of tokens, based on pattern rules
tag: class
source: spacy/matcher/matcher.pyx
---

The `Matcher` lets you find words and phrases using rules describing their token
attributes. Rules can refer to token annotations (like the text or
part-of-speech tags), as well as lexical attributes like `Token.is_punct`.
Applying the matcher to a [`Doc`](/api/doc) gives you access to the matched
tokens in context. For in-depth examples and workflows for combining rules and
statistical models, see the [usage guide](/usage/rule-based-matching) on
rule-based matching.

## Pattern format {#patterns}

> ```json
> ### Example
> [
>   {"LOWER": "i"},
>   {"LEMMA": {"IN": ["like", "love"]}},
>   {"POS": "NOUN", "OP": "+"}
> ]
> ```

A pattern added to the `Matcher` consists of a list of dictionaries. Each
dictionary describes **one token** and its attributes. The available token
pattern keys correspond to a number of
[`Token` attributes](/api/token#attributes). The supported attributes for
rule-based matching are:

| Attribute                              | Type |  Description                                                                                           |
| -------------------------------------- | ---- | ------------------------------------------------------------------------------------------------------ |
| `ORTH`                                 | str  | The exact verbatim text of a token.                                                                    |
| `TEXT` <Tag variant="new">2.1</Tag>    | str  | The exact verbatim text of a token.                                                                    |
| `LOWER`                                | str  | The lowercase form of the token text.                                                                  |
|  `LENGTH`                              | int  | The length of the token text.                                                                          |
|  `IS_ALPHA`, `IS_ASCII`, `IS_DIGIT`    | bool | Token text consists of alphabetic characters, ASCII characters, digits.                                |
|  `IS_LOWER`, `IS_UPPER`, `IS_TITLE`    | bool | Token text is in lowercase, uppercase, titlecase.                                                      |
|  `IS_PUNCT`, `IS_SPACE`, `IS_STOP`     | bool | Token is punctuation, whitespace, stop word.                                                           |
|  `LIKE_NUM`, `LIKE_URL`, `LIKE_EMAIL`  | bool | Token text resembles a number, URL, email.                                                             |
|  `POS`, `TAG`, `DEP`, `LEMMA`, `SHAPE` | str  | The token's simple and extended part-of-speech tag, dependency label, lemma, shape.                    |
| `ENT_TYPE`                             | str  | The token's entity label.                                                                              |
| `_` <Tag variant="new">2.1</Tag>       | dict | Properties in [custom extension attributes](/usage/processing-pipelines#custom-components-attributes). |
| `OP`                                   | str  | Operator or quantifier to determine how often to match a token pattern.                                |

Operators and quantifiers define **how often** a token pattern should be
matched:

> ```json
> ### Example
> [
>   {"POS": "ADJ", "OP": "*"},
>   {"POS": "NOUN", "OP": "+"}
> ]
> ```

| OP  | Description                                                      |
| --- | ---------------------------------------------------------------- |
| `!` | Negate the pattern, by requiring it to match exactly 0 times.    |
| `?` | Make the pattern optional, by allowing it to match 0 or 1 times. |
| `+` | Require the pattern to match 1 or more times.                    |
| `*` | Allow the pattern to match zero or more times.                   |

Token patterns can also map to a **dictionary of properties** instead of a
single value to indicate whether the expected value is a member of a list or how
it compares to another value.

> ```json
> ### Example
> [
>   {"LEMMA": {"IN": ["like", "love", "enjoy"]}},
>   {"POS": "PROPN", "LENGTH": {">=": 10}},
> ]
> ```

| Attribute                  | Type       | Description                                                                       |
| -------------------------- | ---------- | --------------------------------------------------------------------------------- |
| `IN`                       | any        | Attribute value is member of a list.                                              |
| `NOT_IN`                   | any        | Attribute value is _not_ member of a list.                                        |
| `==`, `>=`, `<=`, `>`, `<` | int, float | Attribute value is equal, greater or equal, smaller or equal, greater or smaller. |

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

| Name                                    | Type    | Description                                                                                 |
| --------------------------------------- | ------- | ------------------------------------------------------------------------------------------- |
| `vocab`                                 | `Vocab` | The vocabulary object, which must be shared with the documents the matcher will operate on. |
| `validate` <Tag variant="new">2.1</Tag> | bool    | Validate all patterns added to this matcher.                                                |

## Matcher.\_\_call\_\_ {#call tag="method"}

Find all token sequences matching the supplied patterns on the `Doc` or `Span`.

> #### Example
>
> ```python
> from spacy.matcher import Matcher
>
> matcher = Matcher(nlp.vocab)
> pattern = [{"LOWER": "hello"}, {"LOWER": "world"}]
> matcher.add("HelloWorld", [pattern])
> doc = nlp("hello world!")
> matches = matcher(doc)
> ```

| Name        | Type         | Description                                                                                                                                                              |
| ----------- | ------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `doclike`   | `Doc`/`Span` | The `Doc` or `Span` to match over.                                                                                                                                       |
| **RETURNS** | list         | A list of `(match_id, start, end)` tuples, describing the matches. A match tuple describes a span `doc[start:end`]. The `match_id` is the ID of the added match pattern. |

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
| `docs`                                        | iterable | A stream of documents or spans.                                                                                                                                                                                            |
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
> matcher.add("Rule", [[{"ORTH": "test"}]])
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
> assert "Rule" not in matcher
> matcher.add("Rule", [[{'ORTH': 'test'}]])
> assert "Rule" in matcher
> ```

| Name        | Type | Description                                           |
| ----------- | ---- | ----------------------------------------------------- |
| `key`       | str  | The match ID.                                         |
| **RETURNS** | bool | Whether the matcher contains rules for this match ID. |

## Matcher.add {#add tag="method" new="2"}

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
> patterns = [
>    [{"LOWER": "hello"}, {"LOWER": "world"}],
>    [{"ORTH": "Google"}, {"ORTH": "Maps"}]
> ]
> matcher.add("TEST_PATTERNS", patterns)
> doc = nlp("HELLO WORLD on Google Maps.")
> matches = matcher(doc)
> ```

<Infobox title="Changed in v3.0" variant="warning">

As of spaCy v3.0, `Matcher.add` takes a list of patterns as the second argument
(instead of a variable number of arguments). The `on_match` callback becomes an
optional keyword argument.

```diff
patterns = [[{"TEXT": "Google"}, {"TEXT": "Now"}], [{"TEXT": "GoogleNow"}]]
- matcher.add("GoogleNow", on_match, *patterns)
+ matcher.add("GoogleNow", patterns, on_match=on_match)
```

</Infobox>

| Name                                | Type               | Description                                                                                   |
| ----------------------------------- | ------------------ | --------------------------------------------------------------------------------------------- |
| `match_id`                          | str                | An ID for the thing you're matching.                                                          |
| `patterns`                          | `List[List[dict]]` | Match pattern. A pattern consists of a list of dicts, where each dict describes a token.      |
| _keyword-only_                      |                    |                                                                                               |
| `on_match`                          | callable / `None`  | Callback function to act on matches. Takes the arguments `matcher`, `doc`, `i` and `matches`. |
| `greedy` <Tag variant="new">3</Tag> | str                | Optional filter for greedy matches. Can either be `"FIRST"` or `"LONGEST"`.                   |

## Matcher.remove {#remove tag="method" new="2"}

Remove a rule from the matcher. A `KeyError` is raised if the match ID does not
exist.

> #### Example
>
> ```python
> matcher.add("Rule", [[{"ORTH": "test"}]])
> assert "Rule" in matcher
> matcher.remove("Rule")
> assert "Rule" not in matcher
> ```

| Name  | Type | Description               |
| ----- | ---- | ------------------------- |
| `key` | str  | The ID of the match rule. |

## Matcher.get {#get tag="method" new="2"}

Retrieve the pattern stored for a key. Returns the rule as an
`(on_match, patterns)` tuple containing the callback and available patterns.

> #### Example
>
> ```python
> matcher.add("Rule", [[{"ORTH": "test"}]])
> on_match, patterns = matcher.get("Rule")
> ```

| Name        | Type  | Description                                   |
| ----------- | ----- | --------------------------------------------- |
| `key`       | str   | The ID of the match rule.                     |
| **RETURNS** | tuple | The rule, as an `(on_match, patterns)` tuple. |
