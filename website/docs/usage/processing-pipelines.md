---
title: Language Processing Pipelines
next: /usage/vectors-embeddings
menu:
  - ['Processing Text', 'processing']
  - ['How Pipelines Work', 'pipelines']
  - ['Custom Components', 'custom-components']
  # - ['Trainable Components', 'trainable-components']
  - ['Extension Attributes', 'custom-components-attributes']
  - ['Plugins & Wrappers', 'plugins']
---

import Pipelines101 from 'usage/101/\_pipelines.md'

<Pipelines101 />

## Processing text {#processing}

When you call `nlp` on a text, spaCy will **tokenize** it and then **call each
component** on the `Doc`, in order. It then returns the processed `Doc` that you
can work with.

```python
doc = nlp("This is a text")
```

When processing large volumes of text, the statistical models are usually more
efficient if you let them work on batches of texts. spaCy's
[`nlp.pipe`](/api/language#pipe) method takes an iterable of texts and yields
processed `Doc` objects. The batching is done internally.

```diff
texts = ["This is a text", "These are lots of texts", "..."]
- docs = [nlp(text) for text in texts]
+ docs = list(nlp.pipe(texts))
```

<Infobox title="Tips for efficient processing" emoji="💡">

- Process the texts **as a stream** using [`nlp.pipe`](/api/language#pipe) and
  buffer them in batches, instead of one-by-one. This is usually much more
  efficient.
- Only apply the **pipeline components you need**. Getting predictions from the
  model that you don't actually need adds up and becomes very inefficient at
  scale. To prevent this, use the `disable` keyword argument to disable
  components you don't need – either when loading a model, or during processing
  with `nlp.pipe`. See the section on
  [disabling pipeline components](#disabling) for more details and examples.

</Infobox>

In this example, we're using [`nlp.pipe`](/api/language#pipe) to process a
(potentially very large) iterable of texts as a stream. Because we're only
accessing the named entities in `doc.ents` (set by the `ner` component), we'll
disable all other statistical components (the `tagger` and `parser`) during
processing. `nlp.pipe` yields `Doc` objects, so we can iterate over them and
access the named entity predictions:

> #### ✏️ Things to try
>
> 1. Also disable the `"ner"` component. You'll see that the `doc.ents` are now
>    empty, because the entity recognizer didn't run.

```python
### {executable="true"}
import spacy

texts = [
    "Net income was $9.4 million compared to the prior year of $2.7 million.",
    "Revenue exceeded twelve billion dollars, with a loss of $1b.",
]

nlp = spacy.load("en_core_web_sm")
for doc in nlp.pipe(texts, disable=["tagger", "parser"]):
    # Do something with the doc here
    print([(ent.text, ent.label_) for ent in doc.ents])
```

<Infobox title="Important note" variant="warning">

When using [`nlp.pipe`](/api/language#pipe), keep in mind that it returns a
[generator](https://realpython.com/introduction-to-python-generators/) that
yields `Doc` objects – not a list. So if you want to use it like a list, you'll
have to call `list()` on it first:

```diff
- docs = nlp.pipe(texts)[0]         # will raise an error
+ docs = list(nlp.pipe(texts))[0]   # works as expected
```

</Infobox>

## How pipelines work {#pipelines}

spaCy makes it very easy to create your own pipelines consisting of reusable
components – this includes spaCy's default tagger, parser and entity recognizer,
but also your own custom processing functions. A pipeline component can be added
to an already existing `nlp` object, specified when initializing a `Language`
class, or defined within a [model package](/usage/saving-loading#models).

> #### config.cfg (excerpt)
>
> ```ini
>  [nlp]
>  lang = "en"
>  pipeline = ["tagger", "parser"]
>
> [components]
>
> [components.tagger]
> factory = "tagger"
> # settings for the tagger component
>
> [components.parser]
> factory = "parser"
> # settings for the parser component
> ```

When you load a model, spaCy first consults the model's
[`meta.json`](/usage/saving-loading#models) and
[`config.cfg`](/usage/training#config). The config tells spaCy what language
class to use, which components are in the pipeline, and how those components
should be created. spaCy will then do the following:

1. Load the **language class and data** for the given ID via
   [`get_lang_class`](/api/top-level#util.get_lang_class) and initialize it. The
   `Language` class contains the shared vocabulary, tokenization rules and the
   language-specific settings.
2. Iterate over the **pipeline names** and look up each component name in the
   `[components]` block. The `factory` tells spaCy which
   [component factory](#custom-components-factories) to use for adding the
   component with with [`add_pipe`](/api/language#add_pipe). The settings are
   passed into the factory.
3. Make the **model data** available to the `Language` class by calling
   [`from_disk`](/api/language#from_disk) with the path to the model data
   directory.

So when you call this...

```python
nlp = spacy.load("en_core_web_sm")
```

... the model's `config.cfg` tells spaCy to use the language `"en"` and the
pipeline `["tagger", "parser", "ner"]`. spaCy will then initialize
`spacy.lang.en.English`, and create each pipeline component and add it to the
processing pipeline. It'll then load in the model's data from its data directory
and return the modified `Language` class for you to use as the `nlp` object.

<Infobox title="Changed in v3.0" variant="warning">

spaCy v3.0 introduces a `config.cfg`, which includes more detailed settings for
the model pipeline, its components and the
[training process](/usage/training#config). You can export the config of your
current `nlp` object by calling [`nlp.config.to_disk`](/api/language#config).

</Infobox>

Fundamentally, a [spaCy model](/models) consists of three components: **the
weights**, i.e. binary data loaded in from a directory, a **pipeline** of
functions called in order, and **language data** like the tokenization rules and
language-specific settings. For example, a Spanish NER model requires different
weights, language data and pipeline components than an English parsing and
tagging model. This is also why the pipeline state is always held by the
`Language` class. [`spacy.load`](/api/top-level#spacy.load) puts this all
together and returns an instance of `Language` with a pipeline set and access to
the binary data:

```python
### spacy.load under the hood
lang = "en"
pipeline = ["tagger", "parser", "ner"]
data_path = "path/to/en_core_web_sm/en_core_web_sm-2.0.0"

cls = spacy.util.get_lang_class(lang)   # 1. Get Language instance, e.g. English()
nlp = cls()                             # 2. Initialize it
for name in pipeline:
    nlp.add_pipe(name)                  # 3. Add the component to the pipeline
nlp.from_disk(model_data_path)          # 4. Load in the binary data
```

When you call `nlp` on a text, spaCy will **tokenize** it and then **call each
component** on the `Doc`, in order. Since the model data is loaded, the
components can access it to assign annotations to the `Doc` object, and
subsequently to the `Token` and `Span` which are only views of the `Doc`, and
don't own any data themselves. All components return the modified document,
which is then processed by the component next in the pipeline.

```python
### The pipeline under the hood
doc = nlp.make_doc("This is a sentence")   # create a Doc from raw text
for name, proc in nlp.pipeline:             # iterate over components in order
    doc = proc(doc)                         # apply each component
```

The current processing pipeline is available as `nlp.pipeline`, which returns a
list of `(name, component)` tuples, or `nlp.pipe_names`, which only returns a
list of human-readable component names.

```python
print(nlp.pipeline)
# [('tagger', <spacy.pipeline.Tagger>), ('parser', <spacy.pipeline.DependencyParser>), ('ner', <spacy.pipeline.EntityRecognizer>)]
print(nlp.pipe_names)
# ['tagger', 'parser', 'ner']
```

### Built-in pipeline components {#built-in}

spaCy ships with several built-in pipeline components that are registered with
string names. This means that you can initialize them by calling
[`nlp.add_pipe`](/api/language#add_pipe) with their names and spaCy will know
how to create them. See the [API documentation](/api) for a full list of
available pipeline components and component functions.

> #### Usage
>
> ```python
> nlp = spacy.blank("en")
> nlp.add_pipe("sentencizer")
> # add_pipe returns the added component
> ruler = nlp.add_pipe("entity_ruler")
> ```

| String name     | Component                                       | Description                                                                               |
| --------------- | ----------------------------------------------- | ----------------------------------------------------------------------------------------- |
| `tagger`        | [`Tagger`](/api/tagger)                         | Assign part-of-speech-tags.                                                               |
| `parser`        | [`DependencyParser`](/api/dependencyparser)     | Assign dependency labels.                                                                 |
| `ner`           | [`EntityRecognizer`](/api/entityrecognizer)     | Assign named entities.                                                                    |
| `entity_linker` | [`EntityLinker`](/api/entitylinker)             | Assign knowledge base IDs to named entities. Should be added after the entity recognizer. |
| `entity_ruler`  | [`EntityRuler`](/api/entityruler)               | Assign named entities based on pattern rules and dictionaries.                            |
| `textcat`       | [`TextCategorizer`](/api/textcategorizer)       | Assign text categories.                                                                   |
| `lemmatizer`    | [`Lemmatizer`](/api/lemmatizer)                 | Assign base forms to words.                                                               |
| `morphologizer` | [`Morphologizer`](/api/morphologizer)           | Assign morphological features and coarse-grained POS tags.                                |
| `senter`        | [`SentenceRecognizer`](/api/sentencerecognizer) | Assign sentence boundaries.                                                               |
| `sentencizer`   | [`Sentencizer`](/api/sentencizer)               | Add rule-based sentence segmentation without the dependency parse.                        |
| `tok2vec`       | [`Tok2Vec`](/api/tok2vec)                       |                                                                                           |
| `transformer`   | [`Transformer`](/api/transformer)               | Assign the tokens and outputs of a transformer model.                                     |

### Disabling and modifying pipeline components {#disabling}

If you don't need a particular component of the pipeline – for example, the
tagger or the parser, you can **disable loading** it. This can sometimes make a
big difference and improve loading speed. Disabled component names can be
provided to [`spacy.load`](/api/top-level#spacy.load),
[`Language.from_disk`](/api/language#from_disk) or the `nlp` object itself as a
list:

```python
### Disable loading
nlp = spacy.load("en_core_web_sm", disable=["tagger", "parser"])
```

In some cases, you do want to load all pipeline components and their weights,
because you need them at different points in your application. However, if you
only need a `Doc` object with named entities, there's no need to run all
pipeline components on it – that can potentially make processing much slower.
Instead, you can use the `disable` keyword argument on
[`nlp.pipe`](/api/language#pipe) to temporarily disable the components **during
processing**:

```python
### Disable for processing
for doc in nlp.pipe(texts, disable=["tagger", "parser"]):
    # Do something with the doc here
```

If you need to **execute more code** with components disabled – e.g. to reset
the weights or update only some components during training – you can use the
[`nlp.select_pipes`](/api/language#select_pipes) contextmanager. At the end of
the `with` block, the disabled pipeline components will be restored
automatically. Alternatively, `select_pipes` returns an object that lets you
call its `restore()` method to restore the disabled components when needed. This
can be useful if you want to prevent unnecessary code indentation of large
blocks.

```python
### Disable for block
# 1. Use as a contextmanager
with nlp.select_pipes(disable=["tagger", "parser"]):
    doc = nlp("I won't be tagged and parsed")
doc = nlp("I will be tagged and parsed")

# 2. Restore manually
disabled = nlp.select_pipes(disable="ner")
doc = nlp("I won't have named entities")
disabled.restore()
```

If you want to disable all pipes except for one or a few, you can use the
`enable` keyword. Just like the `disable` keyword, it takes a list of pipe
names, or a string defining just one pipe.

```python
# Enable only the parser
with nlp.select_pipes(enable="parser"):
    doc = nlp("I will only be parsed")
```

Finally, you can also use the [`remove_pipe`](/api/language#remove_pipe) method
to remove pipeline components from an existing pipeline, the
[`rename_pipe`](/api/language#rename_pipe) method to rename them, or the
[`replace_pipe`](/api/language#replace_pipe) method to replace them with a
custom component entirely (more details on this in the section on
[custom components](#custom-components).

```python
nlp.remove_pipe("parser")
nlp.rename_pipe("ner", "entityrecognizer")
nlp.replace_pipe("tagger", my_custom_tagger)
```

### Sourcing pipeline components from existing models {#sourced-components new="3"}

Pipeline components that are independent can also be reused across models.
Instead of adding a new blank component to a pipeline, you can also copy an
existing component from a pretrained model by setting the `source` argument on
[`nlp.add_pipe`](/api/language#add_pipe). The first argument will then be
interpreted as the name of the component in the source pipeline – for instance,
`"ner"`. This is especially useful for
[training a model](/usage/training#config-components) because it lets you mix
and match components and create fully custom model packages with updated
pretrained components and new components trained on your data.

<Infobox variant="warning" title="Important note for pretrained components">

When reusing components across models, keep in mind that the **vocabulary**,
**vectors** and model settings **must match**. If a pretrained model includes
[word vectors](/usage/vectors-embeddings) and the component uses them as
features, the model you copy it to needs to have the _same_ vectors available –
otherwise, it won't be able to make the same predictions.

</Infobox>

> #### In training config
>
> Instead of providing a `factory`, component blocks in the training
> [config](/usage/training#config) can also define a `source`. The string needs
> to be a loadable spaCy model package or path. The
>
> ```ini
> [components.ner]
> source = "en_core_web_sm"
> component = "ner"
> ```
>
> By default, sourced components will be updated with your data during training.
> If you want to preserve the component as-is, you can "freeze" it:
>
> ```ini
> [training]
> frozen_components = ["ner"]
> ```

```python
### {executable="true"}
import spacy

# The source model with different components
source_nlp = spacy.load("en_core_web_sm")
print(source_nlp.pipe_names)

# Add only the entity recognizer to the new blank model
nlp = spacy.blank("en")
nlp.add_pipe("ner", source=source_nlp)
print(nlp.pipe_names)
```

### Analyzing pipeline components {#analysis new="3"}

The [`nlp.analyze_pipes`](/api/language#analyze_pipes) method analyzes the
components in the current pipeline and outputs information about them, like the
attributes they set on the [`Doc`](/api/doc) and [`Token`](/api/token), whether
they retokenize the `Doc` and which scores they produce during training. It will
also show warnings if components require values that aren't set by previous
component – for instance, if the entity linker is used but no component that
runs before it sets named entities. Setting `pretty=True` will pretty-print a
table instead of only returning the structured data.

> #### ✏️ Things to try
>
> 1. Add the components `"ner"` and `"sentencizer"` _before_ the
>    `"entity_linker"`. The analysis should now show no problems, because
>    requirements are met.

```python
### {executable="true"}
import spacy

nlp = spacy.blank("en")
nlp.add_pipe("tagger")
# This is a problem because it needs entities and sentence boundaries
nlp.add_pipe("entity_linker")
analysis = nlp.analyze_pipes(pretty=True)
```

<Accordion title="Example output">

```json
### Structured
{
  "summary": {
    "tagger": {
      "assigns": ["token.tag"],
      "requires": [],
      "scores": ["tag_acc", "pos_acc", "lemma_acc"],
      "retokenizes": false
    },
    "entity_linker": {
      "assigns": ["token.ent_kb_id"],
      "requires": ["doc.ents", "doc.sents", "token.ent_iob", "token.ent_type"],
      "scores": [],
      "retokenizes": false
    }
  },
  "problems": {
    "tagger": [],
    "entity_linker": ["doc.ents", "doc.sents", "token.ent_iob", "token.ent_type"]
  },
  "attrs": {
    "token.ent_iob": { "assigns": [], "requires": ["entity_linker"] },
    "doc.ents": { "assigns": [], "requires": ["entity_linker"] },
    "token.ent_kb_id": { "assigns": ["entity_linker"], "requires": [] },
    "doc.sents": { "assigns": [], "requires": ["entity_linker"] },
    "token.tag": { "assigns": ["tagger"], "requires": [] },
    "token.ent_type": { "assigns": [], "requires": ["entity_linker"] }
  }
}
```

```
### Pretty
============================= Pipeline Overview =============================

#   Component       Assigns           Requires         Scores      Retokenizes
-   -------------   ---------------   --------------   ---------   -----------
0   tagger          token.tag                          tag_acc     False
                                                       pos_acc
                                                       lemma_acc

1   entity_linker   token.ent_kb_id   doc.ents                     False
                                      doc.sents
                                      token.ent_iob
                                      token.ent_type


================================ Problems (4) ================================
⚠ 'entity_linker' requirements not met: doc.ents, doc.sents,
token.ent_iob, token.ent_type
```

</Accordion>

<Infobox variant="warning" title="Important note">

The pipeline analysis is static and does **not actually run the components**.
This means that it relies on the information provided by the components
themselves. If a custom component declares that it assigns an attribute but it
doesn't, the pipeline analysis won't catch that.

</Infobox>

## Creating custom pipeline components {#custom-components}

A pipeline component is a function that receives a `Doc` object, modifies it and
returns it – – for example, by using the current weights to make a prediction
and set some annotation on the document. By adding a component to the pipeline,
you'll get access to the `Doc` at any point **during processing** – instead of
only being able to modify it afterwards.

> #### Example
>
> ```python
> from spacy.language import Language
>
> @Language.component("my_component")
> def my_component(doc):
>    # do something to the doc here
>    return doc
> ```

| Argument    | Type  | Description                                            |
| ----------- | ----- | ------------------------------------------------------ |
| `doc`       | `Doc` | The `Doc` object processed by the previous component.  |
| **RETURNS** | `Doc` | The `Doc` object processed by this pipeline component. |

The [`@Language.component`](/api/language#component) decorator lets you turn a
simple function into a pipeline component. It takes at least one argument, the
**name** of the component factory. You can use this name to add an instance of
your component to the pipeline. It can also be listed in your model config, so
you can save, load and train models using your component.

Custom components can be added to the pipeline using the
[`add_pipe`](/api/language#add_pipe) method. Optionally, you can either specify
a component to add it **before or after**, tell spaCy to add it **first or
last** in the pipeline, or define a **custom name**. If no name is set and no
`name` attribute is present on your component, the function name is used.

> #### Example
>
> ```python
> nlp.add_pipe("my_component")
> nlp.add_pipe("my_component", first=True)
> nlp.add_pipe("my_component", before="parser")
> ```

| Argument | Type      | Description                                                              |
| -------- | --------- | ------------------------------------------------------------------------ |
| `last`   | bool      | If set to `True`, component is added **last** in the pipeline (default). |
| `first`  | bool      | If set to `True`, component is added **first** in the pipeline.          |
| `before` | str / int | String name or index to add the new component **before**.                |
| `after`  | str / int | String name or index to add the new component **after**.                 |

<Infobox title="Changed in v3.0" variant="warning">

As of v3.0, components need to be registered using the
[`@Language.component`](/api/language#component) or
[`@Language.factory`](/api/language#factory) decorator so spaCy knows that a
function is a component. [`nlp.add_pipe`](/api/language#add_pipe) now takes the
**string name** of the component factory instead of the component function. This
doesn't only save you lines of code, it also allows spaCy to validate and track
your custom components, and make sure they can be saved and loaded.

```diff
- ruler = nlp.create_pipe("entity_ruler")
- nlp.add_pipe(ruler)
+ ruler = nlp.add_pipe("entity_ruler")
```

</Infobox>

### Examples: Simple stateless pipeline components {#custom-components-simple}

The following component receives the `Doc` in the pipeline and prints some
information about it: the number of tokens, the part-of-speech tags of the
tokens and a conditional message based on the document length. The
[`@Language.component`](/api/language#component) decorator lets you register the
component under the name `"info_component"`.

> #### ✏️ Things to try
>
> 1. Add the component first in the pipeline by setting `first=True`. You'll see
>    that the part-of-speech tags are empty, because the component now runs
>    before the tagger and the tags aren't available yet.
> 2. Change the component `name` or remove the `name` argument. You should see
>    this change reflected in `nlp.pipe_names`.
> 3. Print `nlp.pipeline`. You'll see a list of tuples describing the component
>    name and the function that's called on the `Doc` object in the pipeline.
> 4. Change the first argument to `@Language.component`, the name, to something
>    else. spaCy should now complain that it doesn't know a component of the
>    name `"info_component"`.

```python
### {executable="true"}
import spacy
from spacy.language import Language

@Language.component("info_component")
def my_component(doc):
    print(f"After tokenization, this doc has {len(doc)} tokens.")
    print("The part-of-speech tags are:", [token.pos_ for token in doc])
    if len(doc) < 10:
        print("This is a pretty short document.")
    return doc

nlp = spacy.load("en_core_web_sm")
nlp.add_pipe("info_component", name="print_info", last=True)
print(nlp.pipe_names)  # ['tagger', 'parser', 'ner', 'print_info']
doc = nlp("This is a sentence.")
```

Here's another example of a pipeline component that implements custom logic to
improve the sentence boundaries set by the dependency parser. The custom logic
should therefore be applied **after** tokenization, but _before_ the dependency
parsing – this way, the parser can also take advantage of the sentence
boundaries.

> #### ✏️ Things to try
>
> 1. Print `[token.dep_ for token in doc]` with and without the custom pipeline
>    component. You'll see that the predicted dependency parse changes to match
>    the sentence boundaries.
> 2. Remove the `else` block. All other tokens will now have `is_sent_start` set
>    to `None` (missing value), the parser will assign sentence boundaries in
>    between.

```python
### {executable="true"}
import spacy
from spacy.language import Language

@Language.component("custom_sentencizer")
def custom_sentencizer(doc):
    for i, token in enumerate(doc[:-2]):
        # Define sentence start if pipe + titlecase token
        if token.text == "|" and doc[i + 1].is_title:
            doc[i + 1].is_sent_start = True
        else:
            # Explicitly set sentence start to False otherwise, to tell
            # the parser to leave those tokens alone
            doc[i + 1].is_sent_start = False
    return doc

nlp = spacy.load("en_core_web_sm")
nlp.add_pipe("custom_sentencizer", before="parser")  # Insert before the parser
doc = nlp("This is. A sentence. | This is. Another sentence.")
for sent in doc.sents:
    print(sent.text)
```

### Component factories and stateful components {#custom-components-factories}

Component factories are callables that take settings and return a **pipeline
component function**. This is useful if your component is stateful and if you
need to customize their creation, or if you need access to the current `nlp`
object or the shared vocab. Component factories can be registered using the
[`@Language.factory`](/api/language#factory) decorator and they need at least
**two named arguments** that are filled in automatically when the component is
added to the pipeline:

> #### Example
>
> ```python
> from spacy.language import Language
>
> @Language.factory("my_component")
> def my_component(nlp, name):
>    return MyComponent()
> ```

| Argument | Type                        | Description                                                                                                               |
| -------- | --------------------------- | ------------------------------------------------------------------------------------------------------------------------- |
| `nlp`    | [`Language`](/api/language) | The current `nlp` object. Can be used to access the                                                                       |
| `name`   | str                         | The **instance name** of the component in the pipeline. This lets you identify different instances of the same component. |

All other settings can be passed in by the user via the `config` argument on
[`nlp.add_pipe`](/api/language). The
[`@Language.factory`](/api/language#factory) decorator also lets you define a
`default_config` that's used as a fallback.

<!-- TODO: add example of passing in a custom Python object via the config based on a registered function -->

```python
### With config {highlight="4,9"}
import spacy
from spacy.language import Language

@Language.factory("my_component", default_config={"some_setting": True})
def my_component(nlp, name, some_setting: bool):
    return MyComponent(some_setting=some_setting)

nlp = spacy.blank("en")
nlp.add_pipe("my_component", config={"some_setting": False})
```

<Accordion title="How is @Language.factory different from @Language.component?" id="factories-decorator-component">

The [`@Language.component`](/api/language#component) decorator is essentially a
**shortcut** for stateless pipeline component that don't need any settings. This
means you don't have to always write a function that returns your function if
there's no state to be passed through – spaCy can just take care of this for
you. The following two code examples are equivalent:

```python
# Statless component with @Language.factory
@Language.factory("my_component")
def create_my_component():
    def my_component(doc):
        # Do something to the doc
        return doc

    return my_component

# Stateless component with @Language.component
@Language.component("my_component")
def my_component(doc):
    # Do something to the doc
    return doc
```

</Accordion>

<Accordion title="Can I add the @Language.factory decorator to a class?" id="factories-class-decorator" spaced>

Yes, the [`@Language.factory`](/api/language#factory) decorator can be added to
a function or a class. If it's added to a class, it expects the `__init__`
method to take the arguments `nlp` and `name`, and will populate all other
arguments from the config. That said, it's often cleaner and more intuitive to
make your factory a separate function. That's also how spaCy does it internally.

</Accordion>

### Example: Stateful component with settings

This example shows a **stateful** pipeline component for handling acronyms:
based on a dictionary, it will detect acronyms and their expanded forms in both
directions and add them to a list as the custom `doc._.acronyms`
[extension attribute](#custom-components-attributes). Under the hood, it uses
the [`PhraseMatcher`](/api/phrasematcher) to find instances of the phrases.

The factory function takes three arguments: the shared `nlp` object and
component instance `name`, which are passed in automatically by spaCy, and a
`case_sensitive` config setting that makes the matching and acronym detection
case-sensitive.

> #### ✏️ Things to try
>
> 1. Change the `config` passed to `nlp.add_pipe` and set `"case_sensitive"` to
>    `True`. You should see that the expanded acronym for "LOL" isn't detected
>    anymore.
> 2. Add some more terms to the `DICTIONARY` and update the processed text so
>    they're detected.
> 3. Add a `name` argument to `nlp.add_pipe` to change the component name. Print
>    `nlp.pipe_names` to see the change reflected in the pipeline.
> 4. Print the config of the current `nlp` object with
>    `print(nlp.config.to_str())` and inspect the `[components]` block. You
>    should see an entry for the acronyms component, referencing the factory
>    `acronyms` and the config settings.

```python
### {executable="true"}
from spacy.language import Language
from spacy.tokens import Doc
from spacy.matcher import PhraseMatcher
import spacy

DICTIONARY = {"lol": "laughing out loud", "brb": "be right back"}
DICTIONARY.update({value: key for key, value in DICTIONARY.items()})

@Language.factory("acronyms", default_config={"case_sensitive": False})
def create_acronym_component(nlp: Language, name: str, case_sensitive: bool):
    return AcronymComponent(nlp, case_sensitive)

class AcronymComponent:
    def __init__(self, nlp: Language, case_sensitive: bool):
        # Create the matcher and match on Token.lower if case-insensitive
        matcher_attr = "TEXT" if case_sensitive else "LOWER"
        self.matcher = PhraseMatcher(nlp.vocab, attr=matcher_attr)
        self.matcher.add("ACRONYMS", [nlp.make_doc(term) for term in DICTIONARY])
        self.case_sensitive = case_sensitive
        # Register custom extension on the Doc
        if not Doc.has_extension("acronyms"):
            Doc.set_extension("acronyms", default=[])

    def __call__(self, doc: Doc) -> Doc:
        # Add the matched spans when doc is processed
        for _, start, end in self.matcher(doc):
            span = doc[start:end]
            acronym = DICTIONARY.get(span.text if self.case_sensitive else span.text.lower())
            doc._.acronyms.append((span, acronym))
        return doc

# Add the component to the pipeline and configure it
nlp = spacy.blank("en")
nlp.add_pipe("acronyms", config={"case_sensitive": False})

# Process a doc and see the results
doc = nlp("LOL, be right back")
print(doc._.acronyms)
```

### Python type hints and pydantic validation {#type-hints new="3"}

spaCy's configs are powered by our machine learning library Thinc's
[configuration system](https://thinc.ai/docs/usage-config), which supports
[type hints](https://docs.python.org/3/library/typing.html) and even
[advanced type annotations](https://thinc.ai/docs/usage-config#advanced-types)
using [`pydantic`](https://github.com/samuelcolvin/pydantic). If your component
factory provides type hints, the values that are passed in will be **checked
against the expected types**. If the value can't be cast to an integer, spaCy
will raise an error. `pydantic` also provides strict types like `StrictFloat`,
which will force the value to be an integer and raise an error if it's not – for
instance, if your config defines a float.

<Infobox variant="warning">

If you're not using
[strict types](https://pydantic-docs.helpmanual.io/usage/types/#strict-types),
values that can be **cast to** the given type will still be accepted. For
example, `1` can be cast to a `float` or a `bool` type, but not to a
`List[str]`. However, if the type is
[`StrictFloat`](https://pydantic-docs.helpmanual.io/usage/types/#strict-types),
only a float will be accepted.

</Infobox>

The following example shows a custom pipeline component for debugging. It can be
added anywhere in the pipeline and logs information about the `nlp` object and
the `Doc` that passes through. The `log_level` config setting lets the user
customize what log statements are shown – for instance, `"INFO"` will show info
logs and more critical logging statements, whereas `"DEBUG"` will show
everything. The value is annotated as a `StrictStr`, so it will only accept a
string value.

> #### ✏️ Things to try
>
> 1. Change the `config` passed to `nlp.add_pipe` to use the log level `"INFO"`.
>    You should see that only the statement logged with `logger.info` is shown.
> 2. Change the `config` passed to `nlp.add_pipe` so that it contains unexpected
>    values – for example, a boolean instead of a string: `"log_level": False`.
>    You should see a validation error.
> 3. Check out the docs on `pydantic`'s
>    [constrained types](https://pydantic-docs.helpmanual.io/usage/types/#constrained-types)
>    and write a type hint for `log_level` that only accepts the exact string
>    values `"DEBUG"`, `"INFO"` or `"CRITICAL"`.

```python
### {executable="true"}
import spacy
from spacy.language import Language
from spacy.tokens import Doc
from pydantic import StrictStr
import logging

@Language.factory("debug", default_config={"log_level": "DEBUG"})
class DebugComponent:
    def __init__(self, nlp: Language, name: str, log_level: StrictStr):
        self.logger = logging.getLogger(f"spacy.{name}")
        self.logger.setLevel(log_level)
        self.logger.info(f"Pipeline: {nlp.pipe_names}")

    def __call__(self, doc: Doc) -> Doc:
        self.logger.debug(f"Doc: {len(doc)} tokens, is_tagged: {doc.is_tagged}")
        return doc

nlp = spacy.load("en_core_web_sm")
nlp.add_pipe("debug", config={"log_level": "DEBUG"})
doc = nlp("This is a text...")
```

### Language-specific factories {#factories-language new="3"}

There are many use case where you might want your pipeline components to be
language-specific. Sometimes this requires entirely different implementation per
language, sometimes the only difference is in the settings or data. spaCy allows
you to register factories of the **same name** on both the `Language` base
class, as well as its **subclasses** like `English` or `German`. Factories are
resolved starting with the specific subclass. If the subclass doesn't define a
component of that name, spaCy will check the `Language` base class.

Here's an example of a pipeline component that overwrites the normalized form of
a token, the `Token.norm_` with an entry from a language-specific lookup table.
It's registered twice under the name `"token_normalizer"` – once using
`@English.factory` and once using `@German.factory`:

```python
### {executable="true"}
from spacy.lang.en import English
from spacy.lang.de import German

class TokenNormalizer:
    def __init__(self, norm_table):
        self.norm_table = norm_table

    def __call__(self, doc):
        for token in doc:
            # Overwrite the token.norm_ if there's an entry in the data
            token.norm_ = self.norm_table.get(token.text, token.norm_)
        return doc

@English.factory("token_normalizer")
def create_en_normalizer(nlp, name):
    return TokenNormalizer({"realise": "realize", "colour": "color"})

@German.factory("token_normalizer")
def create_de_normalizer(nlp, name):
    return TokenNormalizer({"daß": "dass", "wußte": "wusste"})

nlp_en = English()
nlp_en.add_pipe("token_normalizer")  # uses the English factory
print([token.norm_ for token in nlp_en("realise colour daß wußte")])

nlp_de = German()
nlp_de.add_pipe("token_normalizer")  # uses the German factory
print([token.norm_ for token in nlp_de("realise colour daß wußte")])
```

<Infobox title="Implementation details">

Under the hood, language-specific factories are added to the
[`factories` registry](/api/top-level#registry) prefixed with the language code,
e.g. `"en.token_normalizer"`. When resolving the factory in
[`nlp.add_pipe`](/api/language#add_pipe), spaCy first checks for a
language-specific version of the factory using `nlp.lang` and if none is
available, falls back to looking up the regular factory name.

</Infobox>

<!-- TODO:
## Trainable components {#trainable-components new="3"}

spaCy's [`Pipe`](/api/pipe) class helps you implement your own trainable
components that have their own model instance, make predictions over `Doc`
objects and can be updated using [`spacy train`](/api/cli#train). This lets you
plug fully custom machine learning components into your pipeline.

--->

## Extension attributes {#custom-components-attributes new="2"}

spaCy allows you to set any custom attributes and methods on the `Doc`, `Span`
and `Token`, which become available as `Doc._`, `Span._` and `Token._` – for
example, `Token._.my_attr`. This lets you store additional information relevant
to your application, add new features and functionality to spaCy, and implement
your own models trained with other machine learning libraries. It also lets you
take advantage of spaCy's data structures and the `Doc` object as the "single
source of truth".

<Accordion title="Why ._ and not just a top-level attribute?" id="why-dot-underscore">

Writing to a `._` attribute instead of to the `Doc` directly keeps a clearer
separation and makes it easier to ensure backwards compatibility. For example,
if you've implemented your own `.coref` property and spaCy claims it one day,
it'll break your code. Similarly, just by looking at the code, you'll
immediately know what's built-in and what's custom – for example,
`doc.sentiment` is spaCy, while `doc._.sent_score` isn't.

</Accordion>

<Accordion title="How is the ._ implemented?" id="dot-underscore-implementation">

Extension definitions – the defaults, methods, getters and setters you pass in
to `set_extension` – are stored in class attributes on the `Underscore` class.
If you write to an extension attribute, e.g. `doc._.hello = True`, the data is
stored within the [`Doc.user_data`](/api/doc#attributes) dictionary. To keep the
underscore data separate from your other dictionary entries, the string `"._."`
is placed before the name, in a tuple.

</Accordion>

---

There are three main types of extensions, which can be defined using the
[`Doc.set_extension`](/api/doc#set_extension),
[`Span.set_extension`](/api/span#set_extension) and
[`Token.set_extension`](/api/token#set_extension) methods.

1. **Attribute extensions.** Set a default value for an attribute, which can be
   overwritten manually at any time. Attribute extensions work like "normal"
   variables and are the quickest way to store arbitrary information on a `Doc`,
   `Span` or `Token`.

   ```python
    Doc.set_extension("hello", default=True)
    assert doc._.hello
    doc._.hello = False
   ```

2. **Property extensions.** Define a getter and an optional setter function. If
   no setter is provided, the extension is immutable. Since the getter and
   setter functions are only called when you _retrieve_ the attribute, you can
   also access values of previously added attribute extensions. For example, a
   `Doc` getter can average over `Token` attributes. For `Span` extensions,
   you'll almost always want to use a property – otherwise, you'd have to write
   to _every possible_ `Span` in the `Doc` to set up the values correctly.

   ```python
   Doc.set_extension("hello", getter=get_hello_value, setter=set_hello_value)
   assert doc._.hello
   doc._.hello = "Hi!"
   ```

3. **Method extensions.** Assign a function that becomes available as an object
   method. Method extensions are always immutable. For more details and
   implementation ideas, see
   [these examples](/usage/examples#custom-components-attr-methods).

   ```python
   Doc.set_extension("hello", method=lambda doc, name: f"Hi {name}!")
   assert doc._.hello("Bob") == "Hi Bob!"
   ```

Before you can access a custom extension, you need to register it using the
`set_extension` method on the object you want to add it to, e.g. the `Doc`. Keep
in mind that extensions are always **added globally** and not just on a
particular instance. If an attribute of the same name already exists, or if
you're trying to access an attribute that hasn't been registered, spaCy will
raise an `AttributeError`.

```python
### Example
from spacy.tokens import Doc, Span, Token

fruits = ["apple", "pear", "banana", "orange", "strawberry"]
is_fruit_getter = lambda token: token.text in fruits
has_fruit_getter = lambda obj: any([t.text in fruits for t in obj])

Token.set_extension("is_fruit", getter=is_fruit_getter)
Doc.set_extension("has_fruit", getter=has_fruit_getter)
Span.set_extension("has_fruit", getter=has_fruit_getter)
```

> #### Usage example
>
> ```python
> doc = nlp("I have an apple and a melon")
> assert doc[3]._.is_fruit      # get Token attributes
> assert not doc[0]._.is_fruit
> assert doc._.has_fruit        # get Doc attributes
> assert doc[1:4]._.has_fruit   # get Span attributes
> ```

Once you've registered your custom attribute, you can also use the built-in
`set`, `get` and `has` methods to modify and retrieve the attributes. This is
especially useful it you want to pass in a string instead of calling
`doc._.my_attr`.

### Example: Pipeline component for GPE entities and country meta data via a REST API {#component-example3}

This example shows the implementation of a pipeline component that fetches
country meta data via the [REST Countries API](https://restcountries.eu), sets
entity annotations for countries, merges entities into one token and sets custom
attributes on the `Doc`, `Span` and `Token` – for example, the capital,
latitude/longitude coordinates and even the country flag.

```python
### {executable="true"}
import requests
from spacy.lang.en import English
from spacy.language import Language
from spacy.matcher import PhraseMatcher
from spacy.tokens import Doc, Span, Token

@Language.factory("rest_countries")
class RESTCountriesComponent:
    def __init__(self, nlp, name, label="GPE"):
        r = requests.get("https://restcountries.eu/rest/v2/all")
        r.raise_for_status()  # make sure requests raises an error if it fails
        countries = r.json()
        # Convert API response to dict keyed by country name for easy lookup
        self.countries = {c["name"]: c for c in countries}
        self.label = label
        # Set up the PhraseMatcher with Doc patterns for each country name
        self.matcher = PhraseMatcher(nlp.vocab)
        self.matcher.add("COUNTRIES", [nlp.make_doc(c) for c in self.countries.keys()])
        # Register attribute on the Token. We'll be overwriting this based on
        # the matches, so we're only setting a default value, not a getter.
        Token.set_extension("is_country", default=False)
        Token.set_extension("country_capital", default=False)
        Token.set_extension("country_latlng", default=False)
        Token.set_extension("country_flag", default=False)
        # Register attributes on Doc and Span via a getter that checks if one of
        # the contained tokens is set to is_country == True.
        Doc.set_extension("has_country", getter=self.has_country)
        Span.set_extension("has_country", getter=self.has_country)

    def __call__(self, doc):
        spans = []  # keep the spans for later so we can merge them afterwards
        for _, start, end in self.matcher(doc):
            # Generate Span representing the entity & set label
            entity = Span(doc, start, end, label=self.label)
            spans.append(entity)
            # Set custom attribute on each token of the entity
            # Can be extended with other data returned by the API, like
            # currencies, country code, flag, calling code etc.
            for token in entity:
                token._.set("is_country", True)
                token._.set("country_capital", self.countries[entity.text]["capital"])
                token._.set("country_latlng", self.countries[entity.text]["latlng"])
                token._.set("country_flag", self.countries[entity.text]["flag"])
        # Iterate over all spans and merge them into one token
        with doc.retokenize() as retokenizer:
            for span in spans:
                retokenizer.merge(span)
        # Overwrite doc.ents and add entity – be careful not to replace!
        doc.ents = list(doc.ents) + spans
        return doc  # don't forget to return the Doc!

    def has_country(self, tokens):
        """Getter for Doc and Span attributes. Since the getter is only called
        when we access the attribute, we can refer to the Token's 'is_country'
        attribute here, which is already set in the processing step."""
        return any([t._.get("is_country") for t in tokens])

nlp = English()
nlp.add_pipe("rest_countries", config={"label": "GPE"})
doc = nlp("Some text about Colombia and the Czech Republic")
print("Pipeline", nlp.pipe_names)  # pipeline contains component name
print("Doc has countries", doc._.has_country)  # Doc contains countries
for token in doc:
    if token._.is_country:
        print(token.text, token._.country_capital, token._.country_latlng, token._.country_flag)
print("Entities", [(e.text, e.label_) for e in doc.ents])
```

In this case, all data can be fetched on initialization in one request. However,
if you're working with text that contains incomplete country names, spelling
mistakes or foreign-language versions, you could also implement a
`like_country`-style getter function that makes a request to the search API
endpoint and returns the best-matching result.

### User hooks {#custom-components-user-hooks}

While it's generally recommended to use the `Doc._`, `Span._` and `Token._`
proxies to add your own custom attributes, spaCy offers a few exceptions to
allow **customizing the built-in methods** like
[`Doc.similarity`](/api/doc#similarity) or [`Doc.vector`](/api/doc#vector) with
your own hooks, which can rely on statistical models you train yourself. For
instance, you can provide your own on-the-fly sentence segmentation algorithm or
document similarity method.

Hooks let you customize some of the behaviors of the `Doc`, `Span` or `Token`
objects by adding a component to the pipeline. For instance, to customize the
[`Doc.similarity`](/api/doc#similarity) method, you can add a component that
sets a custom function to `doc.user_hooks['similarity']`. The built-in
`Doc.similarity` method will check the `user_hooks` dict, and delegate to your
function if you've set one. Similar results can be achieved by setting functions
to `Doc.user_span_hooks` and `Doc.user_token_hooks`.

> #### Implementation note
>
> The hooks live on the `Doc` object because the `Span` and `Token` objects are
> created lazily, and don't own any data. They just proxy to their parent `Doc`.
> This turns out to be convenient here — we only have to worry about installing
> hooks in one place.

| Name               | Customizes                                                                                                                                                                                                              |
| ------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `user_hooks`       | [`Doc.vector`](/api/doc#vector), [`Doc.has_vector`](/api/doc#has_vector), [`Doc.vector_norm`](/api/doc#vector_norm), [`Doc.sents`](/api/doc#sents)                                                                      |
| `user_token_hooks` | [`Token.similarity`](/api/token#similarity), [`Token.vector`](/api/token#vector), [`Token.has_vector`](/api/token#has_vector), [`Token.vector_norm`](/api/token#vector_norm), [`Token.conjuncts`](/api/token#conjuncts) |
| `user_span_hooks`  | [`Span.similarity`](/api/span#similarity), [`Span.vector`](/api/span#vector), [`Span.has_vector`](/api/span#has_vector), [`Span.vector_norm`](/api/span#vector_norm), [`Span.root`](/api/span#root)                     |

```python
### Add custom similarity hooks
class SimilarityModel:
    def __init__(self, model):
        self._model = model

    def __call__(self, doc):
        doc.user_hooks["similarity"] = self.similarity
        doc.user_span_hooks["similarity"] = self.similarity
        doc.user_token_hooks["similarity"] = self.similarity

    def similarity(self, obj1, obj2):
        y = self._model([obj1.vector, obj2.vector])
        return float(y[0])
```

## Developing plugins and wrappers {#plugins}

We're very excited about all the new possibilities for community extensions and
plugins in spaCy, and we can't wait to see what you build with it! To get you
started, here are a few tips, tricks and best
practices. [See here](/universe/?category=pipeline) for examples of other spaCy
extensions.

### Usage ideas {#custom-components-usage-ideas}

- **Adding new features and hooking in models.** For example, a sentiment
  analysis model, or your preferred solution for lemmatization or sentiment
  analysis. spaCy's built-in tagger, parser and entity recognizer respect
  annotations that were already set on the `Doc` in a previous step of the
  pipeline.
- **Integrating other libraries and APIs.** For example, your pipeline component
  can write additional information and data directly to the `Doc` or `Token` as
  custom attributes, while making sure no information is lost in the process.
  This can be output generated by other libraries and models, or an external
  service with a REST API.
- **Debugging and logging.** For example, a component which stores and/or
  exports relevant information about the current state of the processed
  document, and insert it at any point of your pipeline.

### Best practices {#custom-components-best-practices}

Extensions can claim their own `._` namespace and exist as standalone packages.
If you're developing a tool or library and want to make it easy for others to
use it with spaCy and add it to their pipeline, all you have to do is expose a
function that takes a `Doc`, modifies it and returns it.

- Make sure to choose a **descriptive and specific name** for your pipeline
  component class, and set it as its `name` attribute. Avoid names that are too
  common or likely to clash with built-in or a user's other custom components.
  While it's fine to call your package `"spacy_my_extension"`, avoid component
  names including `"spacy"`, since this can easily lead to confusion.

  ```diff
  + name = "myapp_lemmatizer"
  - name = "lemmatizer"
  ```

- When writing to `Doc`, `Token` or `Span` objects, **use getter functions**
  wherever possible, and avoid setting values explicitly. Tokens and spans don't
  own any data themselves, and they're implemented as C extension classes – so
  you can't usually add new attributes to them like you could with most pure
  Python objects.

  ```diff
  + is_fruit = lambda token: token.text in ("apple", "orange")
  + Token.set_extension("is_fruit", getter=is_fruit)

  - token._.set_extension("is_fruit", default=False)
  - if token.text in ('"apple", "orange"):
  -     token._.set("is_fruit", True)
  ```

- Always add your custom attributes to the **global** `Doc`, `Token` or `Span`
  objects, not a particular instance of them. Add the attributes **as early as
  possible**, e.g. in your extension's `__init__` method or in the global scope
  of your module. This means that in the case of namespace collisions, the user
  will see an error immediately, not just when they run their pipeline.

  ```diff
  + from spacy.tokens import Doc
  + def __init__(attr="my_attr"):
  +     Doc.set_extension(attr, getter=self.get_doc_attr)

  - def __call__(doc):
  -     doc.set_extension("my_attr", getter=self.get_doc_attr)
  ```

- If your extension is setting properties on the `Doc`, `Token` or `Span`,
  include an option to **let the user to change those attribute names**. This
  makes it easier to avoid namespace collisions and accommodate users with
  different naming preferences. We recommend adding an `attrs` argument to the
  `__init__` method of your class so you can write the names to class attributes
  and reuse them across your component.

  ```diff
  + Doc.set_extension(self.doc_attr, default="some value")
  - Doc.set_extension("my_doc_attr", default="some value")
  ```

- Ideally, extensions should be **standalone packages** with spaCy and
  optionally, other packages specified as a dependency. They can freely assign
  to their own `._` namespace, but should stick to that. If your extension's
  only job is to provide a better `.similarity` implementation, and your docs
  state this explicitly, there's no problem with writing to the
  [`user_hooks`](#custom-components-user-hooks) and overwriting spaCy's built-in
  method. However, a third-party extension should **never silently overwrite
  built-ins**, or attributes set by other extensions.

- If you're looking to publish a model that depends on a custom pipeline
  component, you can either **require it** in the model package's dependencies,
  or – if the component is specific and lightweight – choose to **ship it with
  your model package** and add it to the `Language` instance returned by the
  model's `load()` method. For examples of this, check out the implementations
  of spaCy's
  [`load_model_from_init_py`](/api/top-level#util.load_model_from_init_py)
  [`load_model_from_path`](/api/top-level#util.load_model_from_path) utility
  functions.

- Once you're ready to share your extension with others, make sure to **add docs
  and installation instructions** (you can always link to this page for more
  info). Make it easy for others to install and use your extension, for example
  by uploading it to [PyPi](https://pypi.python.org). If you're sharing your
  code on GitHub, don't forget to tag it with
  [`spacy`](https://github.com/topics/spacy?o=desc&s=stars) and
  [`spacy-extension`](https://github.com/topics/spacy-extension?o=desc&s=stars)
  to help people find it. If you post it on Twitter, feel free to tag
  [@spacy_io](https://twitter.com/spacy_io) so we can check it out.

### Wrapping other models and libraries {#wrapping-models-libraries}

Let's say you have a custom entity recognizer that takes a list of strings and
returns their [BILUO tags](/usage/linguistic-features#accessing-ner). Given an
input like `["A", "text", "about", "Facebook"]`, it will predict and return
`["O", "O", "O", "U-ORG"]`. To integrate it into your spaCy pipeline and make it
add those entities to the `doc.ents`, you can wrap it in a custom pipeline
component function and pass it the token texts from the `Doc` object received by
the component.

The [`gold.spans_from_biluo_tags`](/api/top-level#spans_from_biluo_tags) is very
helpful here, because it takes a `Doc` object and token-based BILUO tags and
returns a sequence of `Span` objects in the `Doc` with added labels. So all your
wrapper has to do is compute the entity spans and overwrite the `doc.ents`.

> #### How the doc.ents work
>
> When you add spans to the `doc.ents`, spaCy will automatically resolve them
> back to the underlying tokens and set the `Token.ent_type` and `Token.ent_iob`
> attributes. By definition, each token can only be part of one entity, so
> overlapping entity spans are not allowed.

```python
### {highlight="1,8-9"}
import your_custom_entity_recognizer
from spacy.gold import offsets_from_biluo_tags
from spacy.language import Language

@Language.component("custom_ner_wrapper")
def custom_ner_wrapper(doc):
    words = [token.text for token in doc]
    custom_entities = your_custom_entity_recognizer(words)
    doc.ents = spans_from_biluo_tags(doc, custom_entities)
    return doc
```

The `custom_ner_wrapper` can then be added to the pipeline of a blank model
using [`nlp.add_pipe`](/api/language#add_pipe). You can also replace the
existing entity recognizer of a pretrained model with
[`nlp.replace_pipe`](/api/language#replace_pipe).

Here's another example of a custom model, `your_custom_model`, that takes a list
of tokens and returns lists of fine-grained part-of-speech tags, coarse-grained
part-of-speech tags, dependency labels and head token indices. Here, we can use
the [`Doc.from_array`](/api/doc#from_array) to create a new `Doc` object using
those values. To create a numpy array we need integers, so we can look up the
string labels in the [`StringStore`](/api/stringstore). The
[`doc.vocab.strings.add`](/api/stringstore#add) method comes in handy here,
because it returns the integer ID of the string _and_ makes sure it's added to
the vocab. This is especially important if the custom model uses a different
label scheme than spaCy's default models.

> #### Example: spacy-stanza
>
> For an example of an end-to-end wrapper for statistical tokenization, tagging
> and parsing, check out
> [`spacy-stanza`](https://github.com/explosion/spacy-stanza). It uses a very
> similar approach to the example in this section – the only difference is that
> it fully replaces the `nlp` object instead of providing a pipeline component,
> since it also needs to handle tokenization.

```python
### {highlight="1,11,17-19"}
import your_custom_model
from spacy.language import Language
from spacy.symbols import POS, TAG, DEP, HEAD
from spacy.tokens import Doc
import numpy

@Language.component("custom_model_wrapper")
def custom_model_wrapper(doc):
    words = [token.text for token in doc]
    spaces = [token.whitespace for token in doc]
    pos, tags, deps, heads = your_custom_model(words)
    # Convert the strings to integers and add them to the string store
    pos = [doc.vocab.strings.add(label) for label in pos]
    tags = [doc.vocab.strings.add(label) for label in tags]
    deps = [doc.vocab.strings.add(label) for label in deps]
    # Create a new Doc from a numpy array
    attrs = [POS, TAG, DEP, HEAD]
    arr = numpy.array(list(zip(pos, tags, deps, heads)), dtype="uint64")
    new_doc = Doc(doc.vocab, words=words, spaces=spaces).from_array(attrs, arr)
    return new_doc
```

<Infobox title="Sentence boundaries and heads" variant="warning">

If you create a `Doc` object with dependencies and heads, spaCy is able to
resolve the sentence boundaries automatically. However, note that the `HEAD`
value used to construct a `Doc` is the token index **relative** to the current
token – e.g. `-1` for the previous token. The CoNLL format typically annotates
heads as `1`-indexed absolute indices with `0` indicating the root. If that's
the case in your annotations, you need to convert them first:

```python
heads = [2, 0, 4, 2, 2]
new_heads = [head - i - 1 if head != 0 else 0 for i, head in enumerate(heads)]
```

</Infobox>

<Infobox title="Advanced usage, serialization and entry points" emoji="📖">

For more details on how to write and package custom components, make them
available to spaCy via entry points and implement your own serialization
methods, check out the usage guide on
[saving and loading](/usage/saving-loading).

</Infobox>
