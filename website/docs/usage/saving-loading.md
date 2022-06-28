---
title: Saving and Loading
menu:
  - ['Basics', 'basics']
  - ['Serializing Docs', 'docs']
  - ['Serialization Methods', 'serialization-methods']
  - ['Entry Points', 'entry-points']
  - ['Trained Pipelines', 'models']
---

## Basics {#basics hidden="true"}

import Serialization101 from 'usage/101/\_serialization.md'

<Serialization101 />

### Serializing the pipeline {#pipeline}

When serializing the pipeline, keep in mind that this will only save out the
**binary data for the individual components** to allow spaCy to restore them –
not the entire objects. This is a good thing, because it makes serialization
safe. But it also means that you have to take care of storing the config, which
contains the pipeline configuration and all the relevant settings.

> #### Saving the meta and config
>
> The [`nlp.meta`](/api/language#meta) attribute is a JSON-serializable
> dictionary and contains all pipeline meta information like the author and
> license information. The [`nlp.config`](/api/language#config) attribute is a
> dictionary containing the training configuration, pipeline component factories
> and other settings. It is saved out with a pipeline as the `config.cfg`.

```python
### Serialize
config = nlp.config
bytes_data = nlp.to_bytes()
```

```python
### Deserialize
lang_cls = spacy.util.get_lang_class(config["nlp"]["lang"])
nlp = lang_cls.from_config(config)
nlp.from_bytes(bytes_data)
```

This is also how spaCy does it under the hood when loading a pipeline: it loads
the `config.cfg` containing the language and pipeline information, initializes
the language class, creates and adds the pipeline components based on the config
and _then_ loads in the binary data. You can read more about this process
[here](/usage/processing-pipelines#pipelines).

## Serializing Doc objects efficiently {#docs new="2.2"}

If you're working with lots of data, you'll probably need to pass analyses
between machines, either to use something like [Dask](https://dask.org) or
[Spark](https://spark.apache.org), or even just to save out work to disk. Often
it's sufficient to use the [`Doc.to_array`](/api/doc#to_array) functionality for
this, and just serialize the numpy arrays – but other times you want a more
general way to save and restore `Doc` objects.

The [`DocBin`](/api/docbin) class makes it easy to serialize and deserialize a
collection of `Doc` objects together, and is much more efficient than calling
[`Doc.to_bytes`](/api/doc#to_bytes) on each individual `Doc` object. You can
also control what data gets saved, and you can merge pallets together for easy
map/reduce-style processing.

```python
### {highlight="4,8,9,13,14"}
import spacy
from spacy.tokens import DocBin

doc_bin = DocBin(attrs=["LEMMA", "ENT_IOB", "ENT_TYPE"], store_user_data=True)
texts = ["Some text", "Lots of texts...", "..."]
nlp = spacy.load("en_core_web_sm")
for doc in nlp.pipe(texts):
    doc_bin.add(doc)
bytes_data = doc_bin.to_bytes()

# Deserialize later, e.g. in a new process
nlp = spacy.blank("en")
doc_bin = DocBin().from_bytes(bytes_data)
docs = list(doc_bin.get_docs(nlp.vocab))
```

If `store_user_data` is set to `True`, the `Doc.user_data` will be serialized as
well, which includes the values of
[extension attributes](/usage/processing-pipelines#custom-components-attributes)
(if they're serializable with msgpack).

<Infobox title="Important note on serializing extension attributes" variant="warning">

Including the `Doc.user_data` and extension attributes will only serialize the
**values** of the attributes. To restore the values and access them via the
`doc._.` property, you need to register the global attribute on the `Doc` again.

```python
docs = list(doc_bin.get_docs(nlp.vocab))
Doc.set_extension("my_custom_attr", default=None)
print([doc._.my_custom_attr for doc in docs])
```

</Infobox>

### Using Pickle {#pickle}

> #### Example
>
> ```python
> doc = nlp("This is a text.")
> data = pickle.dumps(doc)
> ```

When pickling spaCy's objects like the [`Doc`](/api/doc) or the
[`EntityRecognizer`](/api/entityrecognizer), keep in mind that they all require
the shared [`Vocab`](/api/vocab) (which includes the string to hash mappings,
label schemes and optional vectors). This means that their pickled
representations can become very large, especially if you have word vectors
loaded, because it won't only include the object itself, but also the entire
shared vocab it depends on.

If you need to pickle multiple objects, try to pickle them **together** instead
of separately. For instance, instead of pickling all pipeline components, pickle
the entire pipeline once. And instead of pickling several `Doc` objects
separately, pickle a list of `Doc` objects. Since they all share a reference to
the _same_ `Vocab` object, it will only be included once.

```python
### Pickling objects with shared data {highlight="8-9"}
doc1 = nlp("Hello world")
doc2 = nlp("This is a test")

doc1_data = pickle.dumps(doc1)
doc2_data = pickle.dumps(doc2)
print(len(doc1_data) + len(doc2_data))  # 6636116 😞

doc_data = pickle.dumps([doc1, doc2])
print(len(doc_data))  # 3319761 😃
```

<Infobox title="Pickling spans and tokens" variant="warning">

Pickling `Token` and `Span` objects isn't supported. They're only views of the
`Doc` and can't exist on their own. Pickling them would always mean pulling in
the parent document and its vocabulary, which has practically no advantage over
pickling the parent `Doc`.

```diff
- data = pickle.dumps(doc[10:20])
+ data = pickle.dumps(doc)
```

If you really only need a span – for example, a particular sentence – you can
use [`Span.as_doc`](/api/span#as_doc) to make a copy of it and convert it to a
`Doc` object. However, note that this will not let you recover contextual
information from _outside_ the span.

```diff
+ span_doc = doc[10:20].as_doc()
data = pickle.dumps(span_doc)
```

</Infobox>

## Implementing serialization methods {#serialization-methods}

When you call [`nlp.to_disk`](/api/language#to_disk),
[`nlp.from_disk`](/api/language#from_disk) or load a pipeline package, spaCy
will iterate over the components in the pipeline, check if they expose a
`to_disk` or `from_disk` method and if so, call it with the path to the pipeline
directory plus the string name of the component. For example, if you're calling
`nlp.to_disk("/path")`, the data for the named entity recognizer will be saved
in `/path/ner`.

If you're using custom pipeline components that depend on external data – for
example, model weights or terminology lists – you can take advantage of spaCy's
built-in component serialization by making your custom component expose its own
`to_disk` and `from_disk` or `to_bytes` and `from_bytes` methods. When an `nlp`
object with the component in its pipeline is saved or loaded, the component will
then be able to serialize and deserialize itself.

<Infobox title="Custom components and data" emoji="📖">

For more details on how to work with pipeline components that depend on data
resources and manage data loading and initialization at training and runtime,
see the usage guide on initializing and serializing
[component data](/usage/processing-pipelines#component-data).

</Infobox>

The following example shows a custom component that keeps arbitrary
JSON-serializable data, allows the user to add to that data and saves and loads
the data to and from a JSON file.

> #### Real-world example
>
> To see custom serialization methods in action, check out the new
> [`EntityRuler`](/api/entityruler) component and its
> [source](%%GITHUB_SPACY/spacy/pipeline/entityruler.py). Patterns added to the
> component will be saved to a `.jsonl` file if the pipeline is serialized to
> disk, and to a bytestring if the pipeline is serialized to bytes. This allows
> saving out a pipeline with a rule-based entity recognizer and including all
> rules _with_ the component data.

```python
### {highlight="16-23,25-30"}
import json
from spacy import Language
from spacy.util import ensure_path

@Language.factory("my_component")
class CustomComponent:
    def __init__(self, nlp: Language, name: str = "my_component"):
        self.name = name
        self.data = []

    def __call__(self, doc):
        # Do something to the doc here
        return doc

    def add(self, data):
        # Add something to the component's data
        self.data.append(data)

    def to_disk(self, path, exclude=tuple()):
        # This will receive the directory path + /my_component
        path = ensure_path(path)
        if not path.exists():
            path.mkdir()
        data_path = path / "data.json"
        with data_path.open("w", encoding="utf8") as f:
            f.write(json.dumps(self.data))

    def from_disk(self, path, exclude=tuple()):
        # This will receive the directory path + /my_component
        data_path = path / "data.json"
        with data_path.open("r", encoding="utf8") as f:
            self.data = json.load(f)
        return self
```

After adding the component to the pipeline and adding some data to it, we can
serialize the `nlp` object to a directory, which will call the custom
component's `to_disk` method.

```python
### {highlight="2-4"}
nlp = spacy.load("en_core_web_sm")
my_component = nlp.add_pipe("my_component")
my_component.add({"hello": "world"})
nlp.to_disk("/path/to/pipeline")
```

The contents of the directory would then look like this.
`CustomComponent.to_disk` converted the data to a JSON string and saved it to a
file `data.json` in its subdirectory:

```yaml
### Directory structure {highlight="2-3"}
└── /path/to/pipeline
    ├── my_component     # data serialized by "my_component"
    │   └── data.json
    ├── ner              # data for "ner" component
    ├── parser           # data for "parser" component
    ├── tagger           # data for "tagger" component
    ├── vocab            # pipeline vocabulary
    ├── meta.json        # pipeline meta.json
    ├── config.cfg       # pipeline config
    └── tokenizer        # tokenization rules
```

When you load the data back in, spaCy will call the custom component's
`from_disk` method with the given file path, and the component can then load the
contents of `data.json`, convert them to a Python object and restore the
component state. The same works for other types of data, of course – for
instance, you could add a
[wrapper for a model](/usage/layers-architectures#frameworks) trained with a
different library like TensorFlow or PyTorch and make spaCy load its weights
automatically when you load the pipeline package.

<Infobox title="Important note on loading custom components" variant="warning">

When you load back a pipeline with custom components, make sure that the
components are **available** and that the
[`@Language.component`](/api/language#component) or
[`@Language.factory`](/api/language#factory) decorators are executed _before_
your pipeline is loaded back. Otherwise, spaCy won't know how to resolve the
string name of a component factory like `"my_component"` back to a function. For
more details, see the documentation on
[adding factories](/usage/processing-pipelines#custom-components-factories) or
use [entry points](#entry-points) to make your extension package expose your
custom components to spaCy automatically.

</Infobox>

<!-- ## Initializing components with data {#initialization new="3"} -->

## Using entry points {#entry-points new="2.1"}

Entry points let you expose parts of a Python package you write to other Python
packages. This lets one application easily customize the behavior of another, by
exposing an entry point in its `setup.py`. For a quick and fun intro to entry
points in Python, check out
[this excellent blog post](https://amir.rachum.com/blog/2017/07/28/python-entry-points/).
spaCy can load custom functions from several different entry points to add
pipeline component factories, language classes and other settings. To make spaCy
use your entry points, your package needs to expose them and it needs to be
installed in the same environment – that's it.

| Entry point                                                                    | Description                                                                                                                                                                                                                                              |
| ------------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [`spacy_factories`](#entry-points-components)                                  | Group of entry points for pipeline component factories, keyed by component name. Can be used to expose custom components defined by another package.                                                                                                     |
| [`spacy_languages`](#entry-points-languages)                                   | Group of entry points for custom [`Language` subclasses](/usage/linguistic-features#language-data), keyed by language shortcut.                                                                                                                          |
| `spacy_lookups` <Tag variant="new">2.2</Tag>                                   | Group of entry points for custom [`Lookups`](/api/lookups), including lemmatizer data. Used by spaCy's [`spacy-lookups-data`](https://github.com/explosion/spacy-lookups-data) package.                                                                  |
| [`spacy_displacy_colors`](#entry-points-displacy) <Tag variant="new">2.2</Tag> | Group of entry points of custom label colors for the [displaCy visualizer](/usage/visualizers#ent). The key name doesn't matter, but it should point to a dict of labels and color values. Useful for custom models that predict different entity types. |

### Custom components via entry points {#entry-points-components}

When you load a pipeline, spaCy will generally use its `config.cfg` to set up
the language class and construct the pipeline. The pipeline is specified as a
list of strings, e.g. `pipeline = ["tagger", "parser", "ner"]`. For each of
those strings, spaCy will call `nlp.add_pipe` and look up the name in all
factories defined by the decorators
[`@Language.component`](/api/language#component) and
[`@Language.factory`](/api/language#factory). This means that you have to import
your custom components _before_ loading the pipeline.

Using entry points, pipeline packages and extension packages can define their
own `"spacy_factories"`, which will be loaded automatically in the background
when the `Language` class is initialized. So if a user has your package
installed, they'll be able to use your components – even if they **don't import
them**!

To stick with the theme of
[this entry points blog post](https://amir.rachum.com/blog/2017/07/28/python-entry-points/),
consider the following custom spaCy
[pipeline component](/usage/processing-pipelines#custom-coponents) that prints a
snake when it's called:

> #### Package directory structure
>
> ```yaml
> ├── snek.py   # the extension code
> └── setup.py  # setup file for pip installation
> ```

```python
### snek.py
from spacy.language import Language

snek = """
    --..,_                     _,.--.
       `'.'.                .'`__ o  `;__. {text}
          '.'.            .'.'`  '---'`  `
            '.`'--....--'`.'
              `'--....--'`
"""

@Language.component("snek")
def snek_component(doc):
    print(snek.format(text=doc.text))
    return doc
```

Since it's a very complex and sophisticated module, you want to split it off
into its own package so you can version it and upload it to PyPi. You also want
your custom package to be able to define `pipeline = ["snek"]` in its
`config.cfg`. For that, you need to be able to tell spaCy where to find the
component `"snek"`. If you don't do this, spaCy will raise an error when you try
to load the pipeline because there's no built-in `"snek"` component. To add an
entry to the factories, you can now expose it in your `setup.py` via the
`entry_points` dictionary:

> #### Entry point syntax
>
> Python entry points for a group are formatted as a **list of strings**, with
> each string following the syntax of `name = module:object`. In this example,
> the created entry point is named `snek` and points to the function
> `snek_component` in the module `snek`, i.e. `snek.py`.

```python
### setup.py {highlight="5-7"}
from setuptools import setup

setup(
    name="snek",
    entry_points={
        "spacy_factories": ["snek = snek:snek_component"]
    }
)
```

The same package can expose multiple entry points, by the way. To make them
available to spaCy, all you need to do is install the package in your
environment:

```bash
$ python setup.py develop
```

spaCy is now able to create the pipeline component `"snek"` – even though you
never imported `snek_component`. When you save the
[`nlp.config`](/api/language#config) to disk, it includes an entry for your
`"snek"` component and any pipeline you train with this config will include the
component and know how to load it – if your `snek` package is installed.

> #### config.cfg (excerpt)
>
> ```diff
> [nlp]
> lang = "en"
> + pipeline = ["snek"]
>
> [components]
>
> + [components.snek]
> + factory = "snek"
> ```

```
>>> from spacy.lang.en import English
>>> nlp = English()
>>> nlp.add_pipe("snek")  # this now works! 🐍🎉
>>> doc = nlp("I am snek")
    --..,_                     _,.--.
       `'.'.                .'`__ o  `;__. I am snek
          '.'.            .'.'`  '---'`  `
            '.`'--....--'`.'
              `'--....--'`
```

Instead of making your snek component a simple
[stateless component](/usage/processing-pipelines#custom-components-simple), you
could also make it a
[factory](/usage/processing-pipelines#custom-components-factories) that takes
settings. Your users can then pass in an optional `config` when they add your
component to the pipeline and customize its appearance – for example, the
`snek_style`.

> #### config.cfg (excerpt)
>
> ```diff
> [components.snek]
> factory = "snek"
> + snek_style = "basic"
> ```

```python
SNEKS = {"basic": snek, "cute": cute_snek}  # collection of sneks

@Language.factory("snek", default_config={"snek_style": "basic"})
class SnekFactory:
    def __init__(self, nlp: Language, name: str, snek_style: str):
        self.nlp = nlp
        self.snek_style = snek_style
        self.snek = SNEKS[self.snek_style]

    def __call__(self, doc):
        print(self.snek)
        return doc
```

```diff
### setup.py
entry_points={
-   "spacy_factories": ["snek = snek:snek_component"]
+   "spacy_factories": ["snek = snek:SnekFactory"]
}
```

The factory can also implement other pipeline component methods like `to_disk`
and `from_disk` for serialization, or even `update` to make the component
trainable. If a component exposes a `from_disk` method and is included in a
pipeline, spaCy will call it on load. This lets you ship custom data with your
pipeline package. When you save out a pipeline using `nlp.to_disk` and the
component exposes a `to_disk` method, it will be called with the disk path.

```python
from spacy.util import ensure_path

def to_disk(self, path, exclude=tuple()):
    path = ensure_path(path)
    if not path.exists():
        path.mkdir()
    snek_path = path / "snek.txt"
    with snek_path.open("w", encoding="utf8") as snek_file:
        snek_file.write(self.snek)

def from_disk(self, path, exclude=tuple()):
    snek_path = path / "snek.txt"
    with snek_path.open("r", encoding="utf8") as snek_file:
        self.snek = snek_file.read()
    return self
```

The above example will serialize the current snake in a `snek.txt` in the data
directory. When a pipeline using the `snek` component is loaded, it will open
the `snek.txt` and make it available to the component.

### Custom language classes via entry points {#entry-points-languages}

To stay with the theme of the previous example and
[this blog post on entry points](https://amir.rachum.com/blog/2017/07/28/python-entry-points/),
let's imagine you wanted to implement your own `SnekLanguage` class for your
custom pipeline – but you don't necessarily want to modify spaCy's code to add a
language. In your package, you could then implement the following
[custom language subclass](/usage/linguistic-features#language-subclass):

```python
### snek.py
from spacy.language import Language

class SnekDefaults(Language.Defaults):
    stop_words = set(["sss", "hiss"])

class SnekLanguage(Language):
    lang = "snk"
    Defaults = SnekDefaults
```

Alongside the `spacy_factories`, there's also an entry point option for
`spacy_languages`, which maps language codes to language-specific `Language`
subclasses:

```diff
### setup.py
from setuptools import setup

setup(
    name="snek",
    entry_points={
        "spacy_factories": ["snek = snek:SnekFactory"],
+       "spacy_languages": ["snk = snek:SnekLanguage"]
    }
)
```

In spaCy, you can then load the custom `snk` language and it will be resolved to
`SnekLanguage` via the custom entry point. This is especially relevant for
pipeline packages you [train](/usage/training), which could then specify
`lang = snk` in their `config.cfg` without spaCy raising an error because the
language is not available in the core library.

### Custom displaCy colors via entry points {#entry-points-displacy new="2.2"}

If you're training a named entity recognition model for a custom domain, you may
end up training different labels that don't have pre-defined colors in the
[`displacy` visualizer](/usage/visualizers#ent). The `spacy_displacy_colors`
entry point lets you define a dictionary of entity labels mapped to their color
values. It's added to the pre-defined colors and can also overwrite existing
values.

> #### Domain-specific NER labels
>
> Good examples of pipelines with domain-specific label schemes are
> [scispaCy](/universe/project/scispacy) and
> [Blackstone](/universe/project/blackstone).

```python
### snek.py
displacy_colors = {"SNEK": "#3dff74", "HUMAN": "#cfc5ff"}
```

Given the above colors, the entry point can be defined as follows. Entry points
need to have a name, so we use the key `colors`. However, the name doesn't
matter and whatever is defined in the entry point group will be used.

```diff
### setup.py
from setuptools import setup

setup(
    name="snek",
    entry_points={
+       "spacy_displacy_colors": ["colors = snek:displacy_colors"]
    }
)
```

After installing the package, the custom colors will be used when visualizing
text with `displacy`. Whenever the label `SNEK` is assigned, it will be
displayed in `#3dff74`.

import DisplaCyEntSnekHtml from 'images/displacy-ent-snek.html'

<Iframe title="displaCy visualization of entities" html={DisplaCyEntSnekHtml} height={100} />

## Saving, loading and distributing trained pipelines {#models}

After training your pipeline, you'll usually want to save its state, and load it
back later. You can do this with the [`Language.to_disk`](/api/language#to_disk)
method:

```python
nlp.to_disk("./en_example_pipeline")
```

The directory will be created if it doesn't exist, and the whole pipeline data,
meta and configuration will be written out. To make the pipeline more convenient
to deploy, we recommend wrapping it as a [Python package](/api/cli#package).

<Accordion title="What’s the difference between the config.cfg and meta.json?" spaced id="models-meta-vs-config" spaced>

When you save a pipeline in spaCy v3.0+, two files will be exported: a
[`config.cfg`](/api/data-formats#config) based on
[`nlp.config`](/api/language#config) and a [`meta.json`](/api/data-formats#meta)
based on [`nlp.meta`](/api/language#meta).

- **config**: Configuration used to create the current `nlp` object, its
  pipeline components and models, as well as training settings and
  hyperparameters. Can include references to registered functions like
  [pipeline components](/usage/processing-pipelines#custom-components) or
  [model architectures](/api/architectures). Given a config, spaCy is able
  reconstruct the whole tree of objects and the `nlp` object. An exported config
  can also be used to [train a pipeline](/usage/training#config) with the same
  settings.
- **meta**: Meta information about the pipeline and the Python package, such as
  the author information, license, version, data sources and label scheme. This
  is mostly used for documentation purposes and for packaging pipelines. It has
  no impact on the functionality of the `nlp` object.

</Accordion>

<Project id="pipelines/tagger_parser_ud">

The easiest way to get started with an end-to-end workflow is to clone a
[project template](/usage/projects) and run it – for example, this template that
lets you train a **part-of-speech tagger** and **dependency parser** on a
Universal Dependencies treebank and generates an installable Python package.

</Project>

### Generating a pipeline package {#models-generating}

<Infobox title="Important note" variant="warning">

Pipeline packages are typically **not suitable** for the public
[pypi.python.org](https://pypi.python.org) directory, which is not designed for
binary data and files over 50 MB. However, if your company is running an
**internal installation** of PyPi, publishing your pipeline packages on there
can be a convenient way to share them with your team.

</Infobox>

spaCy comes with a handy CLI command that will create all required files, and
walk you through generating the meta data. You can also create the
[`meta.json`](/api/data-formats#meta) manually and place it in the data
directory, or supply a path to it using the `--meta` flag. For more info on
this, see the [`package`](/api/cli#package) docs.

> #### meta.json (example)
>
> ```json
> {
>   "name": "example_pipeline",
>   "lang": "en",
>   "version": "1.0.0",
>   "spacy_version": ">=2.0.0,<3.0.0",
>   "description": "Example pipeline for spaCy",
>   "author": "You",
>   "email": "you@example.com",
>   "license": "CC BY-SA 3.0"
> }
> ```

```cli
$ python -m spacy package ./en_example_pipeline ./packages
```

This command will create a pipeline package directory and will run
`python setup.py sdist` in that directory to create a binary `.whl` file or
`.tar.gz` archive of your package that can be installed using `pip install`.
Installing the binary wheel is usually more efficient.

```yaml
### Directory structure
└── /
    ├── MANIFEST.in                           # to include meta.json
    ├── meta.json                             # pipeline meta data
    ├── setup.py                              # setup file for pip installation
    ├── en_example_pipeline                   # pipeline directory
    │    ├── __init__.py                      # init for pip installation
    │    └── en_example_pipeline-1.0.0        # pipeline data
    │        ├── config.cfg                   # pipeline config
    │        ├── meta.json                    # pipeline meta
    │        └── ...                          # directories with component data
    └── dist
        └── en_example_pipeline-1.0.0.tar.gz  # installable package
```

You can also find templates for all files in the
[`cli/package.py` source](https://github.com/explosion/spacy/tree/master/spacy/cli/package.py).
If you're creating the package manually, keep in mind that the directories need
to be named according to the naming conventions of `lang_name` and
`lang_name-version`.

### Including custom functions and components {#models-custom}

If your pipeline includes
[custom components](/usage/processing-pipelines#custom-components), model
architectures or other [code](/usage/training#custom-code), those functions need
to be registered **before** your pipeline is loaded. Otherwise, spaCy won't know
how to create the objects referenced in the config. The
[`spacy package`](/api/cli#package) command lets you provide one or more paths
to Python files containing custom registered functions using the `--code`
argument.

> #### \_\_init\_\_.py (excerpt)
>
> ```python
> from . import functions
>
> def load(**overrides):
>    ...
> ```

```cli
$ python -m spacy package ./en_example_pipeline ./packages --code functions.py
```

The Python files will be copied over into the root of the package, and the
package's `__init__.py` will import them as modules. This ensures that functions
are registered when the pipeline is imported, e.g. when you call `spacy.load`. A
simple import is all that's needed to make registered functions available.

Make sure to include **all Python files** that are referenced in your custom
code, including modules imported by others. If your custom code depends on
**external packages**, make sure they're listed in the list of `"requirements"`
in your [`meta.json`](/api/data-formats#meta). For the majority of use cases,
registered functions should provide you with all customizations you need, from
custom components to custom model architectures and lifecycle hooks. However, if
you do want to customize the setup in more detail, you can edit the package's
`__init__.py` and the package's `load` function that's called by
[`spacy.load`](/api/top-level#spacy.load).

<Infobox variant="warning" title="Important note on making manual edits">

While it's no problem to edit the package code or meta information, avoid making
edits to the `config.cfg` **after** training, as this can easily lead to data
incompatibility. For instance, changing an architecture or hyperparameter can
mean that the trained weights are now incompatible. If you want to make
adjustments, you can do so before training. Otherwise, you should always trust
spaCy to export the current state of its `nlp` objects via
[`nlp.config`](/api/language#config).

</Infobox>

### Loading a custom pipeline package {#loading}

To load a pipeline from a data directory, you can use
[`spacy.load()`](/api/top-level#spacy.load) with the local path. This will look
for a `config.cfg` in the directory and use the `lang` and `pipeline` settings
to initialize a `Language` class with a processing pipeline and load in the
model data.

```python
nlp = spacy.load("/path/to/pipeline")
```

If you want to **load only the binary data**, you'll have to create a `Language`
class and call [`from_disk`](/api/language#from_disk) instead.

```python
nlp = spacy.blank("en").from_disk("/path/to/data")
```
