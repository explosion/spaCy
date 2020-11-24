---
title: Models & Languages
next: usage/facts-figures
menu:
  - ['Quickstart', 'quickstart']
  - ['Language Support', 'languages']
  - ['Installation & Usage', 'download']
  - ['Production Use', 'production']
---

spaCy's models can be installed as **Python packages**. This means that they're
a component of your application, just like any other module. They're versioned
and can be defined as a dependency in your `requirements.txt`. Models can be
installed from a download URL or a local directory, manually or via
[pip](https://pypi.python.org/pypi/pip). Their data can be located anywhere on
your file system.

> #### Important note
>
> If you're upgrading to spaCy v1.7.x or v2.x, you need to **download the new
> models**. If you've trained statistical models that use spaCy's annotations,
> you should **retrain your models** after updating spaCy. If you don't retrain,
> you may suffer train/test skew, which might decrease your accuracy.

## Quickstart {hidden="true"}

import QuickstartModels from 'widgets/quickstart-models.js'

<QuickstartModels title="Quickstart" id="quickstart" description="Install a default model, get the code to load it from within spaCy and an example to test it. For more options, see the section on available models below." />

## Language support {#languages}

spaCy currently provides support for the following languages. You can help by
[improving the existing language data](/usage/adding-languages#language-data)
and extending the tokenization patterns.
[See here](https://github.com/explosion/spaCy/issues/3056) for details on how to
contribute to model development.

> #### Usage note
>
> If a model is available for a language, you can download it using the
> [`spacy download`](/api/cli#download) command. In order to use languages that
> don't yet come with a model, you have to import them directly, or use
> [`spacy.blank`](/api/top-level#spacy.blank):
>
> ```python
> from spacy.lang.fi import Finnish
> nlp = Finnish()  # use directly
> nlp = spacy.blank("fi")  # blank instance
> ```
>
> If lemmatization rules are available for your language, make sure to install
> spaCy with the `lookups` option, or install
> [`spacy-lookups-data`](https://github.com/explosion/spacy-lookups-data)
> separately in the same environment:
>
> ```bash
> $ pip install spacy[lookups]
> ```

import Languages from 'widgets/languages.js'

<Languages />

### Multi-language support {#multi-language new="2"}

> ```python
> # Standard import
> from spacy.lang.xx import MultiLanguage
> nlp = MultiLanguage()
>
> # With lazy-loading
> from spacy.util import get_lang_class
> nlp = get_lang_class('xx')
> ```

As of v2.0, spaCy supports models trained on more than one language. This is
especially useful for named entity recognition. The language ID used for
multi-language or language-neutral models is `xx`. The language class, a generic
subclass containing only the base language data, can be found in
[`lang/xx`](https://github.com/explosion/spaCy/tree/master/spacy/lang/xx).

To load your model with the neutral, multi-language class, simply set
`"language": "xx"` in your [model package](/usage/training#models-generating)'s
`meta.json`. You can also import the class directly, or call
[`util.get_lang_class()`](/api/top-level#util.get_lang_class) for lazy-loading.

### Chinese language support {#chinese new=2.3}

The Chinese language class supports three word segmentation options:

> ```python
> from spacy.lang.zh import Chinese
>
> # Disable jieba to use character segmentation
> Chinese.Defaults.use_jieba = False
> nlp = Chinese()
>
> # Disable jieba through tokenizer config options
> cfg = {"use_jieba": False}
> nlp = Chinese(meta={"tokenizer": {"config": cfg}})
>
> # Load with "default" model provided by pkuseg
> cfg = {"pkuseg_model": "default", "require_pkuseg": True}
> nlp = Chinese(meta={"tokenizer": {"config": cfg}})
> ```

1. **Jieba:** `Chinese` uses [Jieba](https://github.com/fxsjy/jieba) for word
   segmentation by default. It's enabled when you create a new `Chinese`
   language class or call `spacy.blank("zh")`.
2. **Character segmentation:** Character segmentation is supported by disabling
   `jieba` and setting `Chinese.Defaults.use_jieba = False` _before_
   initializing the language class. As of spaCy v2.3.0, the `meta` tokenizer
   config options can be used to configure `use_jieba`.
3. **PKUSeg**: In spaCy v2.3.0, support for
   [PKUSeg](https://github.com/lancopku/PKUSeg-python) has been added to support
   better segmentation for Chinese OntoNotes and the new
   [Chinese models](/models/zh).

<Accordion title="Details on spaCy's PKUSeg API">

The `meta` argument of the `Chinese` language class supports the following
following tokenizer config settings:

| Name               | Type    | Description                                                                                          |
| ------------------ | ------- | ---------------------------------------------------------------------------------------------------- |
| `pkuseg_model`     | unicode | **Required:** Name of a model provided by `pkuseg` or the path to a local model directory.           |
| `pkuseg_user_dict` | unicode | Optional path to a file with one word per line which overrides the default `pkuseg` user dictionary. |
| `require_pkuseg`   | bool    | Overrides all `jieba` settings (optional but strongly recommended).                                  |

```python
### Examples
# Load "default" model
cfg = {"pkuseg_model": "default", "require_pkuseg": True}
nlp = Chinese(meta={"tokenizer": {"config": cfg}})

# Load local model
cfg = {"pkuseg_model": "/path/to/pkuseg_model", "require_pkuseg": True}
nlp = Chinese(meta={"tokenizer": {"config": cfg}})

# Override the user directory
cfg = {"pkuseg_model": "default", "require_pkuseg": True, "pkuseg_user_dict": "/path"}
nlp = Chinese(meta={"tokenizer": {"config": cfg}})
```

You can also modify the user dictionary on-the-fly:

```python
# Append words to user dict
nlp.tokenizer.pkuseg_update_user_dict(["中国", "ABC"])

# Remove all words from user dict and replace with new words
nlp.tokenizer.pkuseg_update_user_dict(["中国"], reset=True)

# Remove all words from user dict
nlp.tokenizer.pkuseg_update_user_dict([], reset=True)
```

</Accordion>

<Accordion title="Details on pretrained and custom Chinese models">

The [Chinese models](/models/zh) provided by spaCy include a custom `pkuseg`
model trained only on
[Chinese OntoNotes 5.0](https://catalog.ldc.upenn.edu/LDC2013T19), since the
models provided by `pkuseg` include data restricted to research use. For
research use, `pkuseg` provides models for several different domains
(`"default"`, `"news"` `"web"`, `"medicine"`, `"tourism"`) and for other uses,
`pkuseg` provides a simple
[training API](https://github.com/lancopku/pkuseg-python/blob/master/readme/readme_english.md#usage):

```python
import pkuseg
from spacy.lang.zh import Chinese

# Train pkuseg model
pkuseg.train("train.utf8", "test.utf8", "/path/to/pkuseg_model")
# Load pkuseg model in spaCy Chinese tokenizer
nlp = Chinese(meta={"tokenizer": {"config": {"pkuseg_model": "/path/to/pkuseg_model", "require_pkuseg": True}}})
```

</Accordion>

### Japanese language support {#japanese new=2.3}

> ```python
> from spacy.lang.ja import Japanese
>
> # Load SudachiPy with split mode A (default)
> nlp = Japanese()
>
> # Load SudachiPy with split mode B
> cfg = {"split_mode": "B"}
> nlp = Japanese(meta={"tokenizer": {"config": cfg}})
> ```

The Japanese language class uses
[SudachiPy](https://github.com/WorksApplications/SudachiPy) for word
segmentation and part-of-speech tagging. The default Japanese language class and
the provided Japanese models use SudachiPy split mode `A`.

The `meta` argument of the `Japanese` language class can be used to configure
the split mode to `A`, `B` or `C`.

<Infobox variant="warning">

If you run into errors related to `sudachipy`, which is currently under active
development, we suggest downgrading to `sudachipy==0.4.5`, which is the version
used for training the current [Japanese models](/models/ja).

</Infobox>

## Installing and using models {#download}

> #### Downloading models in spaCy < v1.7
>
> In older versions of spaCy, you can still use the old download commands. This
> will download and install the models into the `spacy/data` directory.
>
> ```bash
>  python -m spacy.en.download all
>  python -m spacy.de.download all
>  python -m spacy.en.download glove
> ```
>
> The old models are also
> [attached to the v1.6.0 release](https://github.com/explosion/spaCy/tree/v1.6.0).
> To download and install them manually, unpack the archive, drop the contained
> directory into `spacy/data`.

The easiest way to download a model is via spaCy's
[`download`](/api/cli#download) command. It takes care of finding the
best-matching model compatible with your spaCy installation.

```bash
# Download best-matching version of specific model for your spaCy installation
python -m spacy download en_core_web_sm

# Out-of-the-box: download best-matching default model and create shortcut link
python -m spacy download en

# Download exact model version (doesn't create shortcut link)
python -m spacy download en_core_web_sm-2.2.0 --direct
```

The download command will [install the model](/usage/models#download-pip) via
pip and place the package in your `site-packages` directory.

```bash
pip install spacy
python -m spacy download en_core_web_sm
```

```python
import spacy
nlp = spacy.load("en_core_web_sm")
doc = nlp("This is a sentence.")
```

<Infobox title="Important note" variant="warning">

If you're downloading the models using a shortcut like `"en"`, spaCy will create
a symlink within the `spacy/data` directory. This means that your user needs the
**required permissions**. If you've installed spaCy to a system directory and
don't have admin privileges, the model linking may fail. The easiest solution is
to re-run the command as admin, set the `--user` flag or use a virtual
environment. For more info on this, see the
[troubleshooting guide](/usage/#symlink-privilege).

</Infobox>

### Installation via pip {#download-pip}

To download a model directly using [pip](https://pypi.python.org/pypi/pip),
point `pip install` to the URL or local path of the archive file. To find the
direct link to a model, head over to the
[model releases](https://github.com/explosion/spacy-models/releases), right
click on the archive link and copy it to your clipboard.

```bash
# With external URL
pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-2.2.0/en_core_web_sm-2.2.0.tar.gz

# With local file
pip install /Users/you/en_core_web_sm-2.2.0.tar.gz
```

By default, this will install the model into your `site-packages` directory. You
can then use `spacy.load()` to load it via its package name, create a
[shortcut link](#usage-link) to assign it a custom name, or
[import it](#usage-import) explicitly as a module. If you need to download
models as part of an automated process, we recommend using pip with a direct
link, instead of relying on spaCy's [`download`](/api/cli#download) command.

You can also add the direct download link to your application's
`requirements.txt`. For more details, see the section on
[working with models in production](#production).

### Manual download and installation {#download-manual}

In some cases, you might prefer downloading the data manually, for example to
place it into a custom directory. You can download the model via your browser
from the [latest releases](https://github.com/explosion/spacy-models/releases),
or configure your own download script using the URL of the archive file. The
archive consists of a model directory that contains another directory with the
model data.

```yaml
### Directory structure {highlight="7"}
└── en_core_web_md-2.2.0.tar.gz       # downloaded archive
    ├── meta.json                     # model meta data
    ├── setup.py                      # setup file for pip installation
    └── en_core_web_md                # 📦 model package
        ├── __init__.py               # init for pip installation
        ├── meta.json                 # model meta data
        └── en_core_web_md-2.2.0      # model data
```

You can place the **model package directory** anywhere on your local file
system. To use it with spaCy, assign it a name by creating a shortcut link for
the data directory.

### Using models with spaCy {#usage}

To load a model, use [`spacy.load`](/api/top-level#spacy.load) with the model's
shortcut link, package name or a path to the data directory:

```python
import spacy
nlp = spacy.load("en_core_web_sm")           # load model package "en_core_web_sm"
nlp = spacy.load("/path/to/en_core_web_sm")  # load package from a directory
nlp = spacy.load("en")                       # load model with shortcut link "en"

doc = nlp("This is a sentence.")
```

<Infobox title="Tip: Preview model info">

You can use the [`info`](/api/cli#info) command or
[`spacy.info()`](/api/top-level#spacy.info) method to print a model's meta data
before loading it. Each `Language` object with a loaded model also exposes the
model's meta data as the attribute `meta`. For example, `nlp.meta['version']`
will return the model's version.

</Infobox>

### Using custom shortcut links {#usage-link}

While previous versions of spaCy required you to maintain a data directory
containing the models for each installation, you can now choose **how and where
you want to keep your data**. For example, you could download all models
manually and put them into a local directory. Whenever your spaCy projects need
a model, you create a shortcut link to tell spaCy to load it from there. This
means you'll never end up with duplicate data.

The [`link`](/api/cli#link) command will create a symlink in the `spacy/data`
directory.

> #### Why does spaCy use symlinks?
>
> Symlinks were originally introduced to maintain backwards compatibility, as
> older versions expected model data to live within `spacy/data`. However, we
> decided to keep using them in v2.0 instead of opting for a config file.
> There'll always be a need for assigning and saving custom model names or IDs.
> And your system already comes with a native solution to mapping unicode
> aliases to file paths: symbolic links.

```bash
$ python -m spacy link [package name or path] [shortcut] [--force]
```

The first argument is the **package name** (if the model was installed via pip),
or a local path to the the **model package**. The second argument is the
internal name you want to use for the model. Setting the `--force` flag will
overwrite any existing links.

```bash
### Examples
# set up shortcut link to load installed package as "en_default"
python -m spacy link en_core_web_md en_default

# set up shortcut link to load local model as "my_amazing_model"
python -m spacy link /Users/you/model my_amazing_model
```

<Infobox title="Important note" variant="warning">

In order to create a symlink, your user needs the **required permissions**. If
you've installed spaCy to a system directory and don't have admin privileges,
the `spacy link` command may fail. The easiest solution is to re-run the command
as admin, set the `--user` flag or use a virtual environment. For more info on
this, see the [troubleshooting guide](/usage/#symlink-privilege).

</Infobox>

### Importing models as modules {#usage-import}

If you've installed a model via spaCy's downloader, or directly via pip, you can
also `import` it and then call its `load()` method with no arguments:

```python
### {executable="true"}
import en_core_web_sm

nlp = en_core_web_sm.load()
doc = nlp("This is a sentence.")
```

How you choose to load your models ultimately depends on personal preference.
However, **for larger code bases**, we usually recommend native imports, as this
will make it easier to integrate models with your existing build process,
continuous integration workflow and testing framework. It'll also prevent you
from ever trying to load a model that is not installed, as your code will raise
an `ImportError` immediately, instead of failing somewhere down the line when
calling `spacy.load()`.

For more details, see the section on
[working with models in production](#production).

### Using your own models {#own-models}

If you've trained your own model, for example for
[additional languages](/usage/adding-languages) or
[custom named entities](/usage/training#ner), you can save its state using the
[`Language.to_disk()`](/api/language#to_disk) method. To make the model more
convenient to deploy, we recommend wrapping it as a Python package.

For more information and a detailed guide on how to package your model, see the
documentation on [saving and loading models](/usage/saving-loading#models).

## Using models in production {#production}

If your application depends on one or more models, you'll usually want to
integrate them into your continuous integration workflow and build process.
While spaCy provides a range of useful helpers for downloading, linking and
loading models, the underlying functionality is entirely based on native Python
packages. This allows your application to handle a model like any other package
dependency.

For an example of an automated model training and build process, see
[this overview](/usage/training#example-training-spacy) of how we're training
and packaging our models for spaCy.

### Downloading and requiring model dependencies {#models-download}

spaCy's built-in [`download`](/api/cli#download) command is mostly intended as a
convenient, interactive wrapper. It performs compatibility checks and prints
detailed error messages and warnings. However, if you're downloading models as
part of an automated build process, this only adds an unnecessary layer of
complexity. If you know which models your application needs, you should be
specifying them directly.

Because all models are valid Python packages, you can add them to your
application's `requirements.txt`. If you're running your own internal PyPi
installation, you can upload the models there. pip's
[requirements file format](https://pip.pypa.io/en/latest/reference/pip_install/#requirements-file-format)
supports both package names to download via a PyPi server, as well as direct
URLs.

```text
### requirements.txt
spacy>=2.2.0,<3.0.0
https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-2.2.0/en_core_web_sm-2.2.0.tar.gz#egg=en_core_web_sm
```

Specifying `#egg=` with the package name tells pip which package to expect from
the download URL. This way, the package won't be re-downloaded and overwritten
if it's already installed - just like when you're downloading a package from
PyPi.

All models are versioned and specify their spaCy dependency. This ensures
cross-compatibility and lets you specify exact version requirements for each
model. If you've trained your own model, you can use the
[`package`](/api/cli#package) command to generate the required meta data and
turn it into a loadable package.

### Loading and testing models {#models-loading}

Downloading models directly via pip won't call spaCy's link
[`package`](/api/cli#link) command, which creates symlinks for model shortcuts.
This means that you'll have to run this command separately, or use the native
`import` syntax to load the models:

```python
import en_core_web_sm
nlp = en_core_web_sm.load()
```

In general, this approach is recommended for larger code bases, as it's more
"native", and doesn't depend on symlinks or rely on spaCy's loader to resolve
string names to model packages. If a model can't be imported, Python will raise
an `ImportError` immediately. And if a model is imported but not used, any
linter will catch that.

Similarly, it'll give you more flexibility when writing tests that require
loading models. For example, instead of writing your own `try` and `except`
logic around spaCy's loader, you can use
[pytest](http://pytest.readthedocs.io/en/latest/)'s
[`importorskip()`](https://docs.pytest.org/en/latest/builtin.html#_pytest.outcomes.importorskip)
method to only run a test if a specific model or model version is installed.
Each model package exposes a `__version__` attribute which you can also use to
perform your own version compatibility checks before loading a model.
