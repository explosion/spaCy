When you call `nlp` on a text, spaCy first tokenizes the text to produce a `Doc`
object. The `Doc` is then processed in several different steps – this is also
referred to as the **processing pipeline**. The pipeline used by the
[default models](/models) consists of a tagger, a parser and an entity
recognizer. Each pipeline component returns the processed `Doc`, which is then
passed on to the next component.

![The processing pipeline](../../images/pipeline.svg)

> - **Name**: ID of the pipeline component.
> - **Component:** spaCy's implementation of the component.
> - **Creates:** Objects, attributes and properties modified and set by the
>   component.

| Name           | Component                                                          | Creates                                                   | Description                                      |
| -------------- | ------------------------------------------------------------------ | --------------------------------------------------------- | ------------------------------------------------ |
| **tokenizer**  | [`Tokenizer`](/api/tokenizer)                                      | `Doc`                                                     | Segment text into tokens.                        |
| **tagger**     | [`Tagger`](/api/tagger)                                            | `Token.tag`                                               | Assign part-of-speech tags.                      |
| **parser**     | [`DependencyParser`](/api/dependencyparser)                        | `Token.head`, `Token.dep`, `Doc.sents`, `Doc.noun_chunks` | Assign dependency labels.                        |
| **ner**        | [`EntityRecognizer`](/api/entityrecognizer)                        | `Doc.ents`, `Token.ent_iob`, `Token.ent_type`             | Detect and label named entities.                 |
| **lemmatizer** | [`Lemmatizer`](/api/lemmatizer)                                    | `Token.lemma`                                             | Assign base forms.                               |
| **textcat**    | [`TextCategorizer`](/api/textcategorizer)                          | `Doc.cats`                                                | Assign document labels.                          |
| **custom**     | [custom components](/usage/processing-pipelines#custom-components) | `Doc._.xxx`, `Token._.xxx`, `Span._.xxx`                  | Assign custom attributes, methods or properties. |

The processing pipeline always **depends on the statistical model** and its
capabilities. For example, a pipeline can only include an entity recognizer
component if the model includes data to make predictions of entity labels. This
is why each model will specify the pipeline to use in its meta data and
[config](/usage/training#config), as a simple list containing the component
names:

```ini
pipeline = ["tagger", "parser", "ner"]
```

import Accordion from 'components/accordion.js'

<Accordion title="Does the order of pipeline components matter?" id="pipeline-components-order">

The statistical components like the tagger or parser are typically independent
and don't share any data between each other. For example, the named entity
recognizer doesn't use any features set by the tagger and parser, and so on.
This means that you can swap them, or remove single components from the pipeline
without affecting the others. However, components may share a "token-to-vector"
component like [`Tok2Vec`](/api/tok2vec) or [`Transformer`](/api/transformer).

Custom components may also depend on annotations set by other components. For
example, a custom lemmatizer may need the part-of-speech tags assigned, so it'll
only work if it's added after the tagger. The parser will respect pre-defined
sentence boundaries, so if a previous component in the pipeline sets them, its
dependency predictions may be different. Similarly, it matters if you add the
[`EntityRuler`](/api/entityruler) before or after the statistical entity
recognizer: if it's added before, the entity recognizer will take the existing
entities into account when making predictions. The
[`EntityLinker`](/api/entitylinker), which resolves named entities to knowledge
base IDs, should be preceded by a pipeline component that recognizes entities
such as the [`EntityRecognizer`](/api/entityrecognizer).

</Accordion>

<Accordion title="Why is the tokenizer special?" id="pipeline-components-tokenizer">

The tokenizer is a "special" component and isn't part of the regular pipeline.
It also doesn't show up in `nlp.pipe_names`. The reason is that there can only
really be one tokenizer, and while all other pipeline components take a `Doc`
and return it, the tokenizer takes a **string of text** and turns it into a
`Doc`. You can still customize the tokenizer, though. `nlp.tokenizer` is
writable, so you can either create your own
[`Tokenizer` class from scratch](/usage/linguistic-features#native-tokenizers),
or even replace it with an
[entirely custom function](/usage/linguistic-features#custom-tokenizer).

</Accordion>

---
