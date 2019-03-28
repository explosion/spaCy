The central data structures in spaCy are the `Doc` and the `Vocab`. The `Doc`
object owns the **sequence of tokens** and all their annotations. The `Vocab`
object owns a set of **look-up tables** that make common information available
across documents. By centralizing strings, word vectors and lexical attributes,
we avoid storing multiple copies of this data. This saves memory, and ensures
there's a **single source of truth**.

Text annotations are also designed to allow a single source of truth: the `Doc`
object owns the data, and `Span` and `Token` are **views that point into it**.
The `Doc` object is constructed by the `Tokenizer`, and then **modified in
place** by the components of the pipeline. The `Language` object coordinates
these components. It takes raw text and sends it through the pipeline, returning
an **annotated document**. It also orchestrates training and serialization.

![Library architecture](../../images/architecture.svg)

### Container objects {#architecture-containers}

| Name                    | Description                                                                                                                                             |
| ----------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [`Doc`](/api/doc)       | A container for accessing linguistic annotations.                                                                                                       |
| [`Span`](/api/span)     | A slice from a `Doc` object.                                                                                                                            |
| [`Token`](/api/token)   | An individual token — i.e. a word, punctuation symbol, whitespace, etc.                                                                                 |
| [`Lexeme`](/api/lexeme) | An entry in the vocabulary. It's a word type with no context, as opposed to a word token. It therefore has no part-of-speech tag, dependency parse etc. |

### Processing pipeline {#architecture-pipeline}

| Name                                        | Description                                                                                                                   |
| ------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------- |
| [`Language`](/api/language)                 | A text-processing pipeline. Usually you'll load this once per process as `nlp` and pass the instance around your application. |
| [`Tokenizer`](/api/tokenizer)               | Segment text, and create `Doc` objects with the discovered segment boundaries.                                                |
| [`Lemmatizer`](/api/lemmatizer)             | Determine the base forms of words.                                                                                            |
| `Morphology`                                | Assign linguistic features like lemmas, noun case, verb tense etc. based on the word and its part-of-speech tag.              |
| [`Tagger`](/api/tagger)                     | Annotate part-of-speech tags on `Doc` objects.                                                                                |
| [`DependencyParser`](/api/dependencyparser) | Annotate syntactic dependencies on `Doc` objects.                                                                             |
| [`EntityRecognizer`](/api/entityrecognizer) | Annotate named entities, e.g. persons or products, on `Doc` objects.                                                          |
| [`TextCategorizer`](/api/textcategorizer)   | Assign categories or labels to `Doc` objects.                                                                                 |
| [`Matcher`](/api/matcher)                   | Match sequences of tokens, based on pattern rules, similar to regular expressions.                                            |
| [`PhraseMatcher`](/api/phrasematcher)       | Match sequences of tokens based on phrases.                                                                                   |
| [`EntityRuler`](/api/entityruler)           | Add entity spans to the `Doc` using token-based rules or exact phrase matches.                                                |
| [`Sentencizer`](/api/sentencizer)           | Implement custom sentence boundary detection logic that doesn't require the dependency parse.                                 |
| [Other functions](/api/pipeline-functions)  | Automatically apply something to the `Doc`, e.g. to merge spans of tokens.                                                    |

### Other classes {#architecture-other}

| Name                              | Description                                                                                                   |
| --------------------------------- | ------------------------------------------------------------------------------------------------------------- |
| [`Vocab`](/api/vocab)             | A lookup table for the vocabulary that allows you to access `Lexeme` objects.                                 |
| [`StringStore`](/api/stringstore) | Map strings to and from hash values.                                                                          |
| [`Vectors`](/api/vectors)         | Container class for vector data keyed by string.                                                              |
| [`GoldParse`](/api/goldparse)     | Collection for training annotations.                                                                          |
| [`GoldCorpus`](/api/goldcorpus)   | An annotated corpus, using the JSON file format. Manages annotations for tagging, dependency parsing and NER. |
