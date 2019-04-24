---
title: Top-level Functions
menu:
  - ['spacy', 'spacy']
  - ['displacy', 'displacy']
  - ['Utility Functions', 'util']
  - ['Compatibility', 'compat']
---

## spaCy {#spacy hidden="true"}

### spacy.load {#spacy.load tag="function" model="any"}

Load a model via its [shortcut link](/usage/models#usage), the name of an
installed [model package](/usage/training#models-generating), a unicode path or
a `Path`-like object. spaCy will try resolving the load argument in this order.
If a model is loaded from a shortcut link or package name, spaCy will assume
it's a Python package and import it and call the model's own `load()` method. If
a model is loaded from a path, spaCy will assume it's a data directory, read the
language and pipeline settings off the meta.json and initialize the `Language`
class. The data will be loaded in via
[`Language.from_disk`](/api/language#from_disk).

> #### Example
>
> ```python
> nlp = spacy.load("en") # shortcut link
> nlp = spacy.load("en_core_web_sm") # package
> nlp = spacy.load("/path/to/en") # unicode path
> nlp = spacy.load(Path("/path/to/en")) # pathlib Path
>
> nlp = spacy.load("en", disable=["parser", "tagger"])
> ```

| Name        | Type             | Description                                                                       |
| ----------- | ---------------- | --------------------------------------------------------------------------------- |
| `name`      | unicode / `Path` | Model to load, i.e. shortcut link, package name or path.                          |
| `disable`   | list             | Names of pipeline components to [disable](/usage/processing-pipelines#disabling). |
| **RETURNS** | `Language`       | A `Language` object with the loaded model.                                        |

Essentially, `spacy.load()` is a convenience wrapper that reads the language ID
and pipeline components from a model's `meta.json`, initializes the `Language`
class, loads in the model data and returns it.

```python
### Abstract example
cls = util.get_lang_class(lang)         #  get language for ID, e.g. 'en'
nlp = cls()                             #  initialise the language
for name in pipeline: component = nlp.create_pipe(name)   #  create each pipeline component nlp.add_pipe(component)             #  add component to pipeline
nlp.from_disk(model_data_path)          #  load in model data
```

<Infobox title="Changed in v2.0" variant="warning">

As of spaCy 2.0, the `path` keyword argument is deprecated. spaCy will also
raise an error if no model could be loaded and never just return an empty
`Language` object. If you need a blank language, you can use the new function
[`spacy.blank()`](/api/top-level#spacy.blank) or import the class explicitly,
e.g. `from spacy.lang.en import English`.

```diff
- nlp = spacy.load("en", path="/model")
+ nlp = spacy.load("/model")
```

</Infobox>

### spacy.blank {#spacy.blank tag="function" new="2"}

Create a blank model of a given language class. This function is the twin of
`spacy.load()`.

> #### Example
>
> ```python
> nlp_en = spacy.blank("en")
> nlp_de = spacy.blank("de")
> ```

| Name        | Type       | Description                                                                                      |
| ----------- | ---------- | ------------------------------------------------------------------------------------------------ |
| `name`      | unicode    | [ISO code](https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes) of the language class to load. |
| `disable`   | list       | Names of pipeline components to [disable](/usage/processing-pipelines#disabling).                |
| **RETURNS** | `Language` | An empty `Language` object of the appropriate subclass.                                          |

#### spacy.info {#spacy.info tag="function"}

The same as the [`info` command](/api/cli#info). Pretty-print information about
your installation, models and local setup from within spaCy. To get the model
meta data as a dictionary instead, you can use the `meta` attribute on your
`nlp` object with a loaded model, e.g. `nlp.meta`.

> #### Example
>
> ```python
> spacy.info()
> spacy.info("en")
> spacy.info("de", markdown=True)
> ```

| Name       | Type    | Description                                                   |
| ---------- | ------- | ------------------------------------------------------------- |
| `model`    | unicode | A model, i.e. shortcut link, package name or path (optional). |
| `markdown` | bool    | Print information as Markdown.                                |

### spacy.explain {#spacy.explain tag="function"}

Get a description for a given POS tag, dependency label or entity type. For a
list of available terms, see
[`glossary.py`](https://github.com/explosion/spaCy/tree/master/spacy/glossary.py).

> #### Example
>
> ```python
> spacy.explain(u"NORP")
> # Nationalities or religious or political groups
>
> doc = nlp(u"Hello world")
> for word in doc:
>    print(word.text, word.tag_, spacy.explain(word.tag_))
> # Hello UH interjection
> # world NN noun, singular or mass
> ```

| Name        | Type    | Description                                              |
| ----------- | ------- | -------------------------------------------------------- |
| `term`      | unicode | Term to explain.                                         |
| **RETURNS** | unicode | The explanation, or `None` if not found in the glossary. |

### spacy.prefer_gpu {#spacy.prefer_gpu tag="function" new="2.0.14"}

Allocate data and perform operations on [GPU](/usage/#gpu), if available. If
data has already been allocated on CPU, it will not be moved. Ideally, this
function should be called right after importing spaCy and _before_ loading any
models.

> #### Example
>
> ```python
> import spacy
> activated = spacy.prefer_gpu()
> nlp = spacy.load("en_core_web_sm")
> ```

| Name        | Type | Description                    |
| ----------- | ---- | ------------------------------ |
| **RETURNS** | bool | Whether the GPU was activated. |

### spacy.require_gpu {#spacy.require_gpu tag="function" new="2.0.14"}

Allocate data and perform operations on [GPU](/usage/#gpu). Will raise an error
if no GPU is available. If data has already been allocated on CPU, it will not
be moved. Ideally, this function should be called right after importing spaCy
and _before_ loading any models.

> #### Example
>
> ```python
> import spacy
> spacy.require_gpu()
> nlp = spacy.load("en_core_web_sm")
> ```

| Name        | Type | Description |
| ----------- | ---- | ----------- |
| **RETURNS** | bool | `True`      |

## displaCy {#displacy source="spacy/displacy"}

As of v2.0, spaCy comes with a built-in visualization suite. For more info and
examples, see the usage guide on [visualizing spaCy](/usage/visualizers).

### displacy.serve {#displacy.serve tag="method" new="2"}

Serve a dependency parse tree or named entity visualization to view it in your
browser. Will run a simple web server.

> #### Example
>
> ```python
> import spacy
> from spacy import displacy
> nlp = spacy.load("en_core_web_sm")
> doc1 = nlp(u"This is a sentence.")
> doc2 = nlp(u"This is another sentence.")
> displacy.serve([doc1, doc2], style="dep")
> ```

| Name      | Type                | Description                                                                                                                          | Default     |
| --------- | ------------------- | ------------------------------------------------------------------------------------------------------------------------------------ | ----------- |
| `docs`    | list, `Doc`, `Span` | Document(s) to visualize.                                                                                                            |
| `style`   | unicode             | Visualization style, `'dep'` or `'ent'`.                                                                                             | `'dep'`     |
| `page`    | bool                | Render markup as full HTML page.                                                                                                     | `True`      |
| `minify`  | bool                | Minify HTML markup.                                                                                                                  | `False`     |
| `options` | dict                | [Visualizer-specific options](#options), e.g. colors.                                                                                | `{}`        |
| `manual`  | bool                | Don't parse `Doc` and instead, expect a dict or list of dicts. [See here](/usage/visualizers#manual-usage) for formats and examples. | `False`     |
| `port`    | int                 | Port to serve visualization.                                                                                                         | `5000`      |
| `host`    | unicode             | Host to serve visualization.                                                                                                         | `'0.0.0.0'` |

### displacy.render {#displacy.render tag="method" new="2"}

Render a dependency parse tree or named entity visualization.

> #### Example
>
> ```python
> import spacy
> from spacy import displacy
> nlp = spacy.load("en_core_web_sm")
> doc = nlp(u"This is a sentence.")
> html = displacy.render(doc, style="dep")
> ```

| Name        | Type                | Description                                                                                                                                               | Default |
| ----------- | ------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------- | ------- |
| `docs`      | list, `Doc`, `Span` | Document(s) to visualize.                                                                                                                                 |
| `style`     | unicode             | Visualization style, `'dep'` or `'ent'`.                                                                                                                  | `'dep'` |
| `page`      | bool                | Render markup as full HTML page.                                                                                                                          | `False` |
| `minify`    | bool                | Minify HTML markup.                                                                                                                                       | `False` |
| `jupyter`   | bool                | Explicitly enable or disable "[Jupyter](http://jupyter.org/) mode" to return markup ready to be rendered in a notebook. Detected automatically if `None`. | `None`  |
| `options`   | dict                | [Visualizer-specific options](#options), e.g. colors.                                                                                                     | `{}`    |
| `manual`    | bool                | Don't parse `Doc` and instead, expect a dict or list of dicts. [See here](/usage/visualizers#manual-usage) for formats and examples.                      | `False` |
| **RETURNS** | unicode             | Rendered HTML markup.                                                                                                                                     |

### Visualizer options {#displacy_options}

The `options` argument lets you specify additional settings for each visualizer.
If a setting is not present in the options, the default value will be used.

#### Dependency Visualizer options {#options-dep}

> #### Example
>
> ```python
> options = {"compact": True, "color": "blue"}
> displacy.serve(doc, style="dep", options=options)
> ```

| Name               | Type    | Description                                                                                                     | Default                 |
| ------------------ | ------- | --------------------------------------------------------------------------------------------------------------- | ----------------------- |
| `fine_grained`     | bool    | Use fine-grained part-of-speech tags (`Token.tag_`) instead of coarse-grained tags (`Token.pos_`).              | `False`                 |
| `collapse_punct`   | bool    | Attach punctuation to tokens. Can make the parse more readable, as it prevents long arcs to attach punctuation. | `True`                  |
| `collapse_phrases` | bool    | Merge noun phrases into one token.                                                                              | `False`                 |
| `compact`          | bool    | "Compact mode" with square arrows that takes up less space.                                                     | `False`                 |
| `color`            | unicode | Text color (HEX, RGB or color names).                                                                           | `'#000000'`             |
| `bg`               | unicode | Background color (HEX, RGB or color names).                                                                     | `'#ffffff'`             |
| `font`             | unicode | Font name or font family for all text.                                                                          | `'Arial'`               |
| `offset_x`         | int     | Spacing on left side of the SVG in px.                                                                          | `50`                    |
| `arrow_stroke`     | int     | Width of arrow path in px.                                                                                      | `2`                     |
| `arrow_width`      | int     | Width of arrow head in px.                                                                                      | `10` / `8` (compact)    |
| `arrow_spacing`    | int     | Spacing between arrows in px to avoid overlaps.                                                                 | `20` / `12` (compact)   |
| `word_spacing`     | int     | Vertical spacing between words and arcs in px.                                                                  | `45`                    |
| `distance`         | int     | Distance between words in px.                                                                                   | `175` / `150` (compact) |

#### Named Entity Visualizer options {#displacy_options-ent}

> #### Example
>
> ```python
> options = {"ents": ["PERSON", "ORG", "PRODUCT"],
>            "colors": {"ORG": "yellow"}}
> displacy.serve(doc, style="ent", options=options)
> ```

| Name     | Type | Description                                                                           | Default |
| -------- | ---- | ------------------------------------------------------------------------------------- | ------- |
| `ents`   | list | Entity types to highlight (`None` for all types).                                     | `None`  |
| `colors` | dict | Color overrides. Entity types in uppercase should be mapped to color names or values. | `{}`    |

By default, displaCy comes with colors for all
[entity types supported by spaCy](/api/annotation#named-entities). If you're
using custom entity types, you can use the `colors` setting to add your own
colors for them.

## Utility functions {#util source="spacy/util.py"}

spaCy comes with a small collection of utility functions located in
[`spacy/util.py`](https://github.com/explosion/spaCy/tree/master/spacy/util.py).
Because utility functions are mostly intended for **internal use within spaCy**,
their behavior may change with future releases. The functions documented on this
page should be safe to use and we'll try to ensure backwards compatibility.
However, we recommend having additional tests in place if your application
depends on any of spaCy's utilities.

### util.get_data_path {#util.get_data_path tag="function"}

Get path to the data directory where spaCy looks for models. Defaults to
`spacy/data`.

| Name             | Type            | Description                                             |
| ---------------- | --------------- | ------------------------------------------------------- |
| `require_exists` | bool            | Only return path if it exists, otherwise return `None`. |
| **RETURNS**      | `Path` / `None` | Data path or `None`.                                    |

### util.set_data_path {#util.set_data_path tag="function"}

Set custom path to the data directory where spaCy looks for models.

> #### Example
>
> ```python
> util.set_data_path("/custom/path")
> util.get_data_path()
> # PosixPath('/custom/path')
> ```

| Name   | Type             | Description                 |
| ------ | ---------------- | --------------------------- |
| `path` | unicode / `Path` | Path to new data directory. |

### util.get_lang_class {#util.get_lang_class tag="function"}

Import and load a `Language` class. Allows lazy-loading
[language data](/usage/adding-languages) and importing languages using the
two-letter language code. To add a language code for a custom language class,
you can use the [`set_lang_class`](/api/top-level#util.set_lang_class) helper.

> #### Example
>
> ```python
> for lang_id in ["en", "de"]:
>     lang_class = util.get_lang_class(lang_id)
>     lang = lang_class()
>     tokenizer = lang.Defaults.create_tokenizer()
> ```

| Name        | Type       | Description                            |
| ----------- | ---------- | -------------------------------------- |
| `lang`      | unicode    | Two-letter language code, e.g. `'en'`. |
| **RETURNS** | `Language` | Language class.                        |

### util.set_lang_class {#util.set_lang_class tag="function"}

Set a custom `Language` class name that can be loaded via
[`get_lang_class`](/api/top-level#util.get_lang_class). If your model uses a
custom language, this is required so that spaCy can load the correct class from
the two-letter language code.

> #### Example
>
> ```python
> from spacy.lang.xy import CustomLanguage
>
> util.set_lang_class('xy', CustomLanguage)
> lang_class = util.get_lang_class('xy')
> nlp = lang_class()
> ```

| Name   | Type       | Description                            |
| ------ | ---------- | -------------------------------------- |
| `name` | unicode    | Two-letter language code, e.g. `'en'`. |
| `cls`  | `Language` | The language class, e.g. `English`.    |

### util.lang_class_is_loaded (#util.lang_class_is_loaded tag="function" new="2.1")

Check whether a `Language` class is already loaded. `Language` classes are
loaded lazily, to avoid expensive setup code associated with the language data.

> #### Example
>
> ```python
> lang_cls = util.get_lang_class("en")
> assert util.lang_class_is_loaded("en") is True
> assert util.lang_class_is_loaded("de") is False
> ```

| Name        | Type    | Description                            |
| ----------- | ------- | -------------------------------------- |
| `name`      | unicode | Two-letter language code, e.g. `'en'`. |
| **RETURNS** | bool    | Whether the class has been loaded.     |

### util.load_model {#util.load_model tag="function" new="2"}

Load a model from a shortcut link, package or data path. If called with a
shortcut link or package name, spaCy will assume the model is a Python package
and import and call its `load()` method. If called with a path, spaCy will
assume it's a data directory, read the language and pipeline settings from the
meta.json and initialize a `Language` class. The model data will then be loaded
in via [`Language.from_disk()`](/api/language#from_disk).

> #### Example
>
> ```python
> nlp = util.load_model("en")
> nlp = util.load_model("en_core_web_sm", disable=["ner"])
> nlp = util.load_model("/path/to/data")
> ```

| Name          | Type       | Description                                              |
| ------------- | ---------- | -------------------------------------------------------- |
| `name`        | unicode    | Package name, shortcut link or model path.               |
| `**overrides` | -          | Specific overrides, like pipeline components to disable. |
| **RETURNS**   | `Language` | `Language` class with the loaded model.                  |

### util.load_model_from_path {#util.load_model_from_path tag="function" new="2"}

Load a model from a data directory path. Creates the [`Language`](/api/language)
class and pipeline based on the directory's meta.json and then calls
[`from_disk()`](/api/language#from_disk) with the path. This function also makes
it easy to test a new model that you haven't packaged yet.

> #### Example
>
> ```python
> nlp = load_model_from_path("/path/to/data")
> ```

| Name          | Type       | Description                                                                                          |
| ------------- | ---------- | ---------------------------------------------------------------------------------------------------- |
| `model_path`  | unicode    | Path to model data directory.                                                                        |
| `meta`        | dict       | Model meta data. If `False`, spaCy will try to load the meta from a meta.json in the same directory. |
| `**overrides` | -          | Specific overrides, like pipeline components to disable.                                             |
| **RETURNS**   | `Language` | `Language` class with the loaded model.                                                              |

### util.load_model_from_init_py {#util.load_model_from_init_py tag="function" new="2"}

A helper function to use in the `load()` method of a model package's
[`__init__.py`](https://github.com/explosion/spacy-models/tree/master/template/model/xx_model_name/__init__.py).

> #### Example
>
> ```python
> from spacy.util import load_model_from_init_py
>
> def load(**overrides):
>     return load_model_from_init_py(__file__, **overrides)
> ```

| Name          | Type       | Description                                              |
| ------------- | ---------- | -------------------------------------------------------- |
| `init_file`   | unicode    | Path to model's `__init__.py`, i.e. `__file__`.          |
| `**overrides` | -          | Specific overrides, like pipeline components to disable. |
| **RETURNS**   | `Language` | `Language` class with the loaded model.                  |

### util.get_model_meta {#util.get_model_meta tag="function" new="2"}

Get a model's meta.json from a directory path and validate its contents.

> #### Example
>
> ```python
> meta = util.get_model_meta("/path/to/model")
> ```

| Name        | Type             | Description              |
| ----------- | ---------------- | ------------------------ |
| `path`      | unicode / `Path` | Path to model directory. |
| **RETURNS** | dict             | The model's meta data.   |

### util.is_package {#util.is_package tag="function"}

Check if string maps to a package installed via pip. Mainly used to validate
[model packages](/usage/models).

> #### Example
>
> ```python
> util.is_package("en_core_web_sm") # True
> util.is_package("xyz") # False
> ```

| Name        | Type    | Description                                  |
| ----------- | ------- | -------------------------------------------- |
| `name`      | unicode | Name of package.                             |
| **RETURNS** | `bool`  | `True` if installed package, `False` if not. |

### util.get_package_path {#util.get_package_path tag="function" new="2"}

Get path to an installed package. Mainly used to resolve the location of
[model packages](/usage/models). Currently imports the package to find its path.

> #### Example
>
> ```python
> util.get_package_path("en_core_web_sm")
> # /usr/lib/python3.6/site-packages/en_core_web_sm
> ```

| Name           | Type    | Description                      |
| -------------- | ------- | -------------------------------- |
| `package_name` | unicode | Name of installed package.       |
| **RETURNS**    | `Path`  | Path to model package directory. |

### util.is_in_jupyter {#util.is_in_jupyter tag="function" new="2"}

Check if user is running spaCy from a [Jupyter](https://jupyter.org) notebook by
detecting the IPython kernel. Mainly used for the
[`displacy`](/api/top-level#displacy) visualizer.

> #### Example
>
> ```python
> html = "<h1>Hello world!</h1>"
> if util.is_in_jupyter():
>     from IPython.core.display import display, HTML
>     display(HTML(html))
> ```

| Name        | Type | Description                           |
| ----------- | ---- | ------------------------------------- |
| **RETURNS** | bool | `True` if in Jupyter, `False` if not. |

### util.update_exc {#util.update_exc tag="function"}

Update, validate and overwrite
[tokenizer exceptions](/usage/adding-languages#tokenizer-exceptions). Used to
combine global exceptions with custom, language-specific exceptions. Will raise
an error if key doesn't match `ORTH` values.

> #### Example
>
> ```python
> BASE =  {"a.": [{ORTH: "a."}], ":)": [{ORTH: ":)"}]}
> NEW = {"a.": [{ORTH: "a.", LEMMA: "all"}]}
> exceptions = util.update_exc(BASE, NEW)
> # {"a.": [{ORTH: "a.", LEMMA: "all"}], ":)": [{ORTH: ":)"}]}
> ```

| Name              | Type  | Description                                                     |
| ----------------- | ----- | --------------------------------------------------------------- |
| `base_exceptions` | dict  | Base tokenizer exceptions.                                      |
| `*addition_dicts` | dicts | Exception dictionaries to add to the base exceptions, in order. |
| **RETURNS**       | dict  | Combined tokenizer exceptions.                                  |

### util.compile_prefix_regex {#util.compile_prefix_regex tag="function"}

Compile a sequence of prefix rules into a regex object.

> #### Example
>
> ```python
> prefixes = ("§", "%", "=", r"\+")
> prefix_regex = util.compile_prefix_regex(prefixes)
> nlp.tokenizer.prefix_search = prefix_regex.search
> ```

| Name        | Type                                                          | Description                                                                                                                               |
| ----------- | ------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------- |
| `entries`   | tuple                                                         | The prefix rules, e.g. [`lang.punctuation.TOKENIZER_PREFIXES`](https://github.com/explosion/spaCy/tree/master/spacy/lang/punctuation.py). |
| **RETURNS** | [regex](https://docs.python.org/3/library/re.html#re-objects) | The regex object. to be used for [`Tokenizer.prefix_search`](/api/tokenizer#attributes).                                                  |

### util.compile_suffix_regex {#util.compile_suffix_regex tag="function"}

Compile a sequence of suffix rules into a regex object.

> #### Example
>
> ```python
> suffixes = ("'s", "'S", r"(?<=[0-9])\+")
> suffix_regex = util.compile_suffix_regex(suffixes)
> nlp.tokenizer.suffix_search = suffix_regex.search
> ```

| Name        | Type                                                          | Description                                                                                                                               |
| ----------- | ------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------- |
| `entries`   | tuple                                                         | The suffix rules, e.g. [`lang.punctuation.TOKENIZER_SUFFIXES`](https://github.com/explosion/spaCy/tree/master/spacy/lang/punctuation.py). |
| **RETURNS** | [regex](https://docs.python.org/3/library/re.html#re-objects) | The regex object. to be used for [`Tokenizer.suffix_search`](/api/tokenizer#attributes).                                                  |

### util.compile_infix_regex {#util.compile_infix_regex tag="function"}

Compile a sequence of infix rules into a regex object.

> #### Example
>
> ```python
> infixes = ("…", "-", "—", r"(?<=[0-9])[+\-\*^](?=[0-9-])")
> infix_regex = util.compile_infix_regex(infixes)
> nlp.tokenizer.infix_finditer = infix_regex.finditer
> ```

| Name        | Type                                                          | Description                                                                                                                             |
| ----------- | ------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------- |
| `entries`   | tuple                                                         | The infix rules, e.g. [`lang.punctuation.TOKENIZER_INFIXES`](https://github.com/explosion/spaCy/tree/master/spacy/lang/punctuation.py). |
| **RETURNS** | [regex](https://docs.python.org/3/library/re.html#re-objects) | The regex object. to be used for [`Tokenizer.infix_finditer`](/api/tokenizer#attributes).                                               |

### util.minibatch {#util.minibatch tag="function" new="2"}

Iterate over batches of items. `size` may be an iterator, so that batch-size can
vary on each step.

> #### Example
>
> ```python
> batches = minibatch(train_data)
> for batch in batches:
>     texts, annotations = zip(*batch)
>     nlp.update(texts, annotations)
> ```

| Name       | Type           | Description                                                                                                                                                                                  |
| ---------- | -------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `items`    | iterable       | The items to batch up.                                                                                                                                                                       |
| `size`     | int / iterable | The batch size(s). Use [`util.compounding`](/api/top-level#util.compounding) or [`util.decaying`](/api/top-level#util.decaying) or for an infinite series of compounding or decaying values. |
| **YIELDS** | list           | The batches.                                                                                                                                                                                 |

### util.compounding {#util.compounding tag="function" new="2"}

Yield an infinite series of compounding values. Each time the generator is
called, a value is produced by multiplying the previous value by the compound
rate.

> #### Example
>
> ```python
> sizes = compounding(1., 10., 1.5)
> assert next(sizes) == 1.
> assert next(sizes) == 1. * 1.5
> assert next(sizes) == 1.5 * 1.5
> ```

| Name       | Type        | Description             |
| ---------- | ----------- | ----------------------- |
| `start`    | int / float | The first value.        |
| `stop`     | int / float | The maximum value.      |
| `compound` | int / float | The compounding factor. |
| **YIELDS** | int         | Compounding values.     |

### util.decaying {#util.decaying tag="function" new="2"}

Yield an infinite series of linearly decaying values.

> #### Example
>
> ```python
> sizes = decaying(10., 1., 0.001)
> assert next(sizes) == 10.
> assert next(sizes) == 10. - 0.001
> assert next(sizes) == 9.999 - 0.001
> ```

| Name       | Type        | Description          |
| ---------- | ----------- | -------------------- |
| `start`    | int / float | The first value.     |
| `end`      | int / float | The maximum value.   |
| `decay`    | int / float | The decaying factor. |
| **YIELDS** | int         | The decaying values. |

### util.itershuffle {#util.itershuffle tag="function" new="2"}

Shuffle an iterator. This works by holding `bufsize` items back and yielding
them sometime later. Obviously, this is not unbiased – but should be good enough
for batching. Larger `buffsize` means less bias.

> #### Example
>
> ```python
> values = range(1000)
> shuffled = itershuffle(values)
> ```

| Name       | Type     | Description            |
| ---------- | -------- | ---------------------- |
| `iterable` | iterable | Iterator to shuffle.   |
| `buffsize` | int      | Items to hold back.    |
| **YIELDS** | iterable | The shuffled iterator. |

## Compatibility functions {#compat source="spacy/compaty.py"}

All Python code is written in an **intersection of Python 2 and Python 3**. This
is easy in Cython, but somewhat ugly in Python. Logic that deals with Python or
platform compatibility only lives in `spacy.compat`. To distinguish them from
the builtin functions, replacement functions are suffixed with an underscore,
e.g. `unicode_`.

> #### Example
>
> ```python
> from spacy.compat import unicode_
>
> compatible_unicode = unicode_("hello world")
> ```

| Name                 | Python 2                           | Python 3    |
| -------------------- | ---------------------------------- | ----------- |
| `compat.bytes_`      | `str`                              | `bytes`     |
| `compat.unicode_`    | `unicode`                          | `str`       |
| `compat.basestring_` | `basestring`                       | `str`       |
| `compat.input_`      | `raw_input`                        | `input`     |
| `compat.path2str`    | `str(path)` with `.decode('utf8')` | `str(path)` |

### compat.is_config {#compat.is_config tag="function"}

Check if a specific configuration of Python version and operating system matches
the user's setup. Mostly used to display targeted error messages.

> #### Example
>
> ```python
> from spacy.compat import is_config
>
> if is_config(python2=True, windows=True):
>     print("You are using Python 2 on Windows.")
> ```

| Name        | Type | Description                                                      |
| ----------- | ---- | ---------------------------------------------------------------- |
| `python2`   | bool | spaCy is executed with Python 2.x.                               |
| `python3`   | bool | spaCy is executed with Python 3.x.                               |
| `windows`   | bool | spaCy is executed on Windows.                                    |
| `linux`     | bool | spaCy is executed on Linux.                                      |
| `osx`       | bool | spaCy is executed on OS X or macOS.                              |
| **RETURNS** | bool | Whether the specified configuration matches the user's platform. |
