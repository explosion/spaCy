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

| Attribute                                       |  Description                                                                                                              |
| ----------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------- |
| `ORTH`                                          | The exact verbatim text of a token. ~~str~~                                                                               |
| `TEXT` <Tag variant="new">2.1</Tag>             | The exact verbatim text of a token. ~~str~~                                                                               |
| `LOWER`                                         | The lowercase form of the token text. ~~str~~                                                                             |
|  `LENGTH`                                       | The length of the token text. ~~int~~                                                                                     |
|  `IS_ALPHA`, `IS_ASCII`, `IS_DIGIT`             | Token text consists of alphabetic characters, ASCII characters, digits. ~~bool~~                                          |
|  `IS_LOWER`, `IS_UPPER`, `IS_TITLE`             | Token text is in lowercase, uppercase, titlecase. ~~bool~~                                                                |
|  `IS_PUNCT`, `IS_SPACE`, `IS_STOP`              | Token is punctuation, whitespace, stop word. ~~bool~~                                                                     |
|  `IS_SENT_START`                                | Token is start of sentence. ~~bool~~                                                                                      |
|  `LIKE_NUM`, `LIKE_URL`, `LIKE_EMAIL`           | Token text resembles a number, URL, email. ~~bool~~                                                                       |
| `SPACY`                                         | Token has a trailing space. ~~bool~~                                                                                      |
|  `POS`, `TAG`, `MORPH`, `DEP`, `LEMMA`, `SHAPE` | The token's simple and extended part-of-speech tag, morphological analysis, dependency label, lemma, shape. ~~str~~       |
| `ENT_TYPE`                                      | The token's entity label. ~~str~~                                                                                         |
| `ENT_ID`                                        | The token's entity ID (`ent_id`). ~~str~~                                                                                 |
| `ENT_KB_ID`                                     | The token's entity knowledge base ID (`ent_kb_id`). ~~str~~                                                               |
| `_` <Tag variant="new">2.1</Tag>                | Properties in [custom extension attributes](/usage/processing-pipelines#custom-components-attributes). ~~Dict[str, Any]~~ |
| `OP`                                            | Operator or quantifier to determine how often to match a token pattern. ~~str~~                                           |

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
| `*` | Allow the pattern to match 0 or more times.                      |

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

| Attribute                  | Description                                                                                              |
| -------------------------- | -------------------------------------------------------------------------------------------------------- |
| `IN`                       | Attribute value is member of a list. ~~Any~~                                                             |
| `NOT_IN`                   | Attribute value is _not_ member of a list. ~~Any~~                                                       |
| `IS_SUBSET`                | Attribute value (for `MORPH` or custom list attributes) is a subset of a list. ~~Any~~                   |
| `IS_SUPERSET`              | Attribute value (for `MORPH` or custom list attributes) is a superset of a list. ~~Any~~                 |
| `INTERSECTS`               | Attribute value (for `MORPH` or custom list attribute) has a non-empty intersection with a list. ~~Any~~ |
| `==`, `>=`, `<=`, `>`, `<` | Attribute value is equal, greater or equal, smaller or equal, greater or smaller. ~~Union[int, float]~~  |

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

| Name                                    | Description                                                                                           |
| --------------------------------------- | ----------------------------------------------------------------------------------------------------- |
| `vocab`                                 | The vocabulary object, which must be shared with the documents the matcher will operate on. ~~Vocab~~ |
| `validate` <Tag variant="new">2.1</Tag> | Validate all patterns added to this matcher. ~~bool~~                                                 |

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

| Name                                             | Description                                                                                                                                                                                                                                                                                              |
| ------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `doclike`                                        | The `Doc` or `Span` to match over. ~~Union[Doc, Span]~~                                                                                                                                                                                                                                                  |
| _keyword-only_                                   |                                                                                                                                                                                                                                                                                                          |
| `as_spans` <Tag variant="new">3</Tag>            | Instead of tuples, return a list of [`Span`](/api/span) objects of the matches, with the `match_id` assigned as the span label. Defaults to `False`. ~~bool~~                                                                                                                                            |
| `allow_missing` <Tag variant="new">3</Tag>       | Whether to skip checks for missing annotation for attributes included in patterns. Defaults to `False`. ~~bool~~                                                                                                                                                                                         |
| `with_alignments` <Tag variant="new">3.0.6</Tag> | Return match alignment information as part of the match tuple as `List[int]` with the same length as the matched span. Each entry denotes the corresponding index of the token pattern. If `as_spans` is set to `True`, this setting is ignored. Defaults to `False`. ~~bool~~                           |
| **RETURNS**                                      | A list of `(match_id, start, end)` tuples, describing the matches. A match tuple describes a span `doc[start:end`]. The `match_id` is the ID of the added match pattern. If `as_spans` is set to `True`, a list of `Span` objects is returned instead. ~~Union[List[Tuple[int, int, int]], List[Span]]~~ |

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

| Name        | Description                  |
| ----------- | ---------------------------- |
| **RETURNS** | The number of rules. ~~int~~ |

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

| Name        | Description                                                    |
| ----------- | -------------------------------------------------------------- |
| `key`       | The match ID. ~~str~~                                          |
| **RETURNS** | Whether the matcher contains rules for this match ID. ~~bool~~ |

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

| Name                                | Description                                                                                                                                                |
| ----------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `match_id`                          | An ID for the thing you're matching. ~~str~~                                                                                                               |
| `patterns`                          | Match pattern. A pattern consists of a list of dicts, where each dict describes a token. ~~List[List[Dict[str, Any]]]~~                                    |
| _keyword-only_                      |                                                                                                                                                            |
| `on_match`                          | Callback function to act on matches. Takes the arguments `matcher`, `doc`, `i` and `matches`. ~~Optional[Callable[[Matcher, Doc, int, List[tuple], Any]]~~ |
| `greedy` <Tag variant="new">3</Tag> | Optional filter for greedy matches. Can either be `"FIRST"` or `"LONGEST"`. ~~Optional[str]~~                                                              |

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

| Name  | Description                       |
| ----- | --------------------------------- |
| `key` | The ID of the match rule. ~~str~~ |

## Matcher.get {#get tag="method" new="2"}

Retrieve the pattern stored for a key. Returns the rule as an
`(on_match, patterns)` tuple containing the callback and available patterns.

> #### Example
>
> ```python
> matcher.add("Rule", [[{"ORTH": "test"}]])
> on_match, patterns = matcher.get("Rule")
> ```

| Name        | Description                                                                                   |
| ----------- | --------------------------------------------------------------------------------------------- |
| `key`       | The ID of the match rule. ~~str~~                                                             |
| **RETURNS** | The rule, as an `(on_match, patterns)` tuple. ~~Tuple[Optional[Callable], List[List[dict]]]~~ |
