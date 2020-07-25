---
title: Adding Languages
next: /usage/training
menu:
  - ['Language Data', 'language-data']
  - ['Testing', 'testing']
  - ['Training', 'training']
---

Adding full support for a language touches many different parts of the spaCy
library. This guide explains how to fit everything together, and points you to
the specific workflows for each component.

> #### Working on spaCy's source
>
> To add a new language to spaCy, you'll need to **modify the library's code**.
> The easiest way to do this is to clone the
> [repository](https://github.com/explosion/spaCy/tree/master/) and **build
> spaCy from source**. For more information on this, see the
> [installation guide](/usage). Unlike spaCy's core, which is mostly written in
> Cython, all language data is stored in regular Python files. This means that
> you won't have to rebuild anything in between – you can simply make edits and
> reload spaCy to test them.

<Grid cols={2}>

<div>

Obviously, there are lots of ways you can organize your code when you implement
your own language data. This guide will focus on how it's done within spaCy. For
full language support, you'll need to create a `Language` subclass, define
custom **language data**, like a stop list and tokenizer exceptions and test the
new tokenizer. Once the language is set up, you can **build the vocabulary**,
including word frequencies, Brown clusters and word vectors. Finally, you can
**train the tagger and parser**, and save the model to a directory.

For some languages, you may also want to develop a solution for lemmatization
and morphological analysis.

</div>

<Infobox title="Table of Contents" id="toc">

- [Language data 101](#language-data)
- [The Language subclass](#language-subclass)
- [Stop words](#stop-words)
- [Tokenizer exceptions](#tokenizer-exceptions)
- [Norm exceptions](#norm-exceptions)
- [Lexical attributes](#lex-attrs)
- [Syntax iterators](#syntax-iterators)
- [Lemmatizer](#lemmatizer)
- [Tag map](#tag-map)
- [Morph rules](#morph-rules)
- [Testing the language](#testing)
- [Training](#training)

</Infobox>

</Grid>

## Language data {#language-data}

import LanguageData101 from 'usage/101/\_language-data.md'

<LanguageData101 />

The individual components **expose variables** that can be imported within a
language module, and added to the language's `Defaults`. Some components, like
the punctuation rules, usually don't need much customization and can be imported
from the global rules. Others, like the tokenizer and norm exceptions, are very
specific and will make a big difference to spaCy's performance on the particular
language and training a language model.

| Variable               | Type  | Description                                                                                                |
| ---------------------- | ----- | ---------------------------------------------------------------------------------------------------------- |
| `STOP_WORDS`           | set   | Individual words.                                                                                          |
| `TOKENIZER_EXCEPTIONS` | dict  | Keyed by strings mapped to list of one dict per token with token attributes.                               |
| `TOKEN_MATCH`          | regex | Regexes to match complex tokens, e.g. URLs.                                                                |
| `NORM_EXCEPTIONS`      | dict  | Keyed by strings, mapped to their norms.                                                                   |
| `TOKENIZER_PREFIXES`   | list  | Strings or regexes, usually not customized.                                                                |
| `TOKENIZER_SUFFIXES`   | list  | Strings or regexes, usually not customized.                                                                |
| `TOKENIZER_INFIXES`    | list  | Strings or regexes, usually not customized.                                                                |
| `LEX_ATTRS`            | dict  | Attribute ID mapped to function.                                                                           |
| `SYNTAX_ITERATORS`     | dict  | Iterator ID mapped to function. Currently only supports `'noun_chunks'`.                                   |
| `TAG_MAP`              | dict  | Keyed by strings mapped to [Universal Dependencies](http://universaldependencies.org/u/pos/all.html) tags. |
| `MORPH_RULES`          | dict  | Keyed by strings mapped to a dict of their morphological features.                                         |

> #### Should I ever update the global data?
>
> Reusable language data is collected as atomic pieces in the root of the
> [`spacy.lang`](https://github.com/explosion/spaCy/tree/master/spacy/lang)
> module. Often, when a new language is added, you'll find a pattern or symbol
> that's missing. Even if it isn't common in other languages, it might be best
> to add it to the shared language data, unless it has some conflicting
> interpretation. For instance, we don't expect to see guillemot quotation
> symbols (`»` and `«`) in English text. But if we do see them, we'd probably
> prefer the tokenizer to split them off.

<Infobox title="For languages with non-latin characters">

In order for the tokenizer to split suffixes, prefixes and infixes, spaCy needs
to know the language's character set. If the language you're adding uses
non-latin characters, you might need to define the required character classes in
the global
[`char_classes.py`](https://github.com/explosion/spaCy/tree/master/spacy/lang/char_classes.py).
For efficiency, spaCy uses hard-coded unicode ranges to define character
classes, the definitions of which can be found on
[Wikipedia](https://en.wikipedia.org/wiki/Unicode_block). If the language
requires very specific punctuation rules, you should consider overwriting the
default regular expressions with your own in the language's `Defaults`.

</Infobox>

### Creating a language subclass {#language-subclass}

Language-specific code and resources should be organized into a sub-package of
spaCy, named according to the language's
[ISO code](https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes). For instance,
code and resources specific to Spanish are placed into a directory
`spacy/lang/es`, which can be imported as `spacy.lang.es`.

To get started, you can check out the
[existing languages](https://github.com/explosion/spacy/tree/master/spacy/lang).
Here's what the class could look like:

```python
### __init__.py (excerpt)
# import language-specific data
from .stop_words import STOP_WORDS
from .tokenizer_exceptions import TOKENIZER_EXCEPTIONS
from .lex_attrs import LEX_ATTRS

from ..tokenizer_exceptions import BASE_EXCEPTIONS
from ...language import Language
from ...attrs import LANG
from ...util import update_exc

# Create Defaults class in the module scope (necessary for pickling!)
class XxxxxDefaults(Language.Defaults):
    lex_attr_getters = dict(Language.Defaults.lex_attr_getters)
    lex_attr_getters[LANG] = lambda text: "xx" # language ISO code

    # Optional: replace flags with custom functions, e.g. like_num()
    lex_attr_getters.update(LEX_ATTRS)

    # Merge base exceptions and custom tokenizer exceptions
    tokenizer_exceptions = update_exc(BASE_EXCEPTIONS, TOKENIZER_EXCEPTIONS)
    stop_words = STOP_WORDS

# Create actual Language class
class Xxxxx(Language):
    lang = "xx" # Language ISO code
    Defaults = XxxxxDefaults # Override defaults

# Set default export – this allows the language class to be lazy-loaded
__all__ = ["Xxxxx"]
```

<Infobox title="Why lazy-loading?">

Some languages contain large volumes of custom data, like lemmatizer lookup
tables, or complex regular expression that are expensive to compute. As of spaCy
v2.0, `Language` classes are not imported on initialization and are only loaded
when you import them directly, or load a model that requires a language to be
loaded. To lazy-load languages in your application, you can use the
[`util.get_lang_class`](/api/top-level#util.get_lang_class) helper function with
the two-letter language code as its argument.

</Infobox>

### Stop words {#stop-words}

A ["stop list"](https://en.wikipedia.org/wiki/Stop_words) is a classic trick
from the early days of information retrieval when search was largely about
keyword presence and absence. It is still sometimes useful today to filter out
common words from a bag-of-words model. To improve readability, `STOP_WORDS` are
separated by spaces and newlines, and added as a multiline string.

> #### What does spaCy consider a stop word?
>
> There's no particularly principled logic behind what words should be added to
> the stop list. Make a list that you think might be useful to people and is
> likely to be unsurprising. As a rule of thumb, words that are very rare are
> unlikely to be useful stop words.

```python
### Example
STOP_WORDS = set("""
a about above across after afterwards again against all almost alone along
already also although always am among amongst amount an and another any anyhow
anyone anything anyway anywhere are around as at

back be became because become becomes becoming been before beforehand behind
being below beside besides between beyond both bottom but by
""".split())
```

<Infobox title="Important note" variant="warning">

When adding stop words from an online source, always **include the link** in a
comment. Make sure to **proofread** and double-check the words carefully. A lot
of the lists available online have been passed around for years and often
contain mistakes, like unicode errors or random words that have once been added
for a specific use case, but don't actually qualify.

</Infobox>

### Tokenizer exceptions {#tokenizer-exceptions}

spaCy's [tokenization algorithm](/usage/linguistic-features#how-tokenizer-works)
lets you deal with whitespace-delimited chunks separately. This makes it easy to
define special-case rules, without worrying about how they interact with the
rest of the tokenizer. Whenever the key string is matched, the special-case rule
is applied, giving the defined sequence of tokens.

Tokenizer exceptions can be added in the following format:

```python
### tokenizer_exceptions.py (excerpt)
TOKENIZER_EXCEPTIONS = {
    "don't": [
        {ORTH: "do"},
        {ORTH: "n't", NORM: "not"}]
}
```

<Infobox title="Important note" variant="warning">

If an exception consists of more than one token, the `ORTH` values combined
always need to **match the original string**. The way the original string is
split up can be pretty arbitrary sometimes – for example `"gonna"` is split into
`"gon"` (norm "going") and `"na"` (norm "to"). Because of how the tokenizer
works, it's currently not possible to split single-letter strings into multiple
tokens.

</Infobox>

> #### Generating tokenizer exceptions
>
> Keep in mind that generating exceptions only makes sense if there's a clearly
> defined and **finite number** of them, like common contractions in English.
> This is not always the case – in Spanish for instance, infinitive or
> imperative reflexive verbs and pronouns are one token (e.g. "vestirme"). In
> cases like this, spaCy shouldn't be generating exceptions for _all verbs_.
> Instead, this will be handled at a later stage after part-of-speech tagging
> and lemmatization.

When adding the tokenizer exceptions to the `Defaults`, you can use the
[`update_exc`](/api/top-level#util.update_exc) helper function to merge them
with the global base exceptions (including one-letter abbreviations and
emoticons). The function performs a basic check to make sure exceptions are
provided in the correct format. It can take any number of exceptions dicts as
its arguments, and will update and overwrite the exception in this order. For
example, if your language's tokenizer exceptions include a custom tokenization
pattern for "a.", it will overwrite the base exceptions with the language's
custom one.

```python
### Example
from ...util import update_exc

BASE_EXCEPTIONS =  {"a.": [{ORTH: "a."}], ":)": [{ORTH: ":)"}]}
TOKENIZER_EXCEPTIONS = {"a.": [{ORTH: "a.", NORM: "all"}]}

tokenizer_exceptions = update_exc(BASE_EXCEPTIONS, TOKENIZER_EXCEPTIONS)
# {"a.": [{ORTH: "a.", NORM: "all"}], ":)": [{ORTH: ":)"}]}
```

### Norm exceptions {#norm-exceptions new="2"}

In addition to `ORTH`, tokenizer exceptions can also set a `NORM` attribute.
This is useful to specify a normalized version of the token – for example, the
norm of "n't" is "not". By default, a token's norm equals its lowercase text. If
the lowercase spelling of a word exists, norms should always be in lowercase.

> #### Norms vs. lemmas
>
> ```python
> doc = nlp("I'm gonna realise")
> norms = [token.norm_ for token in doc]
> lemmas = [token.lemma_ for token in doc]
> assert norms == ["i", "am", "going", "to", "realize"]
> assert lemmas == ["i", "be", "go", "to", "realise"]
> ```

spaCy usually tries to normalize words with different spellings to a single,
common spelling. This has no effect on any other token attributes, or
tokenization in general, but it ensures that **equivalent tokens receive similar
representations**. This can improve the model's predictions on words that
weren't common in the training data, but are equivalent to other words – for
example, "realise" and "realize", or "thx" and "thanks".

Similarly, spaCy also includes
[global base norms](https://github.com/explosion/spaCy/tree/master/spacy/lang/norm_exceptions.py)
for normalizing different styles of quotation marks and currency symbols. Even
though `$` and `€` are very different, spaCy normalizes them both to `$`. This
way, they'll always be seen as similar, no matter how common they were in the
training data.

As of spaCy v2.3, language-specific norm exceptions are provided as a
JSON dictionary in the package
[`spacy-lookups-data`](https://github.com/explosion/spacy-lookups-data) rather
than in the main library. For a full example, see
[`en_lexeme_norm.json`](https://github.com/explosion/spacy-lookups-data/blob/master/spacy_lookups_data/data/en_lexeme_norm.json).

```json
### Example
{
    "cos": "because",
    "fav": "favorite",
    "accessorise": "accessorize",
    "accessorised": "accessorized"
}
```

If you're adding tables for a new languages, be sure to add the tables to
[`spacy_lookups_data/__init__.py`](https://github.com/explosion/spacy-lookups-data/blob/master/spacy_lookups_data/__init__.py)
and register the entry point under `spacy_lookups` in
[`setup.cfg`](https://github.com/explosion/spacy-lookups-data/blob/master/setup.cfg).

Alternatively, you can initialize your language [`Vocab`](/api/vocab) with a
[`Lookups`](/api/lookups) object that includes the table `lexeme_norm`.

<Accordion title="Norm exceptions in spaCy v2.0-v2.2" id="norm-exceptions-v2.2">

Previously in spaCy v2.0-v2.2, norm exceptions were provided as a simple python
dictionary. For more examples, see the English
[`norm_exceptions.py`](https://github.com/explosion/spaCy/tree/v2.2.x/spacy/lang/en/norm_exceptions.py).

```python
### Example
NORM_EXCEPTIONS = {
    "cos": "because",
    "fav": "favorite",
    "accessorise": "accessorize",
    "accessorised": "accessorized"
}
```

To add the custom norm exceptions lookup table, you can use the `add_lookups()`
helper functions. It takes the default attribute getter function as its first
argument, plus a variable list of dictionaries. If a string's norm is found in
one of the dictionaries, that value is used – otherwise, the default function is
called and the token is assigned its default norm.

```python
lex_attr_getters[NORM] = add_lookups(Language.Defaults.lex_attr_getters[NORM],
                                     NORM_EXCEPTIONS, BASE_NORMS)
```

The order of the dictionaries is also the lookup order – so if your language's
norm exceptions overwrite any of the global exceptions, they should be added
first. Also note that the tokenizer exceptions will always have priority over
the attribute getters.

</Accordion>

### Lexical attributes {#lex-attrs new="2"}

spaCy provides a range of [`Token` attributes](/api/token#attributes) that
return useful information on that token – for example, whether it's uppercase or
lowercase, a left or right punctuation mark, or whether it resembles a number or
email address. Most of these functions, like `is_lower` or `like_url` should be
language-independent. Others, like `like_num` (which includes both digits and
number words), requires some customization.

> #### Best practices
>
> Keep in mind that those functions are only intended to be an approximation.
> It's always better to prioritize simplicity and performance over covering very
> specific edge cases.
>
> English number words are pretty simple, because even large numbers consist of
> individual tokens, and we can get away with splitting and matching strings
> against a list. In other languages, like German, "two hundred and thirty-four"
> is one word, and thus one token. Here, it's best to match a string against a
> list of number word fragments (instead of a technically almost infinite list
> of possible number words).

Here's an example from the English
[`lex_attrs.py`](https://github.com/explosion/spaCy/tree/master/spacy/lang/en/lex_attrs.py):

```python
### lex_attrs.py
_num_words = ["zero", "one", "two", "three", "four", "five", "six", "seven",
              "eight", "nine", "ten", "eleven", "twelve", "thirteen", "fourteen",
              "fifteen", "sixteen", "seventeen", "eighteen", "nineteen", "twenty",
              "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety",
              "hundred", "thousand", "million", "billion", "trillion", "quadrillion",
              "gajillion", "bazillion"]

def like_num(text):
    text = text.replace(",", "").replace(".", "")
    if text.isdigit():
        return True
    if text.count("/") == 1:
        num, denom = text.split("/")
        if num.isdigit() and denom.isdigit():
            return True
    if text.lower() in _num_words:
        return True
    return False

LEX_ATTRS = {
    LIKE_NUM: like_num
}
```

By updating the default lexical attributes with a custom `LEX_ATTRS` dictionary
in the language's defaults via `lex_attr_getters.update(LEX_ATTRS)`, only the
new custom functions are overwritten.

### Syntax iterators {#syntax-iterators}

Syntax iterators are functions that compute views of a `Doc` object based on its
syntax. At the moment, this data is only used for extracting
[noun chunks](/usage/linguistic-features#noun-chunks), which are available as
the [`Doc.noun_chunks`](/api/doc#noun_chunks) property. Because base noun
phrases work differently across languages, the rules to compute them are part of
the individual language's data. If a language does not include a noun chunks
iterator, the property won't be available. For examples, see the existing syntax
iterators:

> #### Noun chunks example
>
> ```python
> doc = nlp("A phrase with another phrase occurs.")
> chunks = list(doc.noun_chunks)
> assert chunks[0].text == "A phrase"
> assert chunks[1].text == "another phrase"
> ```

| Language         | Code | Source                                                                                                            |
| ---------------- | ---- | ----------------------------------------------------------------------------------------------------------------- |
| English          | `en` | [`lang/en/syntax_iterators.py`](https://github.com/explosion/spaCy/tree/master/spacy/lang/en/syntax_iterators.py) |
| German           | `de` | [`lang/de/syntax_iterators.py`](https://github.com/explosion/spaCy/tree/master/spacy/lang/de/syntax_iterators.py) |
| French           | `fr` | [`lang/fr/syntax_iterators.py`](https://github.com/explosion/spaCy/tree/master/spacy/lang/fr/syntax_iterators.py) |
| Spanish          | `es` | [`lang/es/syntax_iterators.py`](https://github.com/explosion/spaCy/tree/master/spacy/lang/es/syntax_iterators.py) |
| Greek            | `el` | [`lang/el/syntax_iterators.py`](https://github.com/explosion/spaCy/tree/master/spacy/lang/el/syntax_iterators.py) |
| Norwegian Bokmål | `nb` | [`lang/nb/syntax_iterators.py`](https://github.com/explosion/spaCy/tree/master/spacy/lang/nb/syntax_iterators.py) |
| Swedish          | `sv` | [`lang/sv/syntax_iterators.py`](https://github.com/explosion/spaCy/tree/master/spacy/lang/sv/syntax_iterators.py) |
| Indonesian       | `id` | [`lang/id/syntax_iterators.py`](https://github.com/explosion/spaCy/tree/master/spacy/lang/id/syntax_iterators.py) |
| Persian          | `fa` | [`lang/fa/syntax_iterators.py`](https://github.com/explosion/spaCy/tree/master/spacy/lang/fa/syntax_iterators.py) |

### Lemmatizer {#lemmatizer new="2"}

As of v2.0, spaCy supports simple lookup-based lemmatization. This is usually
the quickest and easiest way to get started. The data is stored in a dictionary
mapping a string to its lemma. To determine a token's lemma, spaCy simply looks
it up in the table. Here's an example from the Spanish language data:

```json
### es_lemma_lookup.json (excerpt)
{
  "aba": "abar",
  "ababa": "abar",
  "ababais": "abar",
  "ababan": "abar",
  "ababanes": "ababán",
  "ababas": "abar",
  "ababoles": "ababol",
  "ababábites": "ababábite"
}
```

#### Adding JSON resources {#lemmatizer-resources new="2.2"}

As of v2.2, resources for the lemmatizer are stored as JSON and have been moved
to a separate repository and package,
[`spacy-lookups-data`](https://github.com/explosion/spacy-lookups-data). The
package exposes the data files via language-specific
[entry points](/usage/saving-loading#entry-points) that spaCy reads when
constructing the `Vocab` and [`Lookups`](/api/lookups). This allows easier
access to the data, serialization with the models and file compression on disk
(so your spaCy installation is smaller). If you want to use the lookup tables
without a pretrained model, you have to explicitly install spaCy with lookups
via `pip install spacy[lookups]` or by installing
[`spacy-lookups-data`](https://github.com/explosion/spacy-lookups-data) in the
same environment as spaCy.

### Tag map {#tag-map}

Most treebanks define a custom part-of-speech tag scheme, striking a balance
between level of detail and ease of prediction. While it's useful to have custom
tagging schemes, it's also useful to have a common scheme, to which the more
specific tags can be related. The tagger can learn a tag scheme with any
arbitrary symbols. However, you need to define how those symbols map down to the
[Universal Dependencies tag set](http://universaldependencies.org/u/pos/all.html).
This is done by providing a tag map.

The keys of the tag map should be **strings in your tag set**. The values should
be a dictionary. The dictionary must have an entry POS whose value is one of the
[Universal Dependencies](http://universaldependencies.org/u/pos/all.html) tags.
Optionally, you can also include morphological features or other token
attributes in the tag map as well. This allows you to do simple
[rule-based morphological analysis](/usage/linguistic-features#rule-based-morphology).

```python
### Example
from ..symbols import POS, NOUN, VERB, DET

TAG_MAP = {
    "NNS":  {POS: NOUN, "Number": "plur"},
    "VBG":  {POS: VERB, "VerbForm": "part", "Tense": "pres", "Aspect": "prog"},
    "DT":   {POS: DET}
}
```

### Morph rules {#morph-rules}

The morphology rules let you set token attributes such as lemmas, keyed by the
extended part-of-speech tag and token text. The morphological features and their
possible values are language-specific and based on the
[Universal Dependencies scheme](http://universaldependencies.org).

```python
### Example
from ..symbols import LEMMA

MORPH_RULES = {
    "VBZ": {
        "am": {LEMMA: "be", "VerbForm": "Fin", "Person": "One", "Tense": "Pres", "Mood": "Ind"},
        "are": {LEMMA: "be", "VerbForm": "Fin", "Person": "Two", "Tense": "Pres", "Mood": "Ind"},
        "is": {LEMMA: "be", "VerbForm": "Fin", "Person": "Three", "Tense": "Pres", "Mood": "Ind"},
        "'re": {LEMMA: "be", "VerbForm": "Fin", "Person": "Two", "Tense": "Pres", "Mood": "Ind"},
        "'s": {LEMMA: "be", "VerbForm": "Fin", "Person": "Three", "Tense": "Pres", "Mood": "Ind"}
    }
}
```

In the example of `"am"`, the attributes look like this:

| Attribute           | Description                                                                                                                    |
| ------------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| `LEMMA: "be"`       | Base form, e.g. "to be".                                                                                                       |
| `"VerbForm": "Fin"` | Finite verb. Finite verbs have a subject and can be the root of an independent clause – "I am." is a valid, complete sentence. |
| `"Person": "One"`   | First person, i.e. "**I** am".                                                                                                 |
| `"Tense": "Pres"`   | Present tense, i.e. actions that are happening right now or actions that usually happen.                                       |
| `"Mood": "Ind"`     | Indicative, i.e. something happens, has happened or will happen (as opposed to imperative or conditional).                     |

<Infobox title="Important note" variant="warning">

The morphological attributes are currently **not all used by spaCy**. Full
integration is still being developed. In the meantime, it can still be useful to
add them, especially if the language you're adding includes important
distinctions and special cases. This ensures that as soon as full support is
introduced, your language will be able to assign all possible attributes.

</Infobox>

## Testing the new language {#testing}

Before using the new language or submitting a
[pull request](https://github.com/explosion/spaCy/pulls) to spaCy, you should
make sure it works as expected. This is especially important if you've added
custom regular expressions for token matching or punctuation – you don't want to
be causing regressions.

<Infobox title="spaCy's test suite">

spaCy uses the [pytest framework](https://docs.pytest.org/en/latest/) for
testing. For more details on how the tests are structured and best practices for
writing your own tests, see our
[tests documentation](https://github.com/explosion/spaCy/tree/master/spacy/tests).

</Infobox>

### Writing language-specific tests {#testing-custom}

It's recommended to always add at least some tests with examples specific to the
language. Language tests should be located in
[`tests/lang`](https://github.com/explosion/spaCy/tree/master/spacy/tests/lang)
in a directory named after the language ID. You'll also need to create a fixture
for your tokenizer in the
[`conftest.py`](https://github.com/explosion/spaCy/tree/master/spacy/tests/conftest.py).
Always use the [`get_lang_class`](/api/top-level#util.get_lang_class) helper
function within the fixture, instead of importing the class at the top of the
file. This will load the language data only when it's needed. (Otherwise, _all
data_ would be loaded every time you run a test.)

```python
@pytest.fixture
def en_tokenizer():
    return util.get_lang_class("en").Defaults.create_tokenizer()
```

When adding test cases, always
[`parametrize`](https://github.com/explosion/spaCy/tree/master/spacy/tests#parameters)
them – this will make it easier for others to add more test cases without having
to modify the test itself. You can also add parameter tuples, for example, a
test sentence and its expected length, or a list of expected tokens. Here's an
example of an English tokenizer test for combinations of punctuation and
abbreviations:

```python
### Example test
@pytest.mark.parametrize('text,length', [
    ("The U.S. Army likes Shock and Awe.", 8),
    ("U.N. regulations are not a part of their concern.", 10),
    ("“Isn't it?”", 6)])
def test_en_tokenizer_handles_punct_abbrev(en_tokenizer, text, length):
    tokens = en_tokenizer(text)
    assert len(tokens) == length
```

## Training a language model {#training}

Much of spaCy's functionality requires models to be trained from labeled data.
For instance, in order to use the named entity recognizer, you need to first
train a model on text annotated with examples of the entities you want to
recognize. The parser, part-of-speech tagger and text categorizer all also
require models to be trained from labeled examples. The word vectors, word
probabilities and word clusters also require training, although these can be
trained from unlabeled text, which tends to be much easier to collect.

### Creating a vocabulary file {#vocab-file}

spaCy expects that common words will be cached in a [`Vocab`](/api/vocab)
instance. The vocabulary caches lexical features. spaCy loads the vocabulary
from binary data, in order to keep loading efficient. The easiest way to save
out a new binary vocabulary file is to use the `spacy init-model` command, which
expects a JSONL file with words and their lexical attributes. See the docs on
the [vocab JSONL format](/api/annotation#vocab-jsonl) for details.

#### Training the word vectors {#word-vectors}

[Word2vec](https://en.wikipedia.org/wiki/Word2vec) and related algorithms let
you train useful word similarity models from unlabeled text. This is a key part
of using deep learning for NLP with limited labeled data. The vectors are also
useful by themselves – they power the `.similarity` methods in spaCy. For best
results, you should pre-process the text with spaCy before training the Word2vec
model. This ensures your tokenization will match. You can use our
[word vectors training script](https://github.com/explosion/spacy/tree/master/bin/train_word_vectors.py),
which pre-processes the text with your language-specific tokenizer and trains
the model using [Gensim](https://radimrehurek.com/gensim/). The `vectors.bin`
file should consist of one word and vector per line.

```python
https://github.com/explosion/spacy/tree/master/bin/train_word_vectors.py
```

If you don't have a large sample of text available, you can also convert word
vectors produced by a variety of other tools into spaCy's format. See the docs
on [converting word vectors](/usage/vectors-similarity#converting) for details.

### Creating or converting a training corpus {#training-corpus}

The easiest way to train spaCy's tagger, parser, entity recognizer or text
categorizer is to use the [`spacy train`](/api/cli#train) command-line utility.
In order to use this, you'll need training and evaluation data in the
[JSON format](/api/annotation#json-input) spaCy expects for training.

If your data is in one of the supported formats, the easiest solution might be
to use the [`spacy convert`](/api/cli#convert) command-line utility. This
supports several popular formats, including the IOB format for named entity
recognition, the JSONL format produced by our annotation tool
[Prodigy](https://prodi.gy), and the
[CoNLL-U](http://universaldependencies.org/docs/format.html) format used by the
[Universal Dependencies](http://universaldependencies.org/) corpus.

One thing to keep in mind is that spaCy expects to train its models from **whole
documents**, not just single sentences. If your corpus only contains single
sentences, spaCy's models will never learn to expect multi-sentence documents,
leading to low performance on real text. To mitigate this problem, you can use
the `-n` argument to the `spacy convert` command, to merge some of the sentences
into longer pseudo-documents.

### Training the tagger and parser {#train-tagger-parser}

Once you have your training and evaluation data in the format spaCy expects, you
can train your model use the using spaCy's [`train`](/api/cli#train) command.
Note that training statistical models still involves a degree of
trial-and-error. You may need to tune one or more settings, also called
"hyper-parameters", to achieve optimal performance. See the
[usage guide on training](/usage/training#tagger-parser) for more details.
