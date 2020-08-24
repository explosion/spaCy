---
title: Embeddings, Transformers and Transfer Learning
teaser: Using transformer embeddings like BERT in spaCy
menu:
  - ['Embedding Layers', 'embedding-layers']
  - ['Transformers', 'transformers']
  - ['Static Vectors', 'static-vectors']
  - ['Pretraining', 'pretraining']
next: /usage/training
---

spaCy supports a number of **transfer and multi-task learning** workflows that
can often help improve your pipeline's efficiency or accuracy. Transfer learning
refers to techniques such as word vector tables and language model pretraining.
These techniques can be used to import knowledge from raw text into your
pipeline, so that your models are able to generalize better from your annotated
examples.

You can convert **word vectors** from popular tools like
[FastText](https://fasttext.cc) and [Gensim](https://radimrehurek.com/gensim),
or you can load in any pretrained **transformer model** if you install
[`spacy-transformers`](https://github.com/explosion/spacy-transformers). You can
also do your own language model pretraining via the
[`spacy pretrain`](/api/cli#pretrain) command. You can even **share** your
transformer or other contextual embedding model across multiple components,
which can make long pipelines several times more efficient. To use transfer
learning, you'll need at least a few annotated examples for what you're trying
to predict. Otherwise, you could try using a "one-shot learning" approach using
[vectors and similarity](/usage/linguistic-features#vectors-similarity).

<Accordion title="What’s the difference between word vectors and language models?" id="vectors-vs-language-models">

The key difference between [word vectors](#word-vectors) and contextual language
models such as [transformers](#transformers) is that word vectors model
**lexical types**, rather than _tokens_. If you have a list of terms with no
context around them, a transformer model like BERT can't really help you. BERT
is designed to understand language **in context**, which isn't what you have. A
word vectors table will be a much better fit for your task. However, if you do
have words in context — whole sentences or paragraphs of running text — word
vectors will only provide a very rough approximation of what the text is about.

Word vectors are also very computationally efficient, as they map a word to a
vector with a single indexing operation. Word vectors are therefore useful as a
way to **improve the accuracy** of neural network models, especially models that
are small or have received little or no pretraining. In spaCy, word vector
tables are only used as **static features**. spaCy does not backpropagate
gradients to the pretrained word vectors table. The static vectors table is
usually used in combination with a smaller table of learned task-specific
embeddings.

</Accordion>

<Accordion title="When should I add word vectors to my model?">

Word vectors are not compatible with most [transformer models](#transformers),
but if you're training another type of NLP network, it's almost always worth
adding word vectors to your model. As well as improving your final accuracy,
word vectors often make experiments more consistent, as the accuracy you reach
will be less sensitive to how the network is randomly initialized. High variance
due to random chance can slow down your progress significantly, as you need to
run many experiments to filter the signal from the noise.

Word vector features need to be enabled prior to training, and the same word
vectors table will need to be available at runtime as well. You cannot add word
vector features once the model has already been trained, and you usually cannot
replace one word vectors table with another without causing a significant loss
of performance.

</Accordion>

## Shared embedding layers {#embedding-layers}

spaCy lets you share a single transformer or other token-to-vector ("tok2vec")
embedding layer between multiple components. You can even update the shared
layer, performing **multi-task learning**. Reusing the tok2vec layer between
components can make your pipeline run a lot faster and result in much smaller
models. However, it can make the pipeline less modular and make it more
difficult to swap components or retrain parts of the pipeline. Multi-task
learning can affect your accuracy (either positively or negatively), and may
require some retuning of your hyper-parameters.

![Pipeline components using a shared embedding component vs. independent embedding layers](../images/tok2vec.svg)

| Shared                                                                                      | Independent                                                             |
| ------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------- |
| ✅ **smaller:** models only need to include a single copy of the embeddings                 | ❌ **larger:** models need to include the embeddings for each component |
| ✅ **faster:** embed the documents once for your whole pipeline                             | ❌ **slower:** rerun the embedding for each component                   |
| ❌ **less composable:** all components require the same embedding component in the pipeline | ✅ **modular:** components can be moved and swapped freely              |

You can share a single transformer or other tok2vec model between multiple
components by adding a [`Transformer`](/api/transformer) or
[`Tok2Vec`](/api/tok2vec) component near the start of your pipeline. Components
later in the pipeline can "connect" to it by including a **listener layer** like
[Tok2VecListener](/api/architectures#Tok2VecListener) within their model.

![Pipeline components listening to shared embedding component](../images/tok2vec-listener.svg)

At the beginning of training, the [`Tok2Vec`](/api/tok2vec) component will grab
a reference to the relevant listener layers in the rest of your pipeline. When
it processes a batch of documents, it will pass forward its predictions to the
listeners, allowing the listeners to **reuse the predictions** when they are
eventually called. A similar mechanism is used to pass gradients from the
listeners back to the model. The [`Transformer`](/api/transformer) component and
[TransformerListener](/api/architectures#TransformerListener) layer do the same
thing for transformer models, but the `Transformer` component will also save the
transformer outputs to the
[`Doc._.trf_data`](/api/transformer#custom_attributes) extension attribute,
giving you access to them after the pipeline has finished running.

<!-- TODO: show example of implementation via config, side by side -->

<!-- TODO: Once rehearsal is tested, mention it here. -->

## Using transformer models {#transformers}

Transformers are a family of neural network architectures that compute **dense,
context-sensitive representations** for the tokens in your documents. Downstream
models in your pipeline can then use these representations as input features to
**improve their predictions**. You can connect multiple components to a single
transformer model, with any or all of those components giving feedback to the
transformer to fine-tune it to your tasks. spaCy's transformer support
interoperates with [PyTorch](https://pytorch.org) and the
[HuggingFace `transformers`](https://huggingface.co/transformers/) library,
giving you access to thousands of pretrained models for your pipelines. There
are many [great guides](http://jalammar.github.io/illustrated-transformer/) to
transformer models, but for practical purposes, you can simply think of them as
a drop-in replacement that let you achieve **higher accuracy** in exchange for
**higher training and runtime costs**.

### Setup and installation {#transformers-installation}

> #### System requirements
>
> We recommend an NVIDIA **GPU** with at least **10GB of memory** in order to
> work with transformer models. Make sure your GPU drivers are up to date and
> you have **CUDA v9+** installed.

> The exact requirements will depend on the transformer model. Training a
> transformer-based model without a GPU will be too slow for most practical
> purposes.
>
> Provisioning a new machine will require about **5GB** of data to be
> downloaded: 3GB CUDA runtime, 800MB PyTorch, 400MB CuPy, 500MB weights, 200MB
> spaCy and dependencies.

Once you have CUDA installed, you'll need to install two pip packages,
[`cupy`](https://docs.cupy.dev/en/stable/install.html) and
[`spacy-transformers`](https://github.com/explosion/spacy-transformers). `cupy`
is just like `numpy`, but for GPU. The best way to install it is to choose a
wheel that matches the version of CUDA you're using. You may also need to set
the `CUDA_PATH` environment variable if your CUDA runtime is installed in a
non-standard location. Putting it all together, if you had installed CUDA 10.2
in `/opt/nvidia/cuda`, you would run:

```bash
### Installation with CUDA
$ export CUDA_PATH="/opt/nvidia/cuda"
$ pip install cupy-cuda102
$ pip install spacy-transformers
```

### Runtime usage {#transformers-runtime}

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

```cli
$ python -m spacy download en_core_trf_lg
```

```python
### Example
import spacy
from thinc.api import use_pytorch_for_gpu_memory, require_gpu

# Use the GPU, with memory allocations directed via PyTorch.
# This prevents out-of-memory errors that would otherwise occur from competing
# memory pools.
use_pytorch_for_gpu_memory()
require_gpu(0)

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

### Training usage {#transformers-training}

The recommended workflow for training is to use spaCy's
[config system](/usage/training#config), usually via the
[`spacy train`](/api/cli#train) command. The training config defines all
component settings and hyperparameters in one place and lets you describe a tree
of objects by referring to creation functions, including functions you register
yourself. For details on how to get started with training your own model, check
out the [training quickstart](/usage/training#quickstart).

<!-- TODO:
<Project id="en_core_trf_lg">

The easiest way to get started is to clone a transformers-based project
template. Swap in your data, edit the settings and hyperparameters and train,
evaluate, package and visualize your model.

</Project>
-->

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
@annotation_setters = "spacy-transformers.null_annotation_setter.v1"

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
are missing, and you can run
[`spacy init fill-config`](/api/cli#init-fill-config) to automatically fill in
all defaults.

</Infobox>

### Customizing the settings {#transformers-training-custom-settings}

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

```cli
python -m spacy train ./config.cfg --code ./code.py
```

### Customizing the model implementations {#training-custom-model}

The [`Transformer`](/api/transformer) component expects a Thinc
[`Model`](https://thinc.ai/docs/api-model) object to be passed in as its `model`
argument. You're not limited to the implementation provided by
`spacy-transformers` – the only requirement is that your registered function
must return an object of type ~~Model[List[Doc], FullTransformerBatch]~~: that
is, a Thinc model that takes a list of [`Doc`](/api/doc) objects, and returns a
[`FullTransformerBatch`](/api/transformer#fulltransformerbatch) object with the
transformer data.

The same idea applies to task models that power the **downstream components**.
Most of spaCy's built-in model creation functions support a `tok2vec` argument,
which should be a Thinc layer of type ~~Model[List[Doc], List[Floats2d]]~~. This
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
`pooling`, which needs to be of type ~~Model[Ragged, Floats2d]~~. This layer
determines how the vector for each spaCy token will be computed from the zero or
more source rows the token is aligned against. Here we use the
[`reduce_mean`](https://thinc.ai/docs/api-layers#reduce_mean) layer, which
averages the wordpiece rows. We could instead use
[`reduce_max`](https://thinc.ai/docs/api-layers#reduce_max), or a custom
function you write yourself.

You can have multiple components all listening to the same transformer model,
and all passing gradients back to it. By default, all of the gradients will be
**equally weighted**. You can control this with the `grad_factor` setting, which
lets you reweight the gradients from the different listeners. For instance,
setting `grad_factor = 0` would disable gradients from one of the listeners,
while `grad_factor = 2.0` would multiply them by 2. This is similar to having a
custom learning rate for each component. Instead of a constant, you can also
provide a schedule, allowing you to freeze the shared parameters at the start of
training.

## Static vectors {#static-vectors}

<!-- TODO: write -->

### Using word vectors in your models {#word-vectors-models}

Many neural network models are able to use word vector tables as additional
features, which sometimes results in significant improvements in accuracy.
spaCy's built-in embedding layer,
[MultiHashEmbed](/api/architectures#MultiHashEmbed), can be configured to use
word vector tables using the `also_use_static_vectors` flag. This setting is
also available on the [MultiHashEmbedCNN](/api/architectures#MultiHashEmbedCNN)
layer, which builds the default token-to-vector encoding architecture.

```ini
[tagger.model.tok2vec.embed]
@architectures = "spacy.MultiHashEmbed.v1"
width = 128
rows = 7000
also_embed_subwords = true
also_use_static_vectors = true
```

<Infobox title="How it works" emoji="💡">

The configuration system will look up the string `"spacy.MultiHashEmbed.v1"` in
the `architectures` [registry](/api/top-level#registry), and call the returned
object with the rest of the arguments from the block. This will result in a call
to the
[`MultiHashEmbed`](https://github.com/explosion/spacy/tree/develop/spacy/ml/models/tok2vec.py)
function, which will return a [Thinc](https://thinc.ai) model object with the
type signature ~~Model[List[Doc], List[Floats2d]]~~. Because the embedding layer
takes a list of `Doc` objects as input, it does not need to store a copy of the
vectors table. The vectors will be retrieved from the `Doc` objects that are
passed in, via the `doc.vocab.vectors` attribute. This part of the process is
handled by the [StaticVectors](/api/architectures#StaticVectors) layer.

</Infobox>

#### Creating a custom embedding layer {#custom-embedding-layer}

The [MultiHashEmbed](/api/architectures#StaticVectors) layer is spaCy's
recommended strategy for constructing initial word representations for your
neural network models, but you can also implement your own. You can register any
function to a string name, and then reference that function within your config
(see the [training docs](/usage/training) for more details). To try this out,
you can save the following little example to a new Python file:

```python
from spacy.ml.staticvectors import StaticVectors
from spacy.util import registry

print("I was imported!")

@registry.architectures("my_example.MyEmbedding.v1")
def MyEmbedding(output_width: int) -> Model[List[Doc], List[Floats2d]]:
    print("I was called!")
    return StaticVectors(nO=output_width)
```

If you pass the path to your file to the [`spacy train`](/api/cli#train) command
using the `--code` argument, your file will be imported, which means the
decorator registering the function will be run. Your function is now on equal
footing with any of spaCy's built-ins, so you can drop it in instead of any
other model with the same input and output signature. For instance, you could
use it in the tagger model as follows:

```ini
[tagger.model.tok2vec.embed]
@architectures = "my_example.MyEmbedding.v1"
output_width = 128
```

Now that you have a custom function wired into the network, you can start
implementing the logic you're interested in. For example, let's say you want to
try a relatively simple embedding strategy that makes use of static word
vectors, but combines them via summation with a smaller table of learned
embeddings.

```python
from thinc.api import add, chain, remap_ids, Embed
from spacy.ml.staticvectors import StaticVectors

@registry.architectures("my_example.MyEmbedding.v1")
def MyCustomVectors(
    output_width: int,
    vector_width: int,
    embed_rows: int,
    key2row: Dict[int, int]
) -> Model[List[Doc], List[Floats2d]]:
    return add(
        StaticVectors(nO=output_width),
        chain(
           FeatureExtractor(["ORTH"]),
           remap_ids(key2row),
           Embed(nO=output_width, nV=embed_rows)
        )
    )
```

## Pretraining {#pretraining}

<!-- TODO: write -->
