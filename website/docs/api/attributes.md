---
title: Attributes
teaser: Token attributes
source: spacy/attrs.pyx
---

[Token](/api/token) attributes are specified using internal IDs in many places
including:

- [`Matcher` patterns](/api/matcher#patterns),
- [`Doc.to_array`](/api/doc#to_array) and
  [`Doc.from_array`](/api/doc#from_array)
- [`Doc.has_annotation`](/api/doc#has_annotation)
- [`MultiHashEmbed`](/api/architectures#MultiHashEmbed) Tok2Vec architecture
  `attrs`

> ```python
> import spacy
> from spacy.attrs import DEP
>
> nlp = spacy.blank("en")
> doc = nlp("There are many attributes.")
>
> # DEP always has the same internal value
> assert DEP == 76
>
> # "DEP" is automatically converted to DEP
> assert DEP == nlp.vocab.strings["DEP"]
> assert doc.has_annotation(DEP) == doc.has_annotation("DEP")
>
> # look up IDs in spacy.attrs.IDS
> from spacy.attrs import IDS
> assert IDS["DEP"] == DEP
> ```

All methods automatically convert between the string version of an ID (`"DEP"`)
and the internal integer symbols (`DEP`). The internal IDs can be imported from
`spacy.attrs` or retrieved from the [`StringStore`](/api/stringstore). A map
from string attribute names to internal attribute IDs is stored in
`spacy.attrs.IDS`.

The corresponding [`Token` object attributes](/api/token#attributes) can be
accessed using the same names in lowercase, e.g. `token.orth` or `token.length`.
For attributes that represent string values, the internal integer ID is
accessed as `Token.attr`, e.g. `token.dep`, while the string value can be
retrieved by appending `_` as in `token.dep_`.


| Attribute    | Description                                                                                                                                                   |
| ------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `DEP`        | The token's dependency label. ~~str~~                                                                                                                         |
| `ENT_ID`     | The token's entity ID (`ent_id`). ~~str~~                                                                                                                     |
| `ENT_IOB`    | The IOB part of the token's entity tag. Uses custom integer vaues rather than the string store: unset is `0`, `I` is `1`, `O` is `2`, and `B` is `3`. ~~str~~ |
| `ENT_KB_ID`  | The token's entity knowledge base ID. ~~str~~                                                                                                                 |
| `ENT_TYPE`   | The token's entity label. ~~str~~                                                                                                                             |
| `IS_ALPHA`   | Token text consists of alphabetic characters. ~~bool~~                                                                                                        |
| `IS_ASCII`   | Token text consists of ASCII characters. ~~bool~~                                                                                                             |
| `IS_DIGIT`   | Token text consists of digits. ~~bool~~                                                                                                                       |
| `IS_LOWER`   | Token text is in lowercase. ~~bool~~                                                                                                                          |
| `IS_PUNCT`   | Token is punctuation. ~~bool~~                                                                                                                                |
| `IS_SPACE`   | Token is whitespace. ~~bool~~                                                                                                                                 |
| `IS_STOP`    | Token is a stop word. ~~bool~~                                                                                                                                |
| `IS_TITLE`   | Token text is in titlecase. ~~bool~~                                                                                                                          |
| `IS_UPPER`   | Token text is in uppercase. ~~bool~~                                                                                                                          |
| `LEMMA`      | The token's lemma. ~~str~~                                                                                                                                    |
| `LENGTH`     | The length of the token text. ~~int~~                                                                                                                         |
| `LIKE_EMAIL` | Token text resembles an email address. ~~bool~~                                                                                                               |
| `LIKE_NUM`   | Token text resembles a number. ~~bool~~                                                                                                                       |
| `LIKE_URL`   | Token text resembles a URL. ~~bool~~                                                                                                                          |
| `LOWER`      | The lowercase form of the token text. ~~str~~                                                                                                                 |
| `MORPH`      | The token's morphological analysis. ~~MorphAnalysis~~                                                                                                         |
| `NORM`       | The normalized form of the token text. ~~str~~                                                                                                                |
| `ORTH`       | The exact verbatim text of a token. ~~str~~                                                                                                                   |
| `POS`        | The token's universal part of speech (UPOS). ~~str~~                                                                                                          |
| `SENT_START` | Token is start of sentence. ~~bool~~                                                                                                                          |
| `SHAPE`      | The token's shape. ~~str~~                                                                                                                                    |
| `SPACY`      | Token has a trailing space. ~~bool~~                                                                                                                          |
| `TAG`        | The token's fine-grained part of speech. ~~str~~                                                                                                              |
