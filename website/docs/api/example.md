---
title: Example
teaser: A training instance
tag: class
source: spacy/gold/example.pyx
new: 3.0
---

An `Example` holds the information for one training instance. It stores two
`Doc` objects: one for holding the gold-standard reference data, and one for
holding the predictions of the pipeline. An [`Alignment`](#alignment-object)
object stores the alignment between these two documents, as they can differ in
tokenization.

## Example.\_\_init\_\_ {#init tag="method"}

Construct an `Example` object from the `predicted` document and the `reference`
document. If `alignment` is `None`, it will be initialized from the words in
both documents.

> #### Example
>
> ```python
> from spacy.tokens import Doc
> from spacy.gold import Example
>
> words = ["hello", "world", "!"]
> spaces = [True, False, False]
> predicted = Doc(nlp.vocab, words=words, spaces=spaces)
> reference = parse_gold_doc(my_data)
> example = Example(predicted, reference)
> ```

| Name           | Type        | Description                                                                                      |
| -------------- | ----------- | ------------------------------------------------------------------------------------------------ |
| `predicted`    | `Doc`       | The document containing (partial) predictions. Can not be `None`.                                |
| `reference`    | `Doc`       | The document containing gold-standard annotations. Can not be `None`.                            |
| _keyword-only_ |             |                                                                                                  |
| `alignment`    | `Alignment` | An object holding the alignment between the tokens of the `predicted` and `reference` documents. |

## Example.from_dict {#from_dict tag="classmethod"}

Construct an `Example` object from the `predicted` document and the reference
annotations provided as a dictionary. For more details on the required format,
see the [training format documentation](/api/data-formats#dict-input).

> #### Example
>
> ```python
> from spacy.tokens import Doc
> from spacy.gold import Example
>
> predicted = Doc(vocab, words=["Apply", "some", "sunscreen"])
> token_ref = ["Apply", "some", "sun", "screen"]
> tags_ref = ["VERB", "DET", "NOUN", "NOUN"]
> example = Example.from_dict(predicted, {"words": token_ref, "tags": tags_ref})
> ```

| Name           | Type             | Description                                                       |
| -------------- | ---------------- | ----------------------------------------------------------------- |
| `predicted`    | `Doc`            | The document containing (partial) predictions. Can not be `None`. |
| `example_dict` | `Dict[str, obj]` | The gold-standard annotations as a dictionary. Can not be `None`. |
| **RETURNS**    | `Example`        | The newly constructed object.                                     |

## Example.text {#text tag="property"}

The text of the `predicted` document in this `Example`.

> #### Example
>
> ```python
> raw_text = example.text
> ```

| Name        | Type | Description                           |
| ----------- | ---- | ------------------------------------- |
| **RETURNS** | str  | The text of the `predicted` document. |

## Example.predicted {#predicted tag="property"}

> #### Example
>
> ```python
> docs = [eg.predicted for eg in examples]
> predictions, _ = model.begin_update(docs)
> set_annotations(docs, predictions)
> ```

The `Doc` holding the predictions. Occassionally also refered to as `example.x`.

| Name        | Type  | Description                                    |
| ----------- | ----- | ---------------------------------------------- |
| **RETURNS** | `Doc` | The document containing (partial) predictions. |

## Example.reference {#reference tag="property"}

> #### Example
>
> ```python
> for i, eg in enumerate(examples):
>     for j, label in enumerate(all_labels):
>         gold_labels[i][j] = eg.reference.cats.get(label, 0.0)
> ```

The `Doc` holding the gold-standard annotations. Occassionally also refered to
as `example.y`.

| Name        | Type  | Description                                        |
| ----------- | ----- | -------------------------------------------------- |
| **RETURNS** | `Doc` | The document containing gold-standard annotations. |

## Example.alignment {#alignment tag="property"}

> #### Example
>
> ```python
> tokens_x = ["Apply", "some", "sunscreen"]
> x = Doc(vocab, words=tokens_x)
> tokens_y = ["Apply", "some", "sun", "screen"]
> example = Example.from_dict(x, {"words": tokens_y})
> alignment = example.alignment
> assert list(alignment.y2x.data) == [[0], [1], [2], [2]]
> ```

The `Alignment` object mapping the tokens of the `predicted` document to those
of the `reference` document.

| Name        | Type        | Description                                        |
| ----------- | ----------- | -------------------------------------------------- |
| **RETURNS** | `Alignment` | The document containing gold-standard annotations. |

## Example.get_aligned {#get_aligned tag="method"}

> #### Example
>
> ```python
> predicted = Doc(vocab, words=["Apply", "some", "sunscreen"])
> token_ref = ["Apply", "some", "sun", "screen"]
> tags_ref = ["VERB", "DET", "NOUN", "NOUN"]
> example = Example.from_dict(predicted, {"words": token_ref, "tags": tags_ref})
> assert example.get_aligned("TAG", as_string=True) == ["VERB", "DET", "NOUN"]
> ```

Get the aligned view of a certain token attribute, denoted by its int ID or
string name.

| Name        | Type                       | Description                                                        | Default |
| ----------- | -------------------------- | ------------------------------------------------------------------ | ------- |
| `field`     | int or str                 | Attribute ID or string name                                        |         |
| `as_string` | bool                       | Whether or not to return the list of values as strings.            | `False` |
| **RETURNS** | `List[int]` or `List[str]` | List of integer values, or string values if `as_string` is `True`. |         |

## Example.get_aligned_parse {#get_aligned_parse tag="method"}

> #### Example
>
> ```python
> doc = nlp("He pretty quickly walks away")
> example = Example.from_dict(doc, {"heads": [3, 2, 3, 0, 2]})
> proj_heads, proj_labels = example.get_aligned_parse(projectivize=True)
> assert proj_heads == [3, 2, 3, 0, 3]
> ```

Get the aligned view of the dependency parse. If `projectivize` is set to
`True`, non-projective dependency trees are made projective through the
Pseudo-Projective Dependency Parsing algorithm by Nivre and Nilsson (2005).

| Name           | Type                       | Description                                                        | Default |
| -------------- | -------------------------- | ------------------------------------------------------------------ | ------- |
| `projectivize` | bool                       | Whether or not to projectivize the dependency trees                | `True`  |
| **RETURNS**    | `List[int]` or `List[str]` | List of integer values, or string values if `as_string` is `True`. |         |

## Example.get_aligned_ner {#get_aligned_ner tag="method"}

> #### Example
>
> ```python
> words = ["Mrs", "Smith", "flew", "to", "New York"]
> doc = Doc(en_vocab, words=words)
> entities = [(0, 9, "PERSON"), (18, 26, "LOC")]
> gold_words = ["Mrs Smith", "flew", "to", "New", "York"]
> example = Example.from_dict(doc, {"words": gold_words, "entities": entities})
> ner_tags = example.get_aligned_ner()
> assert ner_tags == ["B-PERSON", "L-PERSON", "O", "O", "U-LOC"]
> ```

Get the aligned view of the NER
[BILUO](/usage/linguistic-features#accessing-ner) tags.

| Name        | Type        | Description                                                                         |
| ----------- | ----------- | ----------------------------------------------------------------------------------- |
| **RETURNS** | `List[str]` | List of BILUO values, denoting whether tokens are part of an NER annotation or not. |

## Example.get_aligned_spans_y2x {#get_aligned_spans_y2x tag="method"}

> #### Example
>
> ```python
> words = ["Mr and Mrs Smith", "flew", "to", "New York"]
> doc = Doc(en_vocab, words=words)
> entities = [(0, 16, "PERSON")]
> tokens_ref = ["Mr", "and", "Mrs", "Smith", "flew", "to", "New", "York"]
> example = Example.from_dict(doc, {"words": tokens_ref, "entities": entities})
> ents_ref = example.reference.ents
> assert [(ent.start, ent.end) for ent in ents_ref] == [(0, 4)]
> ents_y2x = example.get_aligned_spans_y2x(ents_ref)
> assert [(ent.start, ent.end) for ent in ents_y2x] == [(0, 1)]
> ```

Get the aligned view of any set of [`Span`](/api/span) objects defined over
`example.reference`. The resulting span indices will align to the tokenization
in `example.predicted`.

| Name        | Type             | Description                                                     |
| ----------- | ---------------- | --------------------------------------------------------------- |
| `y_spans`   | `Iterable[Span]` | `Span` objects aligned to the tokenization of `self.reference`. |
| **RETURNS** | `Iterable[Span]` | `Span` objects aligned to the tokenization of `self.predicted`. |

## Example.get_aligned_spans_x2y {#get_aligned_spans_x2y tag="method"}

> #### Example
>
> ```python
> nlp.add_pipe("my_ner")
> doc = nlp("Mr and Mrs Smith flew to New York")
> tokens_ref = ["Mr and Mrs", "Smith", "flew", "to", "New York"]
> example = Example.from_dict(doc, {"words": tokens_ref})
> ents_pred = example.predicted.ents
> # Assume the NER model has found "Mr and Mrs Smith" as a named entity
> assert [(ent.start, ent.end) for ent in ents_pred] == [(0, 4)]
> ents_x2y = example.get_aligned_spans_x2y(ents_pred)
> assert [(ent.start, ent.end) for ent in ents_x2y] == [(0, 2)]
> ```

Get the aligned view of any set of [`Span`](/api/span) objects defined over
`example.predicted`. The resulting span indices will align to the tokenization
in `example.reference`. This method is particularly useful to assess the
accuracy of predicted entities against the original gold-standard annotation.

| Name        | Type             | Description                                                     |
| ----------- | ---------------- | --------------------------------------------------------------- |
| `x_spans`   | `Iterable[Span]` | `Span` objects aligned to the tokenization of `self.predicted`. |
| **RETURNS** | `Iterable[Span]` | `Span` objects aligned to the tokenization of `self.reference`. |

## Example.to_dict {#to_dict tag="method"}

Return a [dictionary representation](/api/data-formats#dict-input) of the
reference annotation contained in this `Example`.

> #### Example
>
> ```python
> eg_dict = example.to_dict()
> ```

| Name        | Type             | Description                                            |
| ----------- | ---------------- | ------------------------------------------------------ |
| **RETURNS** | `Dict[str, Any]` | Dictionary representation of the reference annotation. |

## Example.split_sents {#split_sents tag="method"}

> #### Example
>
> ```python
> doc = nlp("I went yesterday had lots of fun")
> tokens_ref = ["I", "went", "yesterday", "had", "lots", "of", "fun"]
> sents_ref = [True, False, False, True, False, False, False]
> example = Example.from_dict(doc, {"words": tokens_ref, "sent_starts": sents_ref})
> split_examples = example.split_sents()
> assert split_examples[0].text == "I went yesterday "
> assert split_examples[1].text == "had lots of fun"
> ```

Split one `Example` into multiple `Example` objects, one for each sentence.

| Name        | Type            | Description                                                |
| ----------- | --------------- | ---------------------------------------------------------- |
| **RETURNS** | `List[Example]` | List of `Example` objects, one for each original sentence. |

## Alignment {#alignment-object new="3"}

Calculate alignment tables between two tokenizations.

### Alignment attributes {#alignment-attributes"}

| Name  | Type                                               | Description                                                |
| ----- | -------------------------------------------------- | ---------------------------------------------------------- |
| `x2y` | [`Ragged`](https://thinc.ai/docs/api-types#ragged) | The `Ragged` object holding the alignment from `x` to `y`. |
| `y2x` | [`Ragged`](https://thinc.ai/docs/api-types#ragged) | The `Ragged` object holding the alignment from `y` to `x`. |

<Infobox title="Important note" variant="warning">

The current implementation of the alignment algorithm assumes that both
tokenizations add up to the same string. For example, you'll be able to align
`["I", "'", "m"]` and `["I", "'m"]`, which both add up to `"I'm"`, but not
`["I", "'m"]` and `["I", "am"]`.

</Infobox>

> #### Example
>
> ```python
> from spacy.gold import Alignment
>
> bert_tokens = ["obama", "'", "s", "podcast"]
> spacy_tokens = ["obama", "'s", "podcast"]
> alignment = Alignment.from_strings(bert_tokens, spacy_tokens)
> a2b = alignment.x2y
> assert list(a2b.dataXd) == [0, 1, 1, 2]
> ```
>
> If `a2b.dataXd[1] == a2b.dataXd[2] == 1`, that means that `A[1]` (`"'"`) and
> `A[2]` (`"s"`) both align to `B[1]` (`"'s"`).

### Alignment.from_strings {#classmethod tag="function"}

| Name        | Type        | Description                                     |
| ----------- | ----------- | ----------------------------------------------- |
| `A`         | list        | String values of candidate tokens to align.     |
| `B`         | list        | String values of reference tokens to align.     |
| **RETURNS** | `Alignment` | An `Alignment` object describing the alignment. |
