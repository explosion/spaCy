---
title: Transformers
teaser: Using transformer models like BERT in spaCy
---

spaCy v3.0 lets you use almost **any statistical model** to power your pipeline.
You can use models implemented in a variety of frameworks, including TensorFlow,
PyTorch and MXNet. To keep things sane, spaCy expects models from these
frameworks to be wrapped with a common interface, using our machine learning
library [Thinc](https://thinc.ai). A transformer model is just a statistical
model, so the
[`spacy-transformers`](https://github.com/explosion/spacy-transformers) package
actually has very little work to do: we just have to provide a few functions
that do the required plumbing. We also provide a pipeline component,
[`Transformer`](/api/transformer), that lets you do multi-task learning and lets
you save the transformer outputs for later use.

<Project id="en_core_bert">

Try out a BERT-based model pipeline using this project template: swap in your
data, edit the settings and hyperparameters and train, evaluate, package and
visualize your model.

</Project>

<!-- TODO: the text below has been copied from the spacy-transformers repo and needs to be updated and adjusted

### Training usage

The recommended workflow for training is to use spaCy's
[config system](/usage/training#config), usually via the
[`spacy train`](/api/cli#train) command. The config system lets you describe a
tree of objects by referring to creation functions, including functions you
register yourself. Here's a config snippet for the `Transformer` component,
along with matching Python code.

```ini
[nlp]
lang = "en"
pipeline = ["transformer"]

[components.transformer]
factory = "transformer"
extra_annotation_setter = null
max_batch_size = 32

[components.transformer.model]
@architectures = "spacy-transformers.TransformerModel.v1"
name = "bert-base-cased"
tokenizer_config = {"use_fast": true}

[components.transformer.model.get_spans]
@span_getters = "get_doc_spans.v1"
```

```python
from spacy_transformers import Transformer

trf = Transformer(
    nlp.vocab,
    TransformerModel(
        "bert-base-cased",
        get_spans=get_doc_spans,
        tokenizer_config={"use_fast": True},
    ),
    annotation_setter=null_annotation_setter,
    max_batch_size=32,
)
```

The `components.transformer` block adds the `transformer` component to the
pipeline, and the `components.transformer.model` block describes the creation of
a Thinc [`Model`](https://thinc.ai/docs/api-model) object that will be passed
into the component. The block names a function registered in the
`@architectures` registry. This function will be looked up and called using the
provided arguments. You're not limited to just that function --- you can write
your own or use someone else's. The only limitation is that it must return an
object of type `Model[List[Doc], FullTransformerBatch]`: that is, a Thinc model
that takes a list of `Doc` objects, and returns a `FullTransformerBatch` object
with the transformer data.

The same idea applies to task models that power the downstream components. Most
of spaCy's built-in model creation functions support a `tok2vec` argument, which
should be a Thinc layer of type `Model[List[Doc], List[Floats2d]]`. This is
where we'll plug in our transformer model, using the `Tok2VecTransformer` layer,
which sneakily delegates to the `Transformer` pipeline component.

```ini
[nlp]
lang = "en"
pipeline = ["ner"]

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

The `Tok2VecListener` layer expects a `pooling` layer, which needs to be of type
`Model[Ragged, Floats2d]`. This layer determines how the vector for each spaCy
token will be computed from the zero or more source rows the token is aligned
against. Here we use the `reduce_mean` layer, which averages the wordpiece rows.
We could instead use `reduce_last`, `reduce_max`, or a custom function you write
yourself.

You can have multiple components all listening to the same transformer model,
and all passing gradients back to it. By default, all of the gradients will be
equally weighted. You can control this with the `grad_factor` setting, which
lets you reweight the gradients from the different listeners. For instance,
setting `grad_factor = 0` would disable gradients from one of the listeners,
while `grad_factor = 2.0` would multiply them by 2. This is similar to having a
custom learning rate for each component. Instead of a constant, you can also
provide a schedule, allowing you to freeze the shared parameters at the start of
training.

### Runtime usage

Transformer models can be used as drop-in replacements for other types of neural
networks, so your spaCy pipeline can include them in a way that's completely
invisible to the user. Users will download, load and use the model in the
standard way, like any other spaCy pipeline.

Instead of using the transformers as subnetworks directly, you can also use them
via the [`Transformer`](/api/transformer) pipeline component. This sets the
[`Doc._.trf_data`](/api/transformer#custom_attributes) extension attribute,
which lets you access the transformers outputs at runtime via the
`doc._.trf_data` extension attribute. You can also customize how the
`Transformer` object sets annotations onto the `Doc`, by customizing the
`Transformer.annotation_setter` object. This callback will be called with the
raw input and output data for the whole batch, along with the batch of `Doc`
objects, allowing you to implement whatever you need.

```python
import spacy

nlp = spacy.load("en_core_trf_lg")
for doc in nlp.pipe(["some text", "some other text"]):
    doc._.trf_data.tensors
    tokvecs = doc._.trf_data.tensors[-1]
```

The `nlp` object in this example is just like any other spaCy pipeline

 -->
