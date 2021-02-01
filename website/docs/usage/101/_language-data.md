Every language is different – and usually full of **exceptions and special
cases**, especially amongst the most common words. Some of these exceptions are
shared across languages, while others are **entirely specific** – usually so
specific that they need to be hard-coded. The
[`lang`](%%GITHUB_SPACY/spacy/lang) module contains all language-specific data,
organized in simple Python files. This makes the data easy to update and extend.

The **shared language data** in the directory root includes rules that can be
generalized across languages – for example, rules for basic punctuation, emoji,
emoticons and single-letter abbreviations. The **individual language data** in a
submodule contains rules that are only relevant to a particular language. It
also takes care of putting together all components and creating the
[`Language`](/api/language) subclass – for example, `English` or `German`. The
values are defined in the [`Language.Defaults`](/api/language#defaults).

> ```python
> from spacy.lang.en import English
> from spacy.lang.de import German
>
> nlp_en = English()  # Includes English data
> nlp_de = German()  # Includes German data
> ```

| Name                                                                                                                                                      | Description                                                                                                                                              |
| --------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Stop words**<br />[`stop_words.py`](%%GITHUB_SPACY/spacy/lang/en/stop_words.py)                                                                         | List of most common words of a language that are often useful to filter out, for example "and" or "I". Matching tokens will return `True` for `is_stop`. |
| **Tokenizer exceptions**<br />[`tokenizer_exceptions.py`](%%GITHUB_SPACY/spacy/lang/de/tokenizer_exceptions.py)                                           | Special-case rules for the tokenizer, for example, contractions like "can't" and abbreviations with punctuation, like "U.K.".                            |
| **Punctuation rules**<br />[`punctuation.py`](%%GITHUB_SPACY/spacy/lang/punctuation.py)                                                                   | Regular expressions for splitting tokens, e.g. on punctuation or special characters like emoji. Includes rules for prefixes, suffixes and infixes.       |
| **Character classes**<br />[`char_classes.py`](%%GITHUB_SPACY/spacy/lang/char_classes.py)                                                                 | Character classes to be used in regular expressions, for example, Latin characters, quotes, hyphens or icons.                                            |
| **Lexical attributes**<br />[`lex_attrs.py`](%%GITHUB_SPACY/spacy/lang/en/lex_attrs.py)                                                                   | Custom functions for setting lexical attributes on tokens, e.g. `like_num`, which includes language-specific words like "ten" or "hundred".              |
| **Syntax iterators**<br />[`syntax_iterators.py`](%%GITHUB_SPACY/spacy/lang/en/syntax_iterators.py)                                                       | Functions that compute views of a `Doc` object based on its syntax. At the moment, only used for [noun chunks](/usage/linguistic-features#noun-chunks).  |
| **Lemmatizer**<br />[`lemmatizer.py`](%%GITHUB_SPACY/spacy/lang/fr/lemmatizer.py) [`spacy-lookups-data`](https://github.com/explosion/spacy-lookups-data) | Custom lemmatizer implementation and lemmatization tables.                                                                                               |
