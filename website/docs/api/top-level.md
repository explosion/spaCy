---
title: Top-level Functions
menu:
  - ['spacy', 'spacy']
  - ['displacy', 'displacy']
  - ['registry', 'registry']
  - ['Loggers', 'loggers']
  - ['Readers', 'readers']
  - ['Batchers', 'batchers']
  - ['Augmenters', 'augmenters']
  - ['Callbacks', 'callbacks']
  - ['Training & Alignment', 'gold']
  - ['Utility Functions', 'util']
---

## spaCy {#spacy hidden="true"}

### spacy.load {#spacy.load tag="function"}

Load a pipeline using the name of an installed
[package](/usage/saving-loading#models), a string path or a `Path`-like object.
spaCy will try resolving the load argument in this order. If a pipeline is
loaded from a string name, spaCy will assume it's a Python package and import it
and call the package's own `load()` method. If a pipeline is loaded from a path,
spaCy will assume it's a data directory, load its
[`config.cfg`](/api/data-formats#config) and use the language and pipeline
information to construct the `Language` class. The data will be loaded in via
[`Language.from_disk`](/api/language#from_disk).

<Infobox variant="warning" title="Changed in v3.0">

As of v3.0, the `disable` keyword argument specifies components to load but
disable, instead of components to not load at all. Those components can now be
specified separately using the new `exclude` keyword argument.

</Infobox>

> #### Example
>
> ```python
> nlp = spacy.load("en_core_web_sm") # package
> nlp = spacy.load("/path/to/pipeline") # string path
> nlp = spacy.load(Path("/path/to/pipeline")) # pathlib Path
>
> nlp = spacy.load("en_core_web_sm", exclude=["parser", "tagger"])
> ```

| Name                                 | Description                                                                                                                                                                                                                                    |
| ------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `name`                               | Pipeline to load, i.e. package name or path. ~~Union[str, Path]~~                                                                                                                                                                              |
| _keyword-only_                       |                                                                                                                                                                                                                                                |
| `vocab`                              | Optional shared vocab to pass in on initialization. If `True` (default), a new `Vocab` object will be created. ~~Union[Vocab, bool]~~                                                                                                          |
| `disable`                            | Names of pipeline components to [disable](/usage/processing-pipelines#disabling). Disabled pipes will be loaded but they won't be run unless you explicitly enable them by calling [nlp.enable_pipe](/api/language#enable_pipe). ~~List[str]~~ |
| `enable`                             | Names of pipeline components to [enable](/usage/processing-pipelines#disabling). All other pipes will be disabled. ~~List[str]~~                                                                                                               |
| `exclude` <Tag variant="new">3</Tag> | Names of pipeline components to [exclude](/usage/processing-pipelines#disabling). Excluded components won't be loaded. ~~List[str]~~                                                                                                           |
| `config` <Tag variant="new">3</Tag>  | Optional config overrides, either as nested dict or dict keyed by section value in dot notation, e.g. `"components.name.value"`. ~~Union[Dict[str, Any], Config]~~                                                                             |
| **RETURNS**                          | A `Language` object with the loaded pipeline. ~~Language~~                                                                                                                                                                                     |

Essentially, `spacy.load()` is a convenience wrapper that reads the pipeline's
[`config.cfg`](/api/data-formats#config), uses the language and pipeline
information to construct a `Language` object, loads in the model data and
weights, and returns it.

```python
### Abstract example
cls = spacy.util.get_lang_class(lang)  # 1. Get Language class, e.g. English
nlp = cls()                            # 2. Initialize it
for name in pipeline:
    nlp.add_pipe(name)                 # 3. Add the component to the pipeline
nlp.from_disk(data_path)               # 4. Load in the binary data
```

### spacy.blank {#spacy.blank tag="function" new="2"}

Create a blank pipeline of a given language class. This function is the twin of
`spacy.load()`.

> #### Example
>
> ```python
> nlp_en = spacy.blank("en")   # equivalent to English()
> nlp_de = spacy.blank("de")   # equivalent to German()
> ```

| Name                                | Description                                                                                                                                                        |
| ----------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `name`                              | [IETF language tag](https://www.w3.org/International/articles/language-tags/), such as 'en', of the language class to load. ~~str~~                                |
| _keyword-only_                      |                                                                                                                                                                    |
| `vocab`                             | Optional shared vocab to pass in on initialization. If `True` (default), a new `Vocab` object will be created. ~~Union[Vocab, bool]~~                              |
| `config` <Tag variant="new">3</Tag> | Optional config overrides, either as nested dict or dict keyed by section value in dot notation, e.g. `"components.name.value"`. ~~Union[Dict[str, Any], Config]~~ |
| `meta`                              | Optional meta overrides for [`nlp.meta`](/api/language#meta). ~~Dict[str, Any]~~                                                                                   |
| **RETURNS**                         | An empty `Language` object of the appropriate subclass. ~~Language~~                                                                                               |

### spacy.info {#spacy.info tag="function"}

The same as the [`info` command](/api/cli#info). Pretty-print information about
your installation, installed pipelines and local setup from within spaCy.

> #### Example
>
> ```python
> spacy.info()
> spacy.info("en_core_web_sm")
> markdown = spacy.info(markdown=True, silent=True)
> ```

| Name           | Description                                                                  |
| -------------- | ---------------------------------------------------------------------------- |
| `model`        | Optional pipeline, i.e. a package name or path (optional). ~~Optional[str]~~ |
| _keyword-only_ |                                                                              |
| `markdown`     | Print information as Markdown. ~~bool~~                                      |
| `silent`       | Don't print anything, just return. ~~bool~~                                  |

### spacy.explain {#spacy.explain tag="function"}

Get a description for a given POS tag, dependency label or entity type. For a
list of available terms, see [`glossary.py`](%%GITHUB_SPACY/spacy/glossary.py).

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

| Name        | Description                                                                |
| ----------- | -------------------------------------------------------------------------- |
| `term`      | Term to explain. ~~str~~                                                   |
| **RETURNS** | The explanation, or `None` if not found in the glossary. ~~Optional[str]~~ |

### spacy.prefer_gpu {#spacy.prefer_gpu tag="function" new="2.0.14"}

Allocate data and perform operations on [GPU](/usage/#gpu), if available. If
data has already been allocated on CPU, it will not be moved. Ideally, this
function should be called right after importing spaCy and _before_ loading any
pipelines.

<Infobox variant="warning" title="Jupyter notebook usage">

In a Jupyter notebook, run `prefer_gpu()` in the same cell as `spacy.load()` to
ensure that the model is loaded on the correct device. See
[more details](/usage/v3#jupyter-notebook-gpu).

</Infobox>

> #### Example
>
> ```python
> import spacy
> activated = spacy.prefer_gpu()
> nlp = spacy.load("en_core_web_sm")
> ```

| Name        | Description                                      |
| ----------- | ------------------------------------------------ |
| `gpu_id`    | Device index to select. Defaults to `0`. ~~int~~ |
| **RETURNS** | Whether the GPU was activated. ~~bool~~          |

### spacy.require_gpu {#spacy.require_gpu tag="function" new="2.0.14"}

Allocate data and perform operations on [GPU](/usage/#gpu). Will raise an error
if no GPU is available. If data has already been allocated on CPU, it will not
be moved. Ideally, this function should be called right after importing spaCy
and _before_ loading any pipelines.

<Infobox variant="warning" title="Jupyter notebook usage">

In a Jupyter notebook, run `require_gpu()` in the same cell as `spacy.load()` to
ensure that the model is loaded on the correct device. See
[more details](/usage/v3#jupyter-notebook-gpu).

</Infobox>

> #### Example
>
> ```python
> import spacy
> spacy.require_gpu()
> nlp = spacy.load("en_core_web_sm")
> ```

| Name        | Description                                      |
| ----------- | ------------------------------------------------ |
| `gpu_id`    | Device index to select. Defaults to `0`. ~~int~~ |
| **RETURNS** | `True` ~~bool~~                                  |

### spacy.require_cpu {#spacy.require_cpu tag="function" new="3.0.0"}

Allocate data and perform operations on CPU. If data has already been allocated
on GPU, it will not be moved. Ideally, this function should be called right
after importing spaCy and _before_ loading any pipelines.

<Infobox variant="warning" title="Jupyter notebook usage">

In a Jupyter notebook, run `require_cpu()` in the same cell as `spacy.load()` to
ensure that the model is loaded on the correct device. See
[more details](/usage/v3#jupyter-notebook-gpu).

</Infobox>

> #### Example
>
> ```python
> import spacy
> spacy.require_cpu()
> nlp = spacy.load("en_core_web_sm")
> ```

| Name        | Description     |
| ----------- | --------------- |
| **RETURNS** | `True` ~~bool~~ |

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

| Name      | Description                                                                                                                                                       |
| --------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `docs`    | Document(s) or span(s) to visualize. ~~Union[Iterable[Union[Doc, Span]], Doc, Span]~~                                                                             |
| `style`   | Visualization style, `"dep"`, `"ent"` or `"span"` <Tag variant="new">3.3</Tag>. Defaults to `"dep"`. ~~str~~                                                                                             |
| `page`    | Render markup as full HTML page. Defaults to `True`. ~~bool~~                                                                                                     |
| `minify`  | Minify HTML markup. Defaults to `False`. ~~bool~~                                                                                                                 |
| `options` | [Visualizer-specific options](#displacy_options), e.g. colors. ~~Dict[str, Any]~~                                                                                 |
| `manual`  | Don't parse `Doc` and instead expect a dict or list of dicts. [See here](/usage/visualizers#manual-usage) for formats and examples. Defaults to `False`. ~~bool~~ |
| `port`    | Port to serve visualization. Defaults to `5000`. ~~int~~                                                                                                          |
| `host`    | Host to serve visualization. Defaults to `"0.0.0.0"`. ~~str~~                                                                                                     |

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

| Name        | Description                                                                                                                                                                            |
| ----------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `docs`      | Document(s) or span(s) to visualize. ~~Union[Iterable[Union[Doc, Span, dict]], Doc, Span, dict]~~                                                                                      |
| `style`     | Visualization style,`"dep"`, `"ent"` or `"span"` <Tag variant="new">3.3</Tag>. Defaults to `"dep"`. ~~str~~                                                                                                                  |
| `page`      | Render markup as full HTML page. Defaults to `True`. ~~bool~~                                                                                                                          |
| `minify`    | Minify HTML markup. Defaults to `False`. ~~bool~~                                                                                                                                      |
| `options`   | [Visualizer-specific options](#displacy_options), e.g. colors. ~~Dict[str, Any]~~                                                                                                      |
| `manual`    | Don't parse `Doc` and instead expect a dict or list of dicts. [See here](/usage/visualizers#manual-usage) for formats and examples. Defaults to `False`. ~~bool~~                      |
| `jupyter`   | Explicitly enable or disable "[Jupyter](http://jupyter.org/) mode" to return markup ready to be rendered in a notebook. Detected automatically if `None` (default). ~~Optional[bool]~~ |
| **RETURNS** | The rendered HTML markup. ~~str~~                                                                                                                                                      |

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

| Name                                       | Description                                                                                                                                  |
| ------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------- |
| `fine_grained`                             | Use fine-grained part-of-speech tags (`Token.tag_`) instead of coarse-grained tags (`Token.pos_`). Defaults to `False`. ~~bool~~             |
| `add_lemma` <Tag variant="new">2.2.4</Tag> | Print the lemmas in a separate row below the token texts. Defaults to `False`. ~~bool~~                                                      |
| `collapse_punct`                           | Attach punctuation to tokens. Can make the parse more readable, as it prevents long arcs to attach punctuation. Defaults to `True`. ~~bool~~ |
| `collapse_phrases`                         | Merge noun phrases into one token. Defaults to `False`. ~~bool~~                                                                             |
| `compact`                                  | "Compact mode" with square arrows that takes up less space. Defaults to `False`. ~~bool~~                                                    |
| `color`                                    | Text color (HEX, RGB or color names). Defaults to `"#000000"`. ~~str~~                                                                       |
| `bg`                                       | Background color (HEX, RGB or color names). Defaults to `"#ffffff"`. ~~str~~                                                                 |
| `font`                                     | Font name or font family for all text. Defaults to `"Arial"`. ~~str~~                                                                        |
| `offset_x`                                 | Spacing on left side of the SVG in px. Defaults to `50`. ~~int~~                                                                             |
| `arrow_stroke`                             | Width of arrow path in px. Defaults to `2`. ~~int~~                                                                                          |
| `arrow_width`                              | Width of arrow head in px. Defaults to `10` in regular mode and `8` in compact mode. ~~int~~                                                 |
| `arrow_spacing`                            | Spacing between arrows in px to avoid overlaps. Defaults to `20` in regular mode and `12` in compact mode. ~~int~~                           |
| `word_spacing`                             | Vertical spacing between words and arcs in px. Defaults to `45`. ~~int~~                                                                     |
| `distance`                                 | Distance between words in px. Defaults to `175` in regular mode and `150` in compact mode. ~~int~~                                           |

#### Named Entity Visualizer options {#displacy_options-ent}

> #### Example
>
> ```python
> options = {"ents": ["PERSON", "ORG", "PRODUCT"],
>            "colors": {"ORG": "yellow"}}
> displacy.serve(doc, style="ent", options=options)
> ```

| Name                                             | Description                                                                                                                                                                                                                                 |
| ------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `ents`                                           | Entity types to highlight or `None` for all types (default). ~~Optional[List[str]]~~                                                                                                                                                        |
| `colors`                                         | Color overrides. Entity types should be mapped to color names or values. ~~Dict[str, str]~~                                                                                                                                                 |
| `template` <Tag variant="new">2.2</Tag>          | Optional template to overwrite the HTML used to render entity spans. Should be a format string and can use `{bg}`, `{text}` and `{label}`. See [`templates.py`](%%GITHUB_SPACY/spacy/displacy/templates.py) for examples. ~~Optional[str]~~ |
| `kb_url_template` <Tag variant="new">3.2.1</Tag> | Optional template to construct the KB url for the entity to link to. Expects a python f-string format with single field to fill in. ~~Optional[str]~~                                                                                       |

#### Span Visualizer options {#displacy_options-span}

> #### Example
>
> ```python
> options = {"spans_key": "sc"}
> displacy.serve(doc, style="span", options=options)
> ```

| Name              | Description                                                                                                                                                                               |
| ----------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `spans_key`       | Which spans key to render spans from. Default is `"sc"`. ~~str~~                                                                                                                          |
| `templates`       | Dictionary containing the keys `"span"`, `"slice"`, and `"start"`. These dictate how the overall span, a span slice, and the starting token will be rendered. ~~Optional[Dict[str, str]~~ |
| `kb_url_template` | Optional template to construct the KB url for the entity to link to. Expects a python f-string format with single field to fill in ~~Optional[str]~~                                      |
| `colors`          | Color overrides. Entity types should be mapped to color names or values. ~~Dict[str, str]~~                                                                                               |

By default, displaCy comes with colors for all entity types used by
[spaCy's trained pipelines](/models) for both entity and span visualizer. If
you're using custom entity types, you can use the `colors` setting to add your
own colors for them. Your application or pipeline package can also expose a
[`spacy_displacy_colors` entry point](/usage/saving-loading#entry-points-displacy)
to add custom labels and their colors automatically.

By default, displaCy links to `#` for entities without a `kb_id` set on their
span. If you wish to link an entity to their URL then consider using the
`kb_url_template` option from above. For example if the `kb_id` on a span is
`Q95` and this is a Wikidata identifier then this option can be set to
`https://www.wikidata.org/wiki/{}`. Clicking on your entity in the rendered HTML
should redirect you to their Wikidata page, in this case
`https://www.wikidata.org/wiki/Q95`.

## registry {#registry source="spacy/util.py" new="3"}

spaCy's function registry extends
[Thinc's `registry`](https://thinc.ai/docs/api-config#registry) and allows you
to map strings to functions. You can register functions to create architectures,
optimizers, schedules and more, and then refer to them and set their arguments
in your [config file](/usage/training#config). Python type hints are used to
validate the inputs. See the
[Thinc docs](https://thinc.ai/docs/api-config#registry) for details on the
`registry` methods and our helper library
[`catalogue`](https://github.com/explosion/catalogue) for some background on the
concept of function registries. spaCy also uses the function registry for
language subclasses, model architecture, lookups and pipeline component
factories.

> #### Example
>
> ```python
> from typing import Iterator
> import spacy
>
> @spacy.registry.schedules("waltzing.v1")
> def waltzing() -> Iterator[float]:
>     i = 0
>     while True:
>         yield i % 3 + 1
>         i += 1
> ```

| Registry name     | Description                                                                                                                                                                                                                                        |
| ----------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `architectures`   | Registry for functions that create [model architectures](/api/architectures). Can be used to register custom model architectures and reference them in the `config.cfg`.                                                                           |
| `augmenters`      | Registry for functions that create [data augmentation](#augmenters) callbacks for corpora and other training data iterators.                                                                                                                       |
| `batchers`        | Registry for training and evaluation [data batchers](#batchers).                                                                                                                                                                                   |
| `callbacks`       | Registry for custom callbacks to [modify the `nlp` object](/usage/training#custom-code-nlp-callbacks) before training.                                                                                                                             |
| `displacy_colors` | Registry for custom color scheme for the [`displacy` NER visualizer](/usage/visualizers). Automatically reads from [entry points](/usage/saving-loading#entry-points).                                                                             |
| `factories`       | Registry for functions that create [pipeline components](/usage/processing-pipelines#custom-components). Added automatically when you use the `@spacy.component` decorator and also reads from [entry points](/usage/saving-loading#entry-points). |
| `initializers`    | Registry for functions that create [initializers](https://thinc.ai/docs/api-initializers).                                                                                                                                                         |
| `languages`       | Registry for language-specific `Language` subclasses. Automatically reads from [entry points](/usage/saving-loading#entry-points).                                                                                                                 |
| `layers`          | Registry for functions that create [layers](https://thinc.ai/docs/api-layers).                                                                                                                                                                     |
| `loggers`         | Registry for functions that log [training results](/usage/training).                                                                                                                                                                               |
| `lookups`         | Registry for large lookup tables available via `vocab.lookups`.                                                                                                                                                                                    |
| `losses`          | Registry for functions that create [losses](https://thinc.ai/docs/api-loss).                                                                                                                                                                       |
| `misc`            | Registry for miscellaneous functions that return data assets, knowledge bases or anything else you may need.                                                                                                                                       |
| `optimizers`      | Registry for functions that create [optimizers](https://thinc.ai/docs/api-optimizers).                                                                                                                                                             |
| `readers`         | Registry for file and data readers, including training and evaluation data readers like [`Corpus`](/api/corpus).                                                                                                                                   |
| `schedules`       | Registry for functions that create [schedules](https://thinc.ai/docs/api-schedules).                                                                                                                                                               |
| `scorers`         | Registry for functions that create scoring methods for user with the [`Scorer`](/api/scorer). Scoring methods are called with `Iterable[Example]` and arbitrary `\*\*kwargs` and return scores as `Dict[str, Any]`.                                |
| `tokenizers`      | Registry for tokenizer factories. Registered functions should return a callback that receives the `nlp` object and returns a [`Tokenizer`](/api/tokenizer) or a custom callable.                                                                   |

### spacy-transformers registry {#registry-transformers}

The following registries are added by the
[`spacy-transformers`](https://github.com/explosion/spacy-transformers) package.
See the [`Transformer`](/api/transformer) API reference and
[usage docs](/usage/embeddings-transformers) for details.

> #### Example
>
> ```python
> import spacy_transformers
>
> @spacy_transformers.registry.annotation_setters("my_annotation_setter.v1")
> def configure_custom_annotation_setter():
>     def annotation_setter(docs, trf_data) -> None:
>        # Set annotations on the docs
>
>     return annotation_setter
> ```

| Registry name                                               | Description                                                                                                                                                                                                                                       |
| ----------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [`span_getters`](/api/transformer#span_getters)             | Registry for functions that take a batch of `Doc` objects and return a list of `Span` objects to process by the transformer, e.g. sentences.                                                                                                      |
| [`annotation_setters`](/api/transformer#annotation_setters) | Registry for functions that create annotation setters. Annotation setters are functions that take a batch of `Doc` objects and a [`FullTransformerBatch`](/api/transformer#fulltransformerbatch) and can set additional annotations on the `Doc`. |

## Loggers {#loggers source="spacy/training/loggers.py" new="3"}

A logger records the training results. When a logger is created, two functions
are returned: one for logging the information for each training step, and a
second function that is called to finalize the logging when the training is
finished. To log each training step, a
[dictionary](/usage/training#custom-logging) is passed on from the
[`spacy train`](/api/cli#train), including information such as the training loss
and the accuracy scores on the development set.

The built-in, default logger is the ConsoleLogger, which prints results to the
console in tabular format. The
[spacy-loggers](https://github.com/explosion/spacy-loggers) package, included as
a dependency of spaCy, enables other loggers, such as one that sends results to
a [Weights & Biases](https://www.wandb.com/) dashboard.

Instead of using one of the built-in loggers, you can
[implement your own](/usage/training#custom-logging).

#### spacy.ConsoleLogger.v1 {#ConsoleLogger tag="registered function"}

> #### Example config
>
> ```ini
> [training.logger]
> @loggers = "spacy.ConsoleLogger.v1"
> ```

Writes the results of a training step to the console in a tabular format.

<Accordion title="Example console output" spaced>

```cli
$ python -m spacy train config.cfg
```

```
ℹ Using CPU
ℹ Loading config and nlp from: config.cfg
ℹ Pipeline: ['tok2vec', 'tagger']
ℹ Start training
ℹ Training. Initial learn rate: 0.0

E     #        LOSS TOK2VEC   LOSS TAGGER   TAG_ACC   SCORE
---   ------   ------------   -----------   -------   ------
  1        0           0.00         86.20      0.22     0.00
  1      200           3.08      18968.78     34.00     0.34
  1      400          31.81      22539.06     33.64     0.34
  1      600          92.13      22794.91     43.80     0.44
  1      800         183.62      21541.39     56.05     0.56
  1     1000         352.49      25461.82     65.15     0.65
  1     1200         422.87      23708.82     71.84     0.72
  1     1400         601.92      24994.79     76.57     0.77
  1     1600         662.57      22268.02     80.20     0.80
  1     1800        1101.50      28413.77     82.56     0.83
  1     2000        1253.43      28736.36     85.00     0.85
  1     2200        1411.02      28237.53     87.42     0.87
  1     2400        1605.35      28439.95     88.70     0.89
```

Note that the cumulative loss keeps increasing within one epoch, but should
start decreasing across epochs.

 </Accordion>

## Readers {#readers}

### File readers {#file-readers source="github.com/explosion/srsly" new="3"}

The following file readers are provided by our serialization library
[`srsly`](https://github.com/explosion/srsly). All registered functions take one
argument `path`, pointing to the file path to load.

> #### Example config
>
> ```ini
> [corpora.train.augmenter.orth_variants]
> @readers = "srsly.read_json.v1"
> path = "corpus/en_orth_variants.json"
> ```

| Name                    | Description                                           |
| ----------------------- | ----------------------------------------------------- |
| `srsly.read_json.v1`    | Read data from a JSON file.                           |
| `srsly.read_jsonl.v1`   | Read data from a JSONL (newline-delimited JSON) file. |
| `srsly.read_yaml.v1`    | Read data from a YAML file.                           |
| `srsly.read_msgpack.v1` | Read data from a binary MessagePack file.             |

<Infobox title="Important note" variant="warning">

Since the file readers expect a local path, you should only use them in config
blocks that are **not executed at runtime** – for example, in `[training]` and
`[corpora]` (to load data or resources like data augmentation tables) or in
`[initialize]` (to pass data to pipeline components).

</Infobox>

#### spacy.read_labels.v1 {#read_labels tag="registered function"}

Read a JSON-formatted labels file generated with
[`init labels`](/api/cli#init-labels). Typically used in the
[`[initialize]`](/api/data-formats#config-initialize) block of the training
config to speed up the model initialization process and provide pre-generated
label sets.

> #### Example config
>
> ```ini
> [initialize.components]
>
> [initialize.components.ner]
>
> [initialize.components.ner.labels]
> @readers = "spacy.read_labels.v1"
> path = "corpus/labels/ner.json"
> ```

| Name        | Description                                                                                                                                                                                                               |
| ----------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `path`      | The path to the labels file generated with [`init labels`](/api/cli#init-labels). ~~Path~~                                                                                                                                |
| `require`   | Whether to require the file to exist. If set to `False` and the labels file doesn't exist, the loader will return `None` and the `initialize` method will extract the labels from the data. Defaults to `False`. ~~bool~~ |
| **CREATES** | The list of labels. ~~List[str]~~                                                                                                                                                                                         |

### Corpus readers {#corpus-readers source="spacy/training/corpus.py" new="3"}

Corpus readers are registered functions that load data and return a function
that takes the current `nlp` object and yields [`Example`](/api/example) objects
that can be used for [training](/usage/training) and
[pretraining](/usage/embeddings-transformers#pretraining). You can replace it
with your own registered function in the
[`@readers` registry](/api/top-level#registry) to customize the data loading and
streaming.

#### spacy.Corpus.v1 {#corpus tag="registered function"}

The `Corpus` reader manages annotated corpora and can be used for training and
development datasets in the [DocBin](/api/docbin) (`.spacy`) format. Also see
the [`Corpus`](/api/corpus) class.

> #### Example config
>
> ```ini
> [paths]
> train = "corpus/train.spacy"
>
> [corpora.train]
> @readers = "spacy.Corpus.v1"
> path = ${paths.train}
> gold_preproc = false
> max_length = 0
> limit = 0
> ```

| Name           | Description                                                                                                                                                                                                                                                                              |
| -------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `path`         | The directory or filename to read from. Expects data in spaCy's binary [`.spacy` format](/api/data-formats#binary-training). ~~Union[str, Path]~~                                                                                                                                        |
| `gold_preproc` | Whether to set up the Example object with gold-standard sentences and tokens for the predictions. See [`Corpus`](/api/corpus#init) for details. ~~bool~~                                                                                                                                 |
| `max_length`   | Maximum document length. Longer documents will be split into sentences, if sentence boundaries are available. Defaults to `0` for no limit. ~~int~~                                                                                                                                      |
| `limit`        | Limit corpus to a subset of examples, e.g. for debugging. Defaults to `0` for no limit. ~~int~~                                                                                                                                                                                          |
| `augmenter`    | Apply some simply data augmentation, where we replace tokens with variations. This is especially useful for punctuation and case replacement, to help generalize beyond corpora that don't have smart-quotes, or only have smart quotes, etc. Defaults to `None`. ~~Optional[Callable]~~ |
| **CREATES**    | The corpus reader. ~~Corpus~~                                                                                                                                                                                                                                                            |

#### spacy.JsonlCorpus.v1 {#jsonlcorpus tag="registered function"}

Create [`Example`](/api/example) objects from a JSONL (newline-delimited JSON)
file of texts keyed by `"text"`. Can be used to read the raw text corpus for
language model [pretraining](/usage/embeddings-transformers#pretraining) from a
JSONL file. Also see the [`JsonlCorpus`](/api/corpus#jsonlcorpus) class.

> #### Example config
>
> ```ini
> [paths]
> pretrain = "corpus/raw_text.jsonl"
>
> [corpora.pretrain]
> @readers = "spacy.JsonlCorpus.v1"
> path = ${paths.pretrain}
> min_length = 0
> max_length = 0
> limit = 0
> ```

| Name         | Description                                                                                                                      |
| ------------ | -------------------------------------------------------------------------------------------------------------------------------- |
| `path`       | The directory or filename to read from. Expects newline-delimited JSON with a key `"text"` for each record. ~~Union[str, Path]~~ |
| `min_length` | Minimum document length (in tokens). Shorter documents will be skipped. Defaults to `0`, which indicates no limit. ~~int~~       |
| `max_length` | Maximum document length (in tokens). Longer documents will be skipped. Defaults to `0`, which indicates no limit. ~~int~~        |
| `limit`      | Limit corpus to a subset of examples, e.g. for debugging. Defaults to `0` for no limit. ~~int~~                                  |
| **CREATES**  | The corpus reader. ~~JsonlCorpus~~                                                                                               |

## Batchers {#batchers source="spacy/training/batchers.py" new="3"}

A data batcher implements a batching strategy that essentially turns a stream of
items into a stream of batches, with each batch consisting of one item or a list
of items. During training, the models update their weights after processing one
batch at a time. Typical batching strategies include presenting the training
data as a stream of batches with similar sizes, or with increasing batch sizes.
See the Thinc documentation on
[`schedules`](https://thinc.ai/docs/api-schedules) for a few standard examples.

Instead of using one of the built-in batchers listed here, you can also
[implement your own](/usage/training#custom-code-readers-batchers), which may or
may not use a custom schedule.

### spacy.batch_by_words.v1 {#batch_by_words tag="registered function"}

Create minibatches of roughly a given number of words. If any examples are
longer than the specified batch length, they will appear in a batch by
themselves, or be discarded if `discard_oversize` is set to `True`. The argument
`docs` can be a list of strings, [`Doc`](/api/doc) objects or
[`Example`](/api/example) objects.

> #### Example config
>
> ```ini
> [training.batcher]
> @batchers = "spacy.batch_by_words.v1"
> size = 100
> tolerance = 0.2
> discard_oversize = false
> get_length = null
> ```

| Name               | Description                                                                                                                                                                             |
| ------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `seqs`             | The sequences to minibatch. ~~Iterable[Any]~~                                                                                                                                           |
| `size`             | The target number of words per batch. Can also be a block referencing a schedule, e.g. [`compounding`](https://thinc.ai/docs/api-schedules/#compounding). ~~Union[int, Sequence[int]]~~ |
| `tolerance`        | What percentage of the size to allow batches to exceed. ~~float~~                                                                                                                       |
| `discard_oversize` | Whether to discard sequences that by themselves exceed the tolerated size. ~~bool~~                                                                                                     |
| `get_length`       | Optional function that receives a sequence item and returns its length. Defaults to the built-in `len()` if not set. ~~Optional[Callable[[Any], int]]~~                                 |
| **CREATES**        | The batcher that takes an iterable of items and returns batches. ~~Callable[[Iterable[Any]], Iterable[List[Any]]]~~                                                                     |

### spacy.batch_by_sequence.v1 {#batch_by_sequence tag="registered function"}

> #### Example config
>
> ```ini
> [training.batcher]
> @batchers = "spacy.batch_by_sequence.v1"
> size = 32
> get_length = null
> ```

Create a batcher that creates batches of the specified size.

| Name         | Description                                                                                                                                                                             |
| ------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `size`       | The target number of items per batch. Can also be a block referencing a schedule, e.g. [`compounding`](https://thinc.ai/docs/api-schedules/#compounding). ~~Union[int, Sequence[int]]~~ |
| `get_length` | Optional function that receives a sequence item and returns its length. Defaults to the built-in `len()` if not set. ~~Optional[Callable[[Any], int]]~~                                 |
| **CREATES**  | The batcher that takes an iterable of items and returns batches. ~~Callable[[Iterable[Any]], Iterable[List[Any]]]~~                                                                     |

### spacy.batch_by_padded.v1 {#batch_by_padded tag="registered function"}

> #### Example config
>
> ```ini
> [training.batcher]
> @batchers = "spacy.batch_by_padded.v1"
> size = 100
> buffer = 256
> discard_oversize = false
> get_length = null
> ```

Minibatch a sequence by the size of padded batches that would result, with
sequences binned by length within a window. The padded size is defined as the
maximum length of sequences within the batch multiplied by the number of
sequences in the batch.

| Name               | Description                                                                                                                                                                                                                                 |
| ------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `size`             | The largest padded size to batch sequences into. Can also be a block referencing a schedule, e.g. [`compounding`](https://thinc.ai/docs/api-schedules/#compounding). ~~Union[int, Sequence[int]]~~                                          |
| `buffer`           | The number of sequences to accumulate before sorting by length. A larger buffer will result in more even sizing, but if the buffer is very large, the iteration order will be less random, which can result in suboptimal training. ~~int~~ |
| `discard_oversize` | Whether to discard sequences that are by themselves longer than the largest padded batch size. ~~bool~~                                                                                                                                     |
| `get_length`       | Optional function that receives a sequence item and returns its length. Defaults to the built-in `len()` if not set. ~~Optional[Callable[[Any], int]]~~                                                                                     |
| **CREATES**        | The batcher that takes an iterable of items and returns batches. ~~Callable[[Iterable[Any]], Iterable[List[Any]]]~~                                                                                                                         |

## Augmenters {#augmenters source="spacy/training/augment.py" new="3"}

Data augmentation is the process of applying small modifications to the training
data. It can be especially useful for punctuation and case replacement – for
example, if your corpus only uses smart quotes and you want to include
variations using regular quotes, or to make the model less sensitive to
capitalization by including a mix of capitalized and lowercase examples. See the
[usage guide](/usage/training#data-augmentation) for details and examples.

### spacy.orth_variants.v1 {#orth_variants tag="registered function"}

> #### Example config
>
> ```ini
> [corpora.train.augmenter]
> @augmenters = "spacy.orth_variants.v1"
> level = 0.1
> lower = 0.5
>
> [corpora.train.augmenter.orth_variants]
> @readers = "srsly.read_json.v1"
> path = "corpus/en_orth_variants.json"
> ```

Create a data augmentation callback that uses orth-variant replacement. The
callback can be added to a corpus or other data iterator during training. It's
especially useful for punctuation and case replacement, to help generalize
beyond corpora that don't have smart quotes, or only have smart quotes etc.

| Name            | Description                                                                                                                                                                                                                                                                                               |
| --------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `level`         | The percentage of texts that will be augmented. ~~float~~                                                                                                                                                                                                                                                 |
| `lower`         | The percentage of texts that will be lowercased. ~~float~~                                                                                                                                                                                                                                                |
| `orth_variants` | A dictionary containing the single and paired orth variants. Typically loaded from a JSON file. See [`en_orth_variants.json`](https://github.com/explosion/spacy-lookups-data/blob/master/spacy_lookups_data/data/en_orth_variants.json) for an example. ~~Dict[str, Dict[List[Union[str, List[str]]]]]~~ |
| **CREATES**     | A function that takes the current `nlp` object and an [`Example`](/api/example) and yields augmented `Example` objects. ~~Callable[[Language, Example], Iterator[Example]]~~                                                                                                                              |

### spacy.lower_case.v1 {#lower_case tag="registered function"}

> #### Example config
>
> ```ini
> [corpora.train.augmenter]
> @augmenters = "spacy.lower_case.v1"
> level = 0.3
> ```

Create a data augmentation callback that lowercases documents. The callback can
be added to a corpus or other data iterator during training. It's especially
useful for making the model less sensitive to capitalization.

| Name        | Description                                                                                                                                                                  |
| ----------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `level`     | The percentage of texts that will be augmented. ~~float~~                                                                                                                    |
| **CREATES** | A function that takes the current `nlp` object and an [`Example`](/api/example) and yields augmented `Example` objects. ~~Callable[[Language, Example], Iterator[Example]]~~ |

## Callbacks {#callbacks source="spacy/training/callbacks.py" new="3"}

The config supports [callbacks](/usage/training#custom-code-nlp-callbacks) at
several points in the lifecycle that can be used modify the `nlp` object.

### spacy.copy_from_base_model.v1 {#copy_from_base_model tag="registered function"}

> #### Example config
>
> ```ini
> [initialize.before_init]
> @callbacks = "spacy.copy_from_base_model.v1"
> tokenizer = "en_core_sci_md"
> vocab = "en_core_sci_md"
> ```

Copy the tokenizer and/or vocab from the specified models. It's similar to the
v2 [base model](https://v2.spacy.io/api/cli#train) option and useful in
combination with
[sourced components](/usage/processing-pipelines#sourced-components) when
fine-tuning an existing pipeline. The vocab includes the lookups and the vectors
from the specified model. Intended for use in `[initialize.before_init]`.

| Name        | Description                                                                                                             |
| ----------- | ----------------------------------------------------------------------------------------------------------------------- |
| `tokenizer` | The pipeline to copy the tokenizer from. Defaults to `None`. ~~Optional[str]~~                                          |
| `vocab`     | The pipeline to copy the vocab from. The vocab includes the lookups and vectors. Defaults to `None`. ~~Optional[str]~~  |
| **CREATES** | A function that takes the current `nlp` object and modifies its `tokenizer` and `vocab`. ~~Callable[[Language], None]~~ |

### spacy.models_with_nvtx_range.v1 {#models_with_nvtx_range tag="registered function"}

> #### Example config
>
> ```ini
> [nlp]
> after_pipeline_creation = {"@callbacks":"spacy.models_with_nvtx_range.v1"}
> ```

Recursively wrap the models in each pipe using
[NVTX](https://nvidia.github.io/NVTX/) range markers. These markers aid in GPU
profiling by attributing specific operations to a ~~Model~~'s forward or
backprop passes.

| Name             | Description                                                                                                                  |
| ---------------- | ---------------------------------------------------------------------------------------------------------------------------- |
| `forward_color`  | Color identifier for forward passes. Defaults to `-1`. ~~int~~                                                               |
| `backprop_color` | Color identifier for backpropagation passes. Defaults to `-1`. ~~int~~                                                       |
| **CREATES**      | A function that takes the current `nlp` and wraps forward/backprop passes in NVTX ranges. ~~Callable[[Language], Language]~~ |

## Training data and alignment {#gold source="spacy/training"}

### training.offsets_to_biluo_tags {#offsets_to_biluo_tags tag="function"}

Encode labelled spans into per-token tags, using the
[BILUO scheme](/usage/linguistic-features#accessing-ner) (Begin, In, Last, Unit,
Out). Returns a list of strings, describing the tags. Each tag string will be in
the form of either `""`, `"O"` or `"{action}-{label}"`, where action is one of
`"B"`, `"I"`, `"L"`, `"U"`. The string `"-"` is used where the entity offsets
don't align with the tokenization in the `Doc` object. The training algorithm
will view these as missing values. `O` denotes a non-entity token. `B` denotes
the beginning of a multi-token entity, `I` the inside of an entity of three or
more tokens, and `L` the end of an entity of two or more tokens. `U` denotes a
single-token entity.

<Infobox title="Changed in v3.0" variant="warning" id="biluo_tags_from_offsets">

This method was previously available as `spacy.gold.biluo_tags_from_offsets`.

</Infobox>

> #### Example
>
> ```python
> from spacy.training import offsets_to_biluo_tags
>
> doc = nlp("I like London.")
> entities = [(7, 13, "LOC")]
> tags = offsets_to_biluo_tags(doc, entities)
> assert tags == ["O", "O", "U-LOC", "O"]
> ```

| Name        | Description                                                                                                                                                                                |
| ----------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `doc`       | The document that the entity offsets refer to. The output tags will refer to the token boundaries within the document. ~~Doc~~                                                             |
| `entities`  | A sequence of `(start, end, label)` triples. `start` and `end` should be character-offset integers denoting the slice into the original string. ~~List[Tuple[int, int, Union[str, int]]]~~ |
| `missing`   | The label used for missing values, e.g. if tokenization doesn't align with the entity offsets. Defaults to `"O"`. ~~str~~                                                                  |
| **RETURNS** | A list of strings, describing the [BILUO](/usage/linguistic-features#accessing-ner) tags. ~~List[str]~~                                                                                    |

### training.biluo_tags_to_offsets {#biluo_tags_to_offsets tag="function"}

Encode per-token tags following the
[BILUO scheme](/usage/linguistic-features#accessing-ner) into entity offsets.

<Infobox title="Changed in v3.0" variant="warning" id="offsets_from_biluo_tags">

This method was previously available as `spacy.gold.offsets_from_biluo_tags`.

</Infobox>

> #### Example
>
> ```python
> from spacy.training import biluo_tags_to_offsets
>
> doc = nlp("I like London.")
> tags = ["O", "O", "U-LOC", "O"]
> entities = biluo_tags_to_offsets(doc, tags)
> assert entities == [(7, 13, "LOC")]
> ```

| Name        | Description                                                                                                                                                                                                                                                  |
| ----------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `doc`       | The document that the BILUO tags refer to. ~~Doc~~                                                                                                                                                                                                           |
| `tags`      | A sequence of [BILUO](/usage/linguistic-features#accessing-ner) tags with each tag describing one token. Each tag string will be of the form of either `""`, `"O"` or `"{action}-{label}"`, where action is one of `"B"`, `"I"`, `"L"`, `"U"`. ~~List[str]~~ |
| **RETURNS** | A sequence of `(start, end, label)` triples. `start` and `end` will be character-offset integers denoting the slice into the original string. ~~List[Tuple[int, int, str]]~~                                                                                 |

### training.biluo_tags_to_spans {#biluo_tags_to_spans tag="function" new="2.1"}

Encode per-token tags following the
[BILUO scheme](/usage/linguistic-features#accessing-ner) into
[`Span`](/api/span) objects. This can be used to create entity spans from
token-based tags, e.g. to overwrite the `doc.ents`.

<Infobox title="Changed in v3.0" variant="warning" id="spans_from_biluo_tags">

This method was previously available as `spacy.gold.spans_from_biluo_tags`.

</Infobox>

> #### Example
>
> ```python
> from spacy.training import biluo_tags_to_spans
>
> doc = nlp("I like London.")
> tags = ["O", "O", "U-LOC", "O"]
> doc.ents = biluo_tags_to_spans(doc, tags)
> ```

| Name        | Description                                                                                                                                                                                                                                                  |
| ----------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `doc`       | The document that the BILUO tags refer to. ~~Doc~~                                                                                                                                                                                                           |
| `tags`      | A sequence of [BILUO](/usage/linguistic-features#accessing-ner) tags with each tag describing one token. Each tag string will be of the form of either `""`, `"O"` or `"{action}-{label}"`, where action is one of `"B"`, `"I"`, `"L"`, `"U"`. ~~List[str]~~ |
| **RETURNS** | A sequence of `Span` objects with added entity labels. ~~List[Span]~~                                                                                                                                                                                        |

## Utility functions {#util source="spacy/util.py"}

spaCy comes with a small collection of utility functions located in
[`spacy/util.py`](%%GITHUB_SPACY/spacy/util.py). Because utility functions are
mostly intended for **internal use within spaCy**, their behavior may change
with future releases. The functions documented on this page should be safe to
use and we'll try to ensure backwards compatibility. However, we recommend
having additional tests in place if your application depends on any of spaCy's
utilities.

### util.get_lang_class {#util.get_lang_class tag="function"}

Import and load a `Language` class. Allows lazy-loading
[language data](/usage/linguistic-features#language-data) and importing
languages using the two-letter language code. To add a language code for a
custom language class, you can register it using the
[`@registry.languages`](/api/top-level#registry) decorator.

> #### Example
>
> ```python
> for lang_id in ["en", "de"]:
>     lang_class = util.get_lang_class(lang_id)
>     lang = lang_class()
> ```

| Name        | Description                                    |
| ----------- | ---------------------------------------------- |
| `lang`      | Two-letter language code, e.g. `"en"`. ~~str~~ |
| **RETURNS** | The respective subclass. ~~Language~~          |

### util.lang_class_is_loaded {#util.lang_class_is_loaded tag="function" new="2.1"}

Check whether a `Language` subclass is already loaded. `Language` subclasses are
loaded lazily to avoid expensive setup code associated with the language data.

> #### Example
>
> ```python
> lang_cls = util.get_lang_class("en")
> assert util.lang_class_is_loaded("en") is True
> assert util.lang_class_is_loaded("de") is False
> ```

| Name        | Description                                    |
| ----------- | ---------------------------------------------- |
| `name`      | Two-letter language code, e.g. `"en"`. ~~str~~ |
| **RETURNS** | Whether the class has been loaded. ~~bool~~    |

### util.load_model {#util.load_model tag="function" new="2"}

Load a pipeline from a package or data path. If called with a string name, spaCy
will assume the pipeline is a Python package and import and call its `load()`
method. If called with a path, spaCy will assume it's a data directory, read the
language and pipeline settings from the [`config.cfg`](/api/data-formats#config)
and create a `Language` object. The model data will then be loaded in via
[`Language.from_disk`](/api/language#from_disk).

> #### Example
>
> ```python
> nlp = util.load_model("en_core_web_sm")
> nlp = util.load_model("en_core_web_sm", exclude=["ner"])
> nlp = util.load_model("/path/to/data")
> ```

| Name                                 | Description                                                                                                                                                                                                                                      |
| ------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `name`                               | Package name or path. ~~str~~                                                                                                                                                                                                                    |
| _keyword-only_                       |                                                                                                                                                                                                                                                  |
| `vocab`                              | Optional shared vocab to pass in on initialization. If `True` (default), a new `Vocab` object will be created. ~~Union[Vocab, bool]~~                                                                                                            |
| `disable`                            | Names of pipeline components to [disable](/usage/processing-pipelines#disabling). Disabled pipes will be loaded but they won't be run unless you explicitly enable them by calling [`nlp.enable_pipe`](/api/language#enable_pipe). ~~List[str]~~ |
| `exclude` <Tag variant="new">3</Tag> | Names of pipeline components to [exclude](/usage/processing-pipelines#disabling). Excluded components won't be loaded. ~~List[str]~~                                                                                                             |
| `config` <Tag variant="new">3</Tag>  | Config overrides as nested dict or flat dict keyed by section values in dot notation, e.g. `"nlp.pipeline"`. ~~Union[Dict[str, Any], Config]~~                                                                                                   |
| **RETURNS**                          | `Language` class with the loaded pipeline. ~~Language~~                                                                                                                                                                                          |

### util.load_model_from_init_py {#util.load_model_from_init_py tag="function" new="2"}

A helper function to use in the `load()` method of a pipeline package's
[`__init__.py`](https://github.com/explosion/spacy-models/tree/master/template/model/xx_model_name/__init__.py).

> #### Example
>
> ```python
> from spacy.util import load_model_from_init_py
>
> def load(**overrides):
>     return load_model_from_init_py(__file__, **overrides)
> ```

| Name                                 | Description                                                                                                                                                                                                                                    |
| ------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `init_file`                          | Path to package's `__init__.py`, i.e. `__file__`. ~~Union[str, Path]~~                                                                                                                                                                         |
| _keyword-only_                       |                                                                                                                                                                                                                                                |
| `vocab` <Tag variant="new">3</Tag>   | Optional shared vocab to pass in on initialization. If `True` (default), a new `Vocab` object will be created. ~~Union[Vocab, bool]~~                                                                                                          |
| `disable`                            | Names of pipeline components to [disable](/usage/processing-pipelines#disabling). Disabled pipes will be loaded but they won't be run unless you explicitly enable them by calling [nlp.enable_pipe](/api/language#enable_pipe). ~~List[str]~~ |
| `exclude` <Tag variant="new">3</Tag> | Names of pipeline components to [exclude](/usage/processing-pipelines#disabling). Excluded components won't be loaded. ~~List[str]~~                                                                                                           |
| `config` <Tag variant="new">3</Tag>  | Config overrides as nested dict or flat dict keyed by section values in dot notation, e.g. `"nlp.pipeline"`. ~~Union[Dict[str, Any], Config]~~                                                                                                 |
| **RETURNS**                          | `Language` class with the loaded pipeline. ~~Language~~                                                                                                                                                                                        |

### util.load_config {#util.load_config tag="function" new="3"}

Load a pipeline's [`config.cfg`](/api/data-formats#config) from a file path. The
config typically includes details about the components and how they're created,
as well as all training settings and hyperparameters.

> #### Example
>
> ```python
> config = util.load_config("/path/to/config.cfg")
> print(config.to_str())
> ```

| Name          | Description                                                                                                                                                                 |
| ------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `path`        | Path to the pipeline's `config.cfg`. ~~Union[str, Path]~~                                                                                                                   |
| `overrides`   | Optional config overrides to replace in loaded config. Can be provided as nested dict, or as flat dict with keys in dot notation, e.g. `"nlp.pipeline"`. ~~Dict[str, Any]~~ |
| `interpolate` | Whether to interpolate the config and replace variables like `${paths.train}` with their values. Defaults to `False`. ~~bool~~                                              |
| **RETURNS**   | The pipeline's config. ~~Config~~                                                                                                                                           |

### util.load_meta {#util.load_meta tag="function" new="3"}

Get a pipeline's [`meta.json`](/api/data-formats#meta) from a file path and
validate its contents. The meta typically includes details about author,
licensing, data sources and version.

> #### Example
>
> ```python
> meta = util.load_meta("/path/to/meta.json")
> ```

| Name        | Description                                              |
| ----------- | -------------------------------------------------------- |
| `path`      | Path to the pipeline's `meta.json`. ~~Union[str, Path]~~ |
| **RETURNS** | The pipeline's meta data. ~~Dict[str, Any]~~             |

### util.get_installed_models {#util.get_installed_models tag="function" new="3"}

List all pipeline packages installed in the current environment. This will
include any spaCy pipeline that was packaged with
[`spacy package`](/api/cli#package). Under the hood, pipeline packages expose a
Python entry point that spaCy can check, without having to load the `nlp`
object.

> #### Example
>
> ```python
> names = util.get_installed_models()
> ```

| Name        | Description                                                                           |
| ----------- | ------------------------------------------------------------------------------------- |
| **RETURNS** | The string names of the pipelines installed in the current environment. ~~List[str]~~ |

### util.is_package {#util.is_package tag="function"}

Check if string maps to a package installed via pip. Mainly used to validate
[pipeline packages](/usage/models).

> #### Example
>
> ```python
> util.is_package("en_core_web_sm") # True
> util.is_package("xyz") # False
> ```

| Name        | Description                                           |
| ----------- | ----------------------------------------------------- |
| `name`      | Name of package. ~~str~~                              |
| **RETURNS** | `True` if installed package, `False` if not. ~~bool~~ |

### util.get_package_path {#util.get_package_path tag="function" new="2"}

Get path to an installed package. Mainly used to resolve the location of
[pipeline packages](/usage/models). Currently imports the package to find its
path.

> #### Example
>
> ```python
> util.get_package_path("en_core_web_sm")
> # /usr/lib/python3.6/site-packages/en_core_web_sm
> ```

| Name           | Description                                  |
| -------------- | -------------------------------------------- |
| `package_name` | Name of installed package. ~~str~~           |
| **RETURNS**    | Path to pipeline package directory. ~~Path~~ |

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

| Name        | Description                                    |
| ----------- | ---------------------------------------------- |
| **RETURNS** | `True` if in Jupyter, `False` if not. ~~bool~~ |

### util.compile_prefix_regex {#util.compile_prefix_regex tag="function"}

Compile a sequence of prefix rules into a regex object.

> #### Example
>
> ```python
> prefixes = ("§", "%", "=", r"\+")
> prefix_regex = util.compile_prefix_regex(prefixes)
> nlp.tokenizer.prefix_search = prefix_regex.search
> ```

| Name        | Description                                                                                                                                 |
| ----------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| `entries`   | The prefix rules, e.g. [`lang.punctuation.TOKENIZER_PREFIXES`](%%GITHUB_SPACY/spacy/lang/punctuation.py). ~~Iterable[Union[str, Pattern]]~~ |
| **RETURNS** | The regex object to be used for [`Tokenizer.prefix_search`](/api/tokenizer#attributes). ~~Pattern~~                                         |

### util.compile_suffix_regex {#util.compile_suffix_regex tag="function"}

Compile a sequence of suffix rules into a regex object.

> #### Example
>
> ```python
> suffixes = ("'s", "'S", r"(?<=[0-9])\+")
> suffix_regex = util.compile_suffix_regex(suffixes)
> nlp.tokenizer.suffix_search = suffix_regex.search
> ```

| Name        | Description                                                                                                                                 |
| ----------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| `entries`   | The suffix rules, e.g. [`lang.punctuation.TOKENIZER_SUFFIXES`](%%GITHUB_SPACY/spacy/lang/punctuation.py). ~~Iterable[Union[str, Pattern]]~~ |
| **RETURNS** | The regex object to be used for [`Tokenizer.suffix_search`](/api/tokenizer#attributes). ~~Pattern~~                                         |

### util.compile_infix_regex {#util.compile_infix_regex tag="function"}

Compile a sequence of infix rules into a regex object.

> #### Example
>
> ```python
> infixes = ("…", "-", "—", r"(?<=[0-9])[+\-\*^](?=[0-9-])")
> infix_regex = util.compile_infix_regex(infixes)
> nlp.tokenizer.infix_finditer = infix_regex.finditer
> ```

| Name        | Description                                                                                                                               |
| ----------- | ----------------------------------------------------------------------------------------------------------------------------------------- |
| `entries`   | The infix rules, e.g. [`lang.punctuation.TOKENIZER_INFIXES`](%%GITHUB_SPACY/spacy/lang/punctuation.py). ~~Iterable[Union[str, Pattern]]~~ |
| **RETURNS** | The regex object to be used for [`Tokenizer.infix_finditer`](/api/tokenizer#attributes). ~~Pattern~~                                      |

### util.minibatch {#util.minibatch tag="function" new="2"}

Iterate over batches of items. `size` may be an iterator, so that batch-size can
vary on each step.

> #### Example
>
> ```python
> batches = minibatch(train_data)
> for batch in batches:
>     nlp.update(batch)
> ```

| Name       | Description                                      |
| ---------- | ------------------------------------------------ |
| `items`    | The items to batch up. ~~Iterable[Any]~~         |
| `size`     | The batch size(s). ~~Union[int, Sequence[int]]~~ |
| **YIELDS** | The batches.                                     |

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

| Name        | Description                             |
| ----------- | --------------------------------------- |
| `spans`     | The spans to filter. ~~Iterable[Span]~~ |
| **RETURNS** | The filtered spans. ~~List[Span]~~      |

### util.get_words_and_spaces {#get_words_and_spaces tag="function" new="3"}

Given a list of words and a text, reconstruct the original tokens and return a
list of words and spaces that can be used to create a [`Doc`](/api/doc#init).
This can help recover destructive tokenization that didn't preserve any
whitespace information.

> #### Example
>
> ```python
> orig_words = ["Hey", ",", "what", "'s", "up", "?"]
> orig_text = "Hey, what's up?"
> words, spaces = get_words_and_spaces(orig_words, orig_text)
> # ['Hey', ',', 'what', "'s", 'up', '?']
> # [False, True, False, True, False, False]
> ```

| Name        | Description                                                                                                                                        |
| ----------- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| `words`     | The list of words. ~~Iterable[str]~~                                                                                                               |
| `text`      | The original text. ~~str~~                                                                                                                         |
| **RETURNS** | A list of words and a list of boolean values indicating whether the word at this position is followed by a space. ~~Tuple[List[str], List[bool]]~~ |
