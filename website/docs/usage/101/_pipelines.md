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

| Name          | Component                                                          | Creates                                                     | Description                                      |
| ------------- | ------------------------------------------------------------------ | ----------------------------------------------------------- | ------------------------------------------------ |
| **tokenizer** | [`Tokenizer`](/api/tokenizer)                                      | `Doc`                                                       | Segment text into tokens.                        |
| **tagger**    | [`Tagger`](/api/tagger)                                            | `Doc[i].tag`                                                | Assign part-of-speech tags.                      |
| **parser**    | [`DependencyParser`](/api/dependencyparser)                        | `Doc[i].head`, `Doc[i].dep`, `Doc.sents`, `Doc.noun_chunks` | Assign dependency labels.                        |
| **ner**       | [`EntityRecognizer`](/api/entityrecognizer)                        | `Doc.ents`, `Doc[i].ent_iob`, `Doc[i].ent_type`             | Detect and label named entities.                 |
| **textcat**   | [`TextCategorizer`](/api/textcategorizer)                          | `Doc.cats`                                                  | Assign document labels.                          |
| ...           | [custom components](/usage/processing-pipelines#custom-components) | `Doc._.xxx`, `Token._.xxx`, `Span._.xxx`                    | Assign custom attributes, methods or properties. |

The processing pipeline always **depends on the statistical model** and its
capabilities. For example, a pipeline can only include an entity recognizer
component if the model includes data to make predictions of entity labels. This
is why each model will specify the pipeline to use in its meta data, as a simple
list containing the component names:

```json
"pipeline": ["tagger", "parser", "ner"]
```

import Accordion from 'components/accordion.js'

<Accordion title="Does the order of pipeline components matter?" id="pipeline-components-order">

In spaCy v2.x, the statistical components like the tagger or parser are
independent and don't share any data between themselves. For example, the named
entity recognizer doesn't use any features set by the tagger and parser, and so
on. This means that you can swap them, or remove single components from the
pipeline without affecting the others.

However, custom components may depend on annotations set by other components.
For example, a custom lemmatizer may need the part-of-speech tags assigned, so
it'll only work if it's added after the tagger. The parser will respect
pre-defined sentence boundaries, so if a previous component in the pipeline sets
them, its dependency predictions may be different. Similarly, it matters if you
add the [`EntityRuler`](/api/entityruler) before or after the statistical entity
recognizer: if it's added before, the entity recognizer will take the existing
entities into account when making predictions.

</Accordion>

---
