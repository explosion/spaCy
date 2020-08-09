---
title: Transformers
teaser: Using transformer models like BERT in spaCy
menu:
  - ['Installation', 'install']
  - ['Runtime Usage', 'runtime']
  - ['Training Usage', 'training']
next: /usage/training
---

## Installation {#install hidden="true"}

spaCy v3.0 lets you use almost **any statistical model** to power your pipeline.
You can use models implemented in a variety of
[frameworks](https://thinc.ai/docs/usage-frameworks), including TensorFlow,
PyTorch and MXNet. To keep things sane, spaCy expects models from these
frameworks to be wrapped with a common interface, using our machine learning
library [Thinc](https://thinc.ai). A transformer model is just a statistical
model, so the
[`spacy-transformers`](https://github.com/explosion/spacy-transformers) package
actually has very little work to do: it just has to provide a few functions that
do the required plumbing. It also provides a pipeline component,
[`Transformer`](/api/transformer), that lets you do multi-task learning and lets
you save the transformer outputs for later use.

To use transformers with spaCy, you need the
[`spacy-transformers`](https://github.com/explosion/spacy-transformers) package
installed. It takes care of all the setup behind the scenes, and makes sure the
transformer pipeline component is available to spaCy.

```bash
$ pip install spacy-transformers
```

## Runtime usage {#runtime}

Transformer models can be used as **drop-in replacements** for other types of
neural networks, so your spaCy pipeline can include them in a way that's
completely invisible to the user. Users will download, load and use the model in
the standard way, like any other spaCy pipeline. Instead of using the
transformers as subnetworks directly, you can also use them via the
[`Transformer`](/api/transformer) pipeline component.

![The processing pipeline with the transformer component](../images/pipeline_transformer.svg)

The `Transformer` component sets the
[`Doc._.trf_data`](/api/transformer#custom_attributes) extension attribute,
which lets you access the transformers outputs at runtime.

```bash
$ python -m spacy download en_core_trf_lg
```

```python
### Example
import spacy

nlp = spacy.load("en_core_trf_lg")
for doc in nlp.pipe(["some text", "some other text"]):
    tokvecs = doc._.trf_data.tensors[-1]
```

You can also customize how the [`Transformer`](/api/transformer) component sets
annotations onto the [`Doc`](/api/doc), by customizing the `annotation_setter`.
This callback will be called with the raw input and output data for the whole
batch, along with the batch of `Doc` objects, allowing you to implement whatever
you need. The annotation setter is called with a batch of [`Doc`](/api/doc)
objects and a [`FullTransformerBatch`](/api/transformer#fulltransformerbatch)
containing the transformers data for the batch.

```python
def custom_annotation_setter(docs, trf_data):
    # TODO:
    ...

nlp = spacy.load("en_core_trf_lg")
nlp.get_pipe("transformer").annotation_setter = custom_annotation_setter
doc = nlp("This is a text")
print()  # TODO:
```

## Training usage {#training}

The recommended workflow for training is to use spaCy's
[config system](/usage/training#config), usually via the
[`spacy train`](/api/cli#train) command. The training config defines all
component settings and hyperparameters in one place and lets you describe a tree
of objects by referring to creation functions, including functions you register
yourself. For details on how to get started with training your own model, check
out the [training quickstart](/usage/training#quickstart).

<Project id="en_core_bert">

The easiest way to get started is to clone a transformers-based project
template. Swap in your data, edit the settings and hyperparameters and train,
evaluate, package and visualize your model.

</Project>

The `[components]` section in the [`config.cfg`](/api/data-formats#config)
describes the pipeline components and the settings used to construct them,
including their model implementation. Here's a config snippet for the
[`Transformer`](/api/transformer) component, along with matching Python code. In
this case, the `[components.transformer]` block describes the `transformer`
component:

> #### Python equivalent
>
> ```python
> from spacy_transformers import Transformer, TransformerModel
> from spacy_transformers.annotation_setters import null_annotation_setter
> from spacy_transformers.span_getters import get_doc_spans
>
> trf = Transformer(
>     nlp.vocab,
>     TransformerModel(
>         "bert-base-cased",
>         get_spans=get_doc_spans,
>         tokenizer_config={"use_fast": True},
>     ),
>     annotation_setter=null_annotation_setter,
>     max_batch_items=4096,
> )
> ```

```ini
### config.cfg (excerpt)
[components.transformer]
factory = "transformer"
max_batch_items = 4096

[components.transformer.model]
@architectures = "spacy-transformers.TransformerModel.v1"
name = "bert-base-cased"
tokenizer_config = {"use_fast": true}

[components.transformer.model.get_spans]
@span_getters = "doc_spans.v1"

[components.transformer.annotation_setter]
@annotation_setters = "spacy-transformer.null_annotation_setter.v1"

```

The `[components.transformer.model]` block describes the `model` argument passed
to the transformer component. It's a Thinc
[`Model`](https://thinc.ai/docs/api-model) object that will be passed into the
component. Here, it references the function
[spacy-transformers.TransformerModel.v1](/api/architectures#TransformerModel)
registered in the [`architectures` registry](/api/top-level#registry). If a key
in a block starts with `@`, it's **resolved to a function** and all other
settings are passed to the function as arguments. In this case, `name`,
`tokenizer_config` and `get_spans`.

`get_spans` is a function that takes a batch of `Doc` object and returns lists
of potentially overlapping `Span` objects to process by the transformer. Several
[built-in functions](/api/transformer#span-getters) are available – for example,
to process the whole document or individual sentences. When the config is
resolved, the function is created and passed into the model as an argument.

<Infobox variant="warning">

Remember that the `config.cfg` used for training should contain **no missing
values** and requires all settings to be defined. You don't want any hidden
defaults creeping in and changing your results! spaCy will tell you if settings
are missing, and you can run [`spacy init config`](/api/cli#init-config) with to
automatically fill in all defaults.

</Infobox>

### Customizing the settings {#training-custom-settings}

To change any of the settings, you can edit the `config.cfg` and re-run the
training. To change any of the functions, like the span getter, you can replace
the name of the referenced function – e.g. `@span_getters = "sent_spans.v1"` to
process sentences. You can also register your own functions using the
`span_getters` registry:

> #### config.cfg
>
> ```ini
> [components.transformer.model.get_spans]
> @span_getters = "custom_sent_spans"
> ```

```python
### code.py
import spacy_transformers

@spacy_transformers.registry.span_getters("custom_sent_spans")
def configure_custom_sent_spans():
    # TODO: write custom example
    def get_sent_spans(docs):
        return [list(doc.sents) for doc in docs]

    return get_sent_spans
```

To resolve the config during training, spaCy needs to know about your custom
function. You can make it available via the `--code` argument that can point to
a Python file. For more details on training with custom code, see the
[training documentation](/usage/training#custom-code).

```bash
$ python -m spacy train ./config.cfg --code ./code.py
```

### Customizing the model implementations {#training-custom-model}

The [`Transformer`](/api/transformer) component expects a Thinc
[`Model`](https://thinc.ai/docs/api-model) object to be passed in as its `model`
argument. You're not limited to the implementation provided by
`spacy-transformers` – the only requirement is that your registered function
must return an object of type `Model[List[Doc], FullTransformerBatch]`: that is,
a Thinc model that takes a list of [`Doc`](/api/doc) objects, and returns a
[`FullTransformerBatch`](/api/transformer#fulltransformerbatch) object with the
transformer data.

> #### Model type annotations
>
> In the documentation and code base, you may come across type annotations and
> descriptions of [Thinc](https://thinc.ai) model types, like
> `Model[List[Doc], List[Floats2d]]`. This so-called generic type describes the
> layer and its input and output type – in this case, it takes a list of `Doc`
> objects as the input and list of 2-dimensional arrays of floats as the output.
> You can read more about defining Thinc
> models [here](https://thinc.ai/docs/usage-models). Also see the
> [type checking](https://thinc.ai/docs/usage-type-checking) for how to enable
> linting in your editor to see live feedback if your inputs and outputs don't
> match.

The same idea applies to task models that power the **downstream components**.
Most of spaCy's built-in model creation functions support a `tok2vec` argument,
which should be a Thinc layer of type `Model[List[Doc], List[Floats2d]]`. This
is where we'll plug in our transformer model, using the
[Tok2VecListener](/api/architectures#Tok2VecListener) layer, which sneakily
delegates to the `Transformer` pipeline component.

```ini
### config.cfg (excerpt) {highlight="12"}
[components.ner]
factory = "ner"

[nlp.pipeline.ner.model]
@architectures = "spacy.TransitionBasedParser.v1"
nr_feature_tokens = 3
hidden_width = 128
maxout_pieces = 3
use_upper = false

[nlp.pipeline.ner.model.tok2vec]
@architectures = "spacy-transformers.Tok2VecListener.v1"
grad_factor = 1.0

[nlp.pipeline.ner.model.tok2vec.pooling]
@layers = "reduce_mean.v1"
```

The [Tok2VecListener](/api/architectures#Tok2VecListener) layer expects a
[pooling layer](https://thinc.ai/docs/api-layers#reduction-ops) as the argument
`pooling`, which needs to be of type `Model[Ragged, Floats2d]`. This layer
determines how the vector for each spaCy token will be computed from the zero or
more source rows the token is aligned against. Here we use the
[`reduce_mean`](https://thinc.ai/docs/api-layers#reduce_mean) layer, which
averages the wordpiece rows. We could instead use `reduce_last`,
[`reduce_max`](https://thinc.ai/docs/api-layers#reduce_max), or a custom
function you write yourself.

<!--TODO: reduce_last: undocumented? -->

You can have multiple components all listening to the same transformer model,
and all passing gradients back to it. By default, all of the gradients will be
**equally weighted**. You can control this with the `grad_factor` setting, which
lets you reweight the gradients from the different listeners. For instance,
setting `grad_factor = 0` would disable gradients from one of the listeners,
while `grad_factor = 2.0` would multiply them by 2. This is similar to having a
custom learning rate for each component. Instead of a constant, you can also
provide a schedule, allowing you to freeze the shared parameters at the start of
training.
