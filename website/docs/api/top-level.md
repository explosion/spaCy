---
title: Top-level Functions
menu:
  - ['spacy', 'spacy']
  - ['displacy', 'displacy']
  - ['Data & Alignment', 'gold']
  - ['Utility Functions', 'util']
---

## spaCy {#spacy hidden="true"}

### spacy.load {#spacy.load tag="function" model="any"}

Load a model using the name of an installed
[model package](/usage/training#models-generating), a string path or a
`Path`-like object. spaCy will try resolving the load argument in this order. If
a model is loaded from a model name, spaCy will assume it's a Python package and
import it and call the model's own `load()` method. If a model is loaded from a
path, spaCy will assume it's a data directory, read the language and pipeline
settings off the meta.json and initialize the `Language` class. The data will be
loaded in via [`Language.from_disk`](/api/language#from_disk).

> #### Example
>
> ```python
> nlp = spacy.load("en_core_web_sm") # package
> nlp = spacy.load("/path/to/en") # string path
> nlp = spacy.load(Path("/path/to/en")) # pathlib Path
>
> nlp = spacy.load("en_core_web_sm", disable=["parser", "tagger"])
> ```

| Name        | Type         | Description                                                                       |
| ----------- | ------------ | --------------------------------------------------------------------------------- |
| `name`      | str / `Path` | Model to load, i.e. package name or path.                                         |
| `disable`   | list         | Names of pipeline components to [disable](/usage/processing-pipelines#disabling). |
| **RETURNS** | `Language`   | A `Language` object with the loaded model.                                        |

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
| `name`      | str        | [ISO code](https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes) of the language class to load. |
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
> spacy.info("en_core_web_sm")
> spacy.info(markdown=True)
> ```

| Name       | Type | Description                                      |
| ---------- | ---- | ------------------------------------------------ |
| `model`    | str  | A model, i.e. a package name or path (optional). |
| `markdown` | bool | Print information as Markdown.                   |

### spacy.explain {#spacy.explain tag="function"}

Get a description for a given POS tag, dependency label or entity type. For a
list of available terms, see
[`glossary.py`](https://github.com/explosion/spaCy/tree/master/spacy/glossary.py).

> #### Example
>
> ```python
> spacy.explain("NORP")
> # Nationalities or religious or political groups
>
> doc = nlp("Hello world")
> for word in doc:
>    print(word.text, word.tag_, spacy.explain(word.tag_))
> # Hello UH interjection
> # world NN noun, singular or mass
> ```

| Name        | Type | Description                                              |
| ----------- | ---- | -------------------------------------------------------- |
| `term`      | str  | Term to explain.                                         |
| **RETURNS** | str  | The explanation, or `None` if not found in the glossary. |

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
> doc1 = nlp("This is a sentence.")
> doc2 = nlp("This is another sentence.")
> displacy.serve([doc1, doc2], style="dep")
> ```

| Name      | Type                | Description                                                                                                                          | Default     |
| --------- | ------------------- | ------------------------------------------------------------------------------------------------------------------------------------ | ----------- |
| `docs`    | list, `Doc`, `Span` | Document(s) to visualize.                                                                                                            |
| `style`   | str                 | Visualization style, `'dep'` or `'ent'`.                                                                                             | `'dep'`     |
| `page`    | bool                | Render markup as full HTML page.                                                                                                     | `True`      |
| `minify`  | bool                | Minify HTML markup.                                                                                                                  | `False`     |
| `options` | dict                | [Visualizer-specific options](#displacy_options), e.g. colors.                                                                       | `{}`        |
| `manual`  | bool                | Don't parse `Doc` and instead, expect a dict or list of dicts. [See here](/usage/visualizers#manual-usage) for formats and examples. | `False`     |
| `port`    | int                 | Port to serve visualization.                                                                                                         | `5000`      |
| `host`    | str                 | Host to serve visualization.                                                                                                         | `'0.0.0.0'` |

### displacy.render {#displacy.render tag="method" new="2"}

Render a dependency parse tree or named entity visualization.

> #### Example
>
> ```python
> import spacy
> from spacy import displacy
> nlp = spacy.load("en_core_web_sm")
> doc = nlp("This is a sentence.")
> html = displacy.render(doc, style="dep")
> ```

| Name        | Type                | Description                                                                                                                                               | Default |
| ----------- | ------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------- | ------- |
| `docs`      | list, `Doc`, `Span` | Document(s) to visualize.                                                                                                                                 |
| `style`     | str                 | Visualization style, `'dep'` or `'ent'`.                                                                                                                  | `'dep'` |
| `page`      | bool                | Render markup as full HTML page.                                                                                                                          | `False` |
| `minify`    | bool                | Minify HTML markup.                                                                                                                                       | `False` |
| `jupyter`   | bool                | Explicitly enable or disable "[Jupyter](http://jupyter.org/) mode" to return markup ready to be rendered in a notebook. Detected automatically if `None`. | `None`  |
| `options`   | dict                | [Visualizer-specific options](#displacy_options), e.g. colors.                                                                                            | `{}`    |
| `manual`    | bool                | Don't parse `Doc` and instead, expect a dict or list of dicts. [See here](/usage/visualizers#manual-usage) for formats and examples.                      | `False` |
| **RETURNS** | str                 | Rendered HTML markup.                                                                                                                                     |

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

| Name                                       | Type | Description                                                                                                     | Default                 |
| ------------------------------------------ | ---- | --------------------------------------------------------------------------------------------------------------- | ----------------------- |
| `fine_grained`                             | bool | Use fine-grained part-of-speech tags (`Token.tag_`) instead of coarse-grained tags (`Token.pos_`).              | `False`                 |
| `add_lemma` <Tag variant="new">2.2.4</Tag> | bool | Print the lemma's in a separate row below the token texts.                                                      | `False`                 |
| `collapse_punct`                           | bool | Attach punctuation to tokens. Can make the parse more readable, as it prevents long arcs to attach punctuation. | `True`                  |
| `collapse_phrases`                         | bool | Merge noun phrases into one token.                                                                              | `False`                 |
| `compact`                                  | bool | "Compact mode" with square arrows that takes up less space.                                                     | `False`                 |
| `color`                                    | str  | Text color (HEX, RGB or color names).                                                                           | `'#000000'`             |
| `bg`                                       | str  | Background color (HEX, RGB or color names).                                                                     | `'#ffffff'`             |
| `font`                                     | str  | Font name or font family for all text.                                                                          | `'Arial'`               |
| `offset_x`                                 | int  | Spacing on left side of the SVG in px.                                                                          | `50`                    |
| `arrow_stroke`                             | int  | Width of arrow path in px.                                                                                      | `2`                     |
| `arrow_width`                              | int  | Width of arrow head in px.                                                                                      | `10` / `8` (compact)    |
| `arrow_spacing`                            | int  | Spacing between arrows in px to avoid overlaps.                                                                 | `20` / `12` (compact)   |
| `word_spacing`                             | int  | Vertical spacing between words and arcs in px.                                                                  | `45`                    |
| `distance`                                 | int  | Distance between words in px.                                                                                   | `175` / `150` (compact) |

#### Named Entity Visualizer options {#displacy_options-ent}

> #### Example
>
> ```python
> options = {"ents": ["PERSON", "ORG", "PRODUCT"],
>            "colors": {"ORG": "yellow"}}
> displacy.serve(doc, style="ent", options=options)
> ```

| Name                                    | Type | Description                                                                                                                                | Default                                                                                          |
| --------------------------------------- | ---- | ------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------ |
| `ents`                                  | list | Entity types to highlight (`None` for all types).                                                                                          | `None`                                                                                           |
| `colors`                                | dict | Color overrides. Entity types in uppercase should be mapped to color names or values.                                                      | `{}`                                                                                             |
| `template` <Tag variant="new">2.2</Tag> | str  | Optional template to overwrite the HTML used to render entity spans. Should be a format string and can use `{bg}`, `{text}` and `{label}`. | see [`templates.py`](https://github.com/explosion/spaCy/blob/master/spacy/displacy/templates.py) |

By default, displaCy comes with colors for all
[entity types supported by spaCy](/api/annotation#named-entities). If you're
using custom entity types, you can use the `colors` setting to add your own
colors for them. Your application or model package can also expose a
[`spacy_displacy_colors` entry point](/usage/saving-loading#entry-points-displacy)
to add custom labels and their colors automatically.

## Training data and alignment {#gold source="spacy/gold"}

### gold.docs_to_json {#docs_to_json tag="function"}

Convert a list of Doc objects into the
[JSON-serializable format](/api/annotation#json-input) used by the
[`spacy train`](/api/cli#train) command. Each input doc will be treated as a
'paragraph' in the output doc.

> #### Example
>
> ```python
> from spacy.gold import docs_to_json
>
> doc = nlp("I like London")
> json_data = docs_to_json([doc])
> ```

| Name        | Type             | Description                                |
| ----------- | ---------------- | ------------------------------------------ |
| `docs`      | iterable / `Doc` | The `Doc` object(s) to convert.            |
| `id`        | int              | ID to assign to the JSON. Defaults to `0`. |
| **RETURNS** | dict             | The data in spaCy's JSON format.           |

### gold.align {#align tag="function"}

Calculate alignment tables between two tokenizations, using the Levenshtein
algorithm. The alignment is case-insensitive.

<Infobox title="Important note" variant="warning">

The current implementation of the alignment algorithm assumes that both
tokenizations add up to the same string. For example, you'll be able to align
`["I", "'", "m"]` and `["I", "'m"]`, which both add up to `"I'm"`, but not
`["I", "'m"]` and `["I", "am"]`.

</Infobox>

> #### Example
>
> ```python
> from spacy.gold import align
>
> bert_tokens = ["obama", "'", "s", "podcast"]
> spacy_tokens = ["obama", "'s", "podcast"]
> alignment = align(bert_tokens, spacy_tokens)
> cost, a2b, b2a, a2b_multi, b2a_multi = alignment
> ```

| Name        | Type  | Description                                                                |
| ----------- | ----- | -------------------------------------------------------------------------- |
| `tokens_a`  | list  | String values of candidate tokens to align.                                |
| `tokens_b`  | list  | String values of reference tokens to align.                                |
| **RETURNS** | tuple | A `(cost, a2b, b2a, a2b_multi, b2a_multi)` tuple describing the alignment. |

The returned tuple contains the following alignment information:

> #### Example
>
> ```python
> a2b = array([0, -1, -1, 2])
> b2a = array([0, 2, 3])
> a2b_multi = {1: 1, 2: 1}
> b2a_multi = {}
> ```
>
> If `a2b[3] == 2`, that means that `tokens_a[3]` aligns to `tokens_b[2]`. If
> there's no one-to-one alignment for a token, it has the value `-1`.

| Name        | Type                                   | Description                                                                                                                                     |
| ----------- | -------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| `cost`      | int                                    | The number of misaligned tokens.                                                                                                                |
| `a2b`       | `numpy.ndarray[ndim=1, dtype='int32']` | One-to-one mappings of indices in `tokens_a` to indices in `tokens_b`.                                                                          |
| `b2a`       | `numpy.ndarray[ndim=1, dtype='int32']` | One-to-one mappings of indices in `tokens_b` to indices in `tokens_a`.                                                                          |
| `a2b_multi` | dict                                   | A dictionary mapping indices in `tokens_a` to indices in `tokens_b`, where multiple tokens of `tokens_a` align to the same token of `tokens_b`. |
| `b2a_multi` | dict                                   | A dictionary mapping indices in `tokens_b` to indices in `tokens_a`, where multiple tokens of `tokens_b` align to the same token of `tokens_a`. |

### gold.biluo_tags_from_offsets {#biluo_tags_from_offsets tag="function"}

Encode labelled spans into per-token tags, using the
[BILUO scheme](/api/annotation#biluo) (Begin, In, Last, Unit, Out). Returns a
list of strings, describing the tags. Each tag string will be of the form of
either `""`, `"O"` or `"{action}-{label}"`, where action is one of `"B"`, `"I"`,
`"L"`, `"U"`. The string `"-"` is used where the entity offsets don't align with
the tokenization in the `Doc` object. The training algorithm will view these as
missing values. `O` denotes a non-entity token. `B` denotes the beginning of a
multi-token entity, `I` the inside of an entity of three or more tokens, and `L`
the end of an entity of two or more tokens. `U` denotes a single-token entity.

> #### Example
>
> ```python
> from spacy.gold import biluo_tags_from_offsets
>
> doc = nlp("I like London.")
> entities = [(7, 13, "LOC")]
> tags = biluo_tags_from_offsets(doc, entities)
> assert tags == ["O", "O", "U-LOC", "O"]
> ```

| Name        | Type     | Description                                                                                                                                     |
| ----------- | -------- | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| `doc`       | `Doc`    | The document that the entity offsets refer to. The output tags will refer to the token boundaries within the document.                          |
| `entities`  | iterable | A sequence of `(start, end, label)` triples. `start` and `end` should be character-offset integers denoting the slice into the original string. |
| **RETURNS** | list     | str strings, describing the [BILUO](/api/annotation#biluo) tags.                                                                                |

### gold.offsets_from_biluo_tags {#offsets_from_biluo_tags tag="function"}

Encode per-token tags following the [BILUO scheme](/api/annotation#biluo) into
entity offsets.

> #### Example
>
> ```python
> from spacy.gold import offsets_from_biluo_tags
>
> doc = nlp("I like London.")
> tags = ["O", "O", "U-LOC", "O"]
> entities = offsets_from_biluo_tags(doc, tags)
> assert entities == [(7, 13, "LOC")]
> ```

| Name        | Type     | Description                                                                                                                                                                                                                 |
| ----------- | -------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `doc`       | `Doc`    | The document that the BILUO tags refer to.                                                                                                                                                                                  |
| `entities`  | iterable | A sequence of [BILUO](/api/annotation#biluo) tags with each tag describing one token. Each tag string will be of the form of either `""`, `"O"` or `"{action}-{label}"`, where action is one of `"B"`, `"I"`, `"L"`, `"U"`. |
| **RETURNS** | list     | A sequence of `(start, end, label)` triples. `start` and `end` will be character-offset integers denoting the slice into the original string.                                                                               |

### gold.spans_from_biluo_tags {#spans_from_biluo_tags tag="function" new="2.1"}

Encode per-token tags following the [BILUO scheme](/api/annotation#biluo) into
[`Span`](/api/span) objects. This can be used to create entity spans from
token-based tags, e.g. to overwrite the `doc.ents`.

> #### Example
>
> ```python
> from spacy.gold import spans_from_biluo_tags
>
> doc = nlp("I like London.")
> tags = ["O", "O", "U-LOC", "O"]
> doc.ents = spans_from_biluo_tags(doc, tags)
> ```

| Name        | Type     | Description                                                                                                                                                                                                                 |
| ----------- | -------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `doc`       | `Doc`    | The document that the BILUO tags refer to.                                                                                                                                                                                  |
| `entities`  | iterable | A sequence of [BILUO](/api/annotation#biluo) tags with each tag describing one token. Each tag string will be of the form of either `""`, `"O"` or `"{action}-{label}"`, where action is one of `"B"`, `"I"`, `"L"`, `"U"`. |
| **RETURNS** | list     | A sequence of `Span` objects with added entity labels.                                                                                                                                                                      |

## Utility functions {#util source="spacy/util.py"}

spaCy comes with a small collection of utility functions located in
[`spacy/util.py`](https://github.com/explosion/spaCy/tree/master/spacy/util.py).
Because utility functions are mostly intended for **internal use within spaCy**,
their behavior may change with future releases. The functions documented on this
page should be safe to use and we'll try to ensure backwards compatibility.
However, we recommend having additional tests in place if your application
depends on any of spaCy's utilities.

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
| `lang`      | str        | Two-letter language code, e.g. `'en'`. |
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
| `name` | str        | Two-letter language code, e.g. `'en'`. |
| `cls`  | `Language` | The language class, e.g. `English`.    |

### util.lang_class_is_loaded {#util.lang_class_is_loaded tag="function" new="2.1"}

Check whether a `Language` class is already loaded. `Language` classes are
loaded lazily, to avoid expensive setup code associated with the language data.

> #### Example
>
> ```python
> lang_cls = util.get_lang_class("en")
> assert util.lang_class_is_loaded("en") is True
> assert util.lang_class_is_loaded("de") is False
> ```

| Name        | Type | Description                            |
| ----------- | ---- | -------------------------------------- |
| `name`      | str  | Two-letter language code, e.g. `'en'`. |
| **RETURNS** | bool | Whether the class has been loaded.     |

### util.load_model {#util.load_model tag="function" new="2"}

Load a model from a package or data path. If called with a package name, spaCy
will assume the model is a Python package and import and call its `load()`
method. If called with a path, spaCy will assume it's a data directory, read the
language and pipeline settings from the meta.json and initialize a `Language`
class. The model data will then be loaded in via
[`Language.from_disk()`](/api/language#from_disk).

> #### Example
>
> ```python
> nlp = util.load_model("en_core_web_sm")
> nlp = util.load_model("en_core_web_sm", disable=["ner"])
> nlp = util.load_model("/path/to/data")
> ```

| Name          | Type       | Description                                              |
| ------------- | ---------- | -------------------------------------------------------- |
| `name`        | str        | Package name or model path.                              |
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
| `model_path`  | str        | Path to model data directory.                                                                        |
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
| `init_file`   | str        | Path to model's `__init__.py`, i.e. `__file__`.          |
| `**overrides` | -          | Specific overrides, like pipeline components to disable. |
| **RETURNS**   | `Language` | `Language` class with the loaded model.                  |

### util.get_model_meta {#util.get_model_meta tag="function" new="2"}

Get a model's meta.json from a directory path and validate its contents.

> #### Example
>
> ```python
> meta = util.get_model_meta("/path/to/model")
> ```

| Name        | Type         | Description              |
| ----------- | ------------ | ------------------------ |
| `path`      | str / `Path` | Path to model directory. |
| **RETURNS** | dict         | The model's meta data.   |

### util.is_package {#util.is_package tag="function"}

Check if string maps to a package installed via pip. Mainly used to validate
[model packages](/usage/models).

> #### Example
>
> ```python
> util.is_package("en_core_web_sm") # True
> util.is_package("xyz") # False
> ```

| Name        | Type   | Description                                  |
| ----------- | ------ | -------------------------------------------- |
| `name`      | str    | Name of package.                             |
| **RETURNS** | `bool` | `True` if installed package, `False` if not. |

### util.get_package_path {#util.get_package_path tag="function" new="2"}

Get path to an installed package. Mainly used to resolve the location of
[model packages](/usage/models). Currently imports the package to find its path.

> #### Example
>
> ```python
> util.get_package_path("en_core_web_sm")
> # /usr/lib/python3.6/site-packages/en_core_web_sm
> ```

| Name           | Type   | Description                      |
| -------------- | ------ | -------------------------------- |
| `package_name` | str    | Name of installed package.       |
| **RETURNS**    | `Path` | Path to model package directory. |

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
> NEW = {"a.": [{ORTH: "a.", NORM: "all"}]}
> exceptions = util.update_exc(BASE, NEW)
> # {"a.": [{ORTH: "a.", NORM: "all"}], ":)": [{ORTH: ":)"}]}
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

| Name       | Type           | Description            |
| ---------- | -------------- | ---------------------- |
| `items`    | iterable       | The items to batch up. |
| `size`     | int / iterable | The batch size(s).     |
| **YIELDS** | list           | The batches.           |

### util.filter_spans {#util.filter_spans tag="function" new="2.1.4"}

Filter a sequence of [`Span`](/api/span) objects and remove duplicates or
overlaps. Useful for creating named entities (where one token can only be part
of one entity) or when merging spans with
[`Retokenizer.merge`](/api/doc#retokenizer.merge). When spans overlap, the
(first) longest span is preferred over shorter spans.

> #### Example
>
> ```python
> doc = nlp("This is a sentence.")
> spans = [doc[0:2], doc[0:2], doc[0:4]]
> filtered = filter_spans(spans)
> ```

| Name        | Type     | Description          |
| ----------- | -------- | -------------------- |
| `spans`     | iterable | The spans to filter. |
| **RETURNS** | list     | The filtered spans.  |

## util.get_words_and_spaces {#get_words_and_spaces tag="function" new="3"}

<!-- TODO: document -->

| Name        | Type  | Description |
| ----------- | ----- | ----------- |
| `words`     | list  |             |
| `text`      | str   |             |
| **RETURNS** | tuple |             |
