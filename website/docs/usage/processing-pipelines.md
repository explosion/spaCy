---
title: Language Processing Pipelines
next: vectors-similarity
menu:
  - ['How Pipelines Work', 'pipelines']
  - ['Custom Components', 'custom-components']
  - ['Extension Attributes', 'custom-components-attributes']
  - ['Plugins & Wrappers', 'plugins']
---

import Pipelines101 from 'usage/101/\_pipelines.md'

<Pipelines101 />

## How pipelines work {#pipelines}

spaCy makes it very easy to create your own pipelines consisting of reusable
components – this includes spaCy's default tagger, parser and entity recognizer,
but also your own custom processing functions. A pipeline component can be added
to an already existing `nlp` object, specified when initializing a `Language`
class, or defined within a [model package](/usage/saving-loading#models).

When you load a model, spaCy first consults the model's
[`meta.json`](/usage/saving-loading#models). The meta typically includes the
model details, the ID of a language class, and an optional list of pipeline
components. spaCy then does the following:

> #### meta.json (excerpt)
>
> ```json
> {
>   "lang": "en",
>   "name": "core_web_sm",
>   "description": "Example model for spaCy",
>   "pipeline": ["tagger", "parser", "ner"]
> }
> ```

1. Load the **language class and data** for the given ID via
   [`get_lang_class`](/api/top-level#util.get_lang_class) and initialize it. The
   `Language` class contains the shared vocabulary, tokenization rules and the
   language-specific annotation scheme.
2. Iterate over the **pipeline names** and create each component using
   [`create_pipe`](/api/anguage#create_pipe), which looks them up in
   `Language.factories`.
3. Add each pipeline component to the pipeline in order, using
   [`add_pipe`](/api/language#add_pipe).
4. Make the **model data** available to the `Language` class by calling
   [`from_disk`](/api/language#from_disk) with the path to the model data
   directory.

So when you call this...

```python
nlp = spacy.load("en_core_web_sm")
```

... the model's `meta.json` tells spaCy to use the language `"en"` and the
pipeline `["tagger", "parser", "ner"]`. spaCy will then initialize
`spacy.lang.en.English`, and create each pipeline component and add it to the
processing pipeline. It'll then load in the model's data from its data directory
and return the modified `Language` class for you to use as the `nlp` object.

Fundamentally, a [spaCy model](/models) consists of three components: **the
weights**, i.e. binary data loaded in from a directory, a **pipeline** of
functions called in order, and **language data** like the tokenization rules and
annotation scheme. All of this is specific to each model, and defined in the
model's `meta.json` – for example, a Spanish NER model requires different
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
    component = nlp.create_pipe(name)   # 3. Create the pipeline components
    nlp.add_pipe(component)             # 4. Add the component to the pipeline
nlp.from_disk(model_data_path)          # 5. Load in the binary data
```

When you call `nlp` on a text, spaCy will **tokenize** it and then **call each
component** on the `Doc`, in order. Since the model data is loaded, the
components can access it to assign annotations to the `Doc` object, and
subsequently to the `Token` and `Span` which are only views of the `Doc`, and
don't own any data themselves. All components return the modified document,
which is then processed by the component next in the pipeline.

```python
### The pipeline under the hood
doc = nlp.make_doc(u"This is a sentence")   # create a Doc from raw text
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

spaCy ships with several built-in pipeline components that are also available in
the `Language.factories`. This means that you can initialize them by calling
[`nlp.create_pipe`](/api/language#create_pipe) with their string names and
require them in the pipeline settings in your model's `meta.json`.

> #### Usage
>
> ```python
> # Option 1: Import and initialize
> from spacy.pipeline import EntityRuler
> ruler = EntityRuler(nlp)
> nlp.add_pipe(ruler)
>
> # Option 2: Using nlp.create_pipe
> sentencizer = nlp.create_pipe("sentencizer")
> nlp.add_pipe(sentencizer)
> ```

| String name         | Component                                                        | Description                                                                                   |
| ------------------- | ---------------------------------------------------------------- | --------------------------------------------------------------------------------------------- |
| `tagger`            | [`Tagger`](/api/tagger)                                          | Assign part-of-speech-tags.                                                                   |
| `parser`            | [`DependencyParser`](/api/dependencyparser)                      | Assign dependency labels.                                                                     |
| `ner`               | [`EntityRecognizer`](/api/entityrecognizer)                      | Assign named entities.                                                                        |
| `textcat`           | [`TextCategorizer`](/api/textcategorizer)                        | Assign text categories.                                                                       |
| `entity_ruler`      | [`EntityRuler`](/api/entityruler)                                | Assign named entities based on pattern rules.                                                 |
| `sentencizer`       | [`Sentencizer`](/api/sentencizer)                                | Add rule-based sentence segmentation without the dependency parse.                            |
| `merge_noun_chunks` | [`merge_noun_chunks`](/api/pipeline-functions#merge_noun_chunks) | Merge all noun chunks into a single token. Should be added after the tagger and parser.       |
| `merge_entities`    | [`merge_entities`](/api/pipeline-functions#merge_entities)       | Merge all entities into a single token. Should be added after the entity recognizer.          |
| `merge_subtokens`   | [`merge_subtokens`](/api/pipeline-functions#merge_subtokens)     | Merge subtokens predicted by the parser into single tokens. Should be added after the parser. |

### Disabling and modifying pipeline components {#disabling}

If you don't need a particular component of the pipeline – for example, the
tagger or the parser, you can disable loading it. This can sometimes make a big
difference and improve loading speed. Disabled component names can be provided
to [`spacy.load`](/api/top-level#spacy.load),
[`Language.from_disk`](/api/language#from_disk) or the `nlp` object itself as a
list:

```python
nlp = spacy.load("en", disable=["parser", "tagger"])
nlp = English().from_disk("/model", disable=["ner"])
```

You can also use the [`remove_pipe`](/api/language#remove_pipe) method to remove
pipeline components from an existing pipeline, the
[`rename_pipe`](/api/language#rename_pipe) method to rename them, or the
[`replace_pipe`](/api/language#replace_pipe) method to replace them with a
custom component entirely (more details on this in the section on
[custom components](#custom-components).

```python
nlp.remove_pipe("parser")
nlp.rename_pipe("ner", "entityrecognizer")
nlp.replace_pipe("tagger", my_custom_tagger)
```

<Infobox title="Important note: disabling pipeline components" variant="warning">

Since spaCy v2.0 comes with better support for customizing the processing
pipeline components, the `parser`, `tagger` and `entity` keyword arguments have
been replaced with `disable`, which takes a list of pipeline component names.
This lets you disable pre-defined components when loading a model, or
initializing a Language class via [`from_disk`](/api/language#from_disk).

```diff
- nlp = spacy.load('en', tagger=False, entity=False)
- doc = nlp(u"I don't want parsed", parse=False)

+ nlp = spacy.load('en', disable=['ner'])
+ nlp.remove_pipe('parser')
+ doc = nlp(u"I don't want parsed")
```

</Infobox>

## Creating custom pipeline components {#custom-components}

A component receives a `Doc` object and can modify it – for example, by using
the current weights to make a prediction and set some annotation on the
document. By adding a component to the pipeline, you'll get access to the `Doc`
at any point **during processing** – instead of only being able to modify it
afterwards.

> #### Example
>
> ```python
> def my_component(doc):
>    # do something to the doc here
>    return doc
> ```

| Argument    | Type  | Description                                            |
| ----------- | ----- | ------------------------------------------------------ |
| `doc`       | `Doc` | The `Doc` object processed by the previous component.  |
| **RETURNS** | `Doc` | The `Doc` object processed by this pipeline component. |

Custom components can be added to the pipeline using the
[`add_pipe`](/api/language#add_pipe) method. Optionally, you can either specify
a component to add it **before or after**, tell spaCy to add it **first or
last** in the pipeline, or define a **custom name**. If no name is set and no
`name` attribute is present on your component, the function name is used.

> #### Example
>
> ```python
> nlp.add_pipe(my_component)
> nlp.add_pipe(my_component, first=True)
> nlp.add_pipe(my_component, before="parser")
> ```

| Argument | Type    | Description                                                              |
| -------- | ------- | ------------------------------------------------------------------------ |
| `last`   | bool    | If set to `True`, component is added **last** in the pipeline (default). |
| `first`  | bool    | If set to `True`, component is added **first** in the pipeline.          |
| `before` | unicode | String name of component to add the new component **before**.            |
| `after`  | unicode | String name of component to add the new component **after**.             |

### Example: A simple pipeline component {#custom-components-simple}

The following component receives the `Doc` in the pipeline and prints some
information about it: the number of tokens, the part-of-speech tags of the
tokens and a conditional message based on the document length.

> #### ✏️ Things to try
>
> 1. Add the component first in the pipeline by setting `first=True`. You'll see
>    that the part-of-speech tags are empty, because the component now runs
>    before the tagger and the tags aren't available yet.
> 2. Change the component `name` or remove the `name` argument. You should see
>    this change reflected in `nlp.pipe_names`.
> 3. Print `nlp.pipeline`. You'll see a list of tuples describing the component
>    name and the function that's called on the `Doc` object in the pipeline.

```python
### {executable="true"}
import spacy

def my_component(doc):
    print("After tokenization, this doc has {} tokens.".format(len(doc)))
    print("The part-of-speech tags are:", [token.pos_ for token in doc])
    if len(doc) < 10:
        print("This is a pretty short document.")
    return doc

nlp = spacy.load("en_core_web_sm")
nlp.add_pipe(my_component, name="print_info", last=True)
print(nlp.pipe_names)  # ['print_info', 'tagger', 'parser', 'ner']
doc = nlp(u"This is a sentence.")

```

Of course, you can also wrap your component as a class to allow initializing it
with custom settings and hold state within the component. This is useful for
**stateful components**, especially ones which **depend on shared data**. In the
following example, the custom component `EntityMatcher` can be initialized with
`nlp` object, a terminology list and an entity label. Using the
[`PhraseMatcher`](/api/phrasematcher), it then matches the terms in the `Doc`
and adds them to the existing entities.

<Infobox title="Important note" variant="warning">

As of v2.1.0, spaCy ships with the [`EntityRuler`](/api/entityruler), a pipeline
component for easy, rule-based named entity recognition. Its implementation is
similar to the `EntityMatcher` code shown below, but it includes some additional
features like support for phrase patterns and token patterns, handling overlaps
with existing entities and pattern export as JSONL.

We'll still keep the pipeline component example below, as it works well to
illustrate complex components. But if you're planning on using this type of
component in your application, you might find the `EntityRuler` more convenient.
[See here](/usage/rule-based-matching#entityruler) for more details and
examples.

</Infobox>

```python
### {executable="true"}
import spacy
from spacy.matcher import PhraseMatcher
from spacy.tokens import Span

class EntityMatcher(object):
    name = "entity_matcher"

    def __init__(self, nlp, terms, label):
        patterns = [nlp.make_doc(text) for text in terms]
        self.matcher = PhraseMatcher(nlp.vocab)
        self.matcher.add(label, None, *patterns)

    def __call__(self, doc):
        matches = self.matcher(doc)
        for match_id, start, end in matches:
            span = Span(doc, start, end, label=match_id)
            doc.ents = list(doc.ents) + [span]
        return doc

nlp = spacy.load("en_core_web_sm")
terms = (u"cat", u"dog", u"tree kangaroo", u"giant sea spider")
entity_matcher = EntityMatcher(nlp, terms, "ANIMAL")

nlp.add_pipe(entity_matcher, after="ner")

print(nlp.pipe_names)  # The components in the pipeline

doc = nlp(u"This is a text about Barack Obama and a tree kangaroo")
print([(ent.text, ent.label_) for ent in doc.ents])
```

### Example: Custom sentence segmentation logic {#component-example1}

Let's say you want to implement custom logic to improve spaCy's sentence
boundary detection. Currently, sentence segmentation is based on the dependency
parse, which doesn't always produce ideal results. The custom logic should
therefore be applied **after** tokenization, but _before_ the dependency parsing
– this way, the parser can also take advantage of the sentence boundaries.

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

def custom_sentencizer(doc):
    for i, token in enumerate(doc[:-2]):
        # Define sentence start if pipe + titlecase token
        if token.text == "|" and doc[i+1].is_title:
            doc[i+1].is_sent_start = True
        else:
            # Explicitly set sentence start to False otherwise, to tell
            # the parser to leave those tokens alone
            doc[i+1].is_sent_start = False
    return doc

nlp = spacy.load("en_core_web_sm")
nlp.add_pipe(custom_sentencizer, before="parser")  # Insert before the parser
doc = nlp(u"This is. A sentence. | This is. Another sentence.")
for sent in doc.sents:
    print(sent.text)
```

### Example: Pipeline component for entity matching and tagging with custom attributes {#component-example2}

This example shows how to create a spaCy extension that takes a terminology list
(in this case, single- and multi-word company names), matches the occurrences in
a document, labels them as `ORG` entities, merges the tokens and sets custom
`is_tech_org` and `has_tech_org` attributes. For efficient matching, the example
uses the [`PhraseMatcher`](/api/phrasematcher) which accepts `Doc` objects as
match patterns and works well for large terminology lists. It also ensures your
patterns will always match, even when you customize spaCy's tokenization rules.
When you call `nlp` on a text, the custom pipeline component is applied to the
`Doc`.

```python
https://github.com/explosion/spaCy/tree/master/examples/pipeline/custom_component_entities.py
```

Wrapping this functionality in a pipeline component allows you to reuse the
module with different settings, and have all pre-processing taken care of when
you call `nlp` on your text and receive a `Doc` object.

### Adding factories {#custom-components-factories}

When spaCy loads a model via its `meta.json`, it will iterate over the
`"pipeline"` setting, look up every component name in the internal factories and
call [`nlp.create_pipe`](/api/language#create_pipe) to initialize the individual
components, like the tagger, parser or entity recognizer. If your model uses
custom components, this won't work – so you'll have to tell spaCy **where to
find your component**. You can do this by writing to the `Language.factories`:

```python
from spacy.language import Language
Language.factories["entity_matcher"] = lambda nlp, **cfg: EntityMatcher(nlp, **cfg)
```

You can also ship the above code and your custom component in your packaged
model's `__init__.py`, so it's executed when you load your model. The `**cfg`
config parameters are passed all the way down from
[`spacy.load`](/api/top-level#spacy.load), so you can load the model and its
components with custom settings:

```python
nlp = spacy.load("your_custom_model", terms=(u"tree kangaroo"), label="ANIMAL")
```

<Infobox title="Important note" variant="warning">

When you load a model via its shortcut or package name, like `en_core_web_sm`,
spaCy will import the package and then call its `load()` method. This means that
custom code in the model's `__init__.py` will be executed, too. This is **not
the case** if you're loading a model from a path containing the model data.
Here, spaCy will only read in the `meta.json`. If you want to use custom
factories with a model loaded from a path, you need to add them to
`Language.factories` _before_ you load the model.

</Infobox>

## Extension attributes {#custom-components-attributes new="2"}

As of v2.0, spaCy allows you to set any custom attributes and methods on the
`Doc`, `Span` and `Token`, which become available as `Doc._`, `Span._` and
`Token._` – for example, `Token._.my_attr`. This lets you store additional
information relevant to your application, add new features and functionality to
spaCy, and implement your own models trained with other machine learning
libraries. It also lets you take advantage of spaCy's data structures and the
`Doc` object as the "single source of truth".

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
   Doc.set_extension("hello", method=lambda doc, name: "Hi {}!".format(name))
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

fruits = [u"apple", u"pear", u"banana", u"orange", u"strawberry"]
is_fruit_getter = lambda token: token.text in fruits
has_fruit_getter = lambda obj: any([t.text in fruits for t in obj])

Token.set_extension("is_fruit", getter=is_fruit_getter)
Doc.set_extension("has_fruit", getter=has_fruit_getter)
Span.set_extension("has_fruit", getter=has_fruit_getter)
```

> #### Usage example
>
> ```python
> doc = nlp(u"I have an apple and a melon")
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
https://github.com/explosion/spaCy/tree/master/examples/pipeline/custom_component_countries_api.py
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
class SimilarityModel(object):
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
plugins in spaCy v2.0, and we can't wait to see what you build with it! To get
you started, here are a few tips, tricks and best
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

  ```diff
  + nlp.add_pipe(my_custom_component)
  +     return nlp.from_disk(model_path)
  ```

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
returns their [BILUO tags](/api/annotation#biluo). Given an input like
`["A", "text", "about", "Facebook"]`, it will predict and return
`["O", "O", "O", "U-ORG"]`. To integrate it into your spaCy pipeline and make it
add those entities to the `doc.ents`, you can wrap it in a custom pipeline
component function and pass it the token texts from the `Doc` object received by
the component.

The [`gold.spans_from_biluo_tags`](/api/goldparse#spans_from_biluo_tags) is very
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
### {highlight="1,6-7"}
import your_custom_entity_recognizer
from spacy.gold import offsets_from_biluo_tags

def custom_ner_wrapper(doc):
    words = [token.text for token in doc]
    custom_entities = your_custom_entity_recognizer(words)
    doc.ents = spans_from_biluo_tags(doc, custom_entities)
    return doc
```

The `custom_ner_wrapper` can then be added to the pipeline of a blank model
using [`nlp.add_pipe`](/api/language#add_pipe). You can also replace the
existing entity recognizer of a pre-trained model with
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

> #### Example: spacy-stanfordnlp
>
> For an example of an end-to-end wrapper for statistical tokenization, tagging
> and parsing, check out
> [`spacy-stanfordnlp`](https://github.com/explosion/spacy-stanfordnlp). It uses
> a very similar approach to the example in this section – the only difference
> is that it fully replaces the `nlp` object instead of providing a pipeline
> component, since it also needs to handle tokenization.

```python
### {highlight="1,9,15-17"}
import your_custom_model
from spacy.symbols import POS, TAG, DEP, HEAD
from spacy.tokens import Doc
import numpy

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

<Infobox title="📖 Advanced usage, serialization and entry points">

For more details on how to write and package custom components, make them
available to spaCy via entry points and implement your own serialization
methods, check out the usage guide on
[saving and loading](/usage/saving-loading).

</Infobox>
