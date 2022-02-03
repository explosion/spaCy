---
title: Models & Languages
next: usage/facts-figures
menu:
  - ['Quickstart', 'quickstart']
  - ['Language Support', 'languages']
  - ['Installation & Usage', 'download']
  - ['Production Use', 'production']
---

spaCy's trained pipelines can be installed as **Python packages**. This means
that they're a component of your application, just like any other module.
They're versioned and can be defined as a dependency in your `requirements.txt`.
Trained pipelines can be installed from a download URL or a local directory,
manually or via [pip](https://pypi.python.org/pypi/pip). Their data can be
located anywhere on your file system.

> #### Important note
>
> If you're upgrading to spaCy v3.x, you need to **download the new pipeline
> packages**. If you've trained your own pipelines, you need to **retrain** them
> after updating spaCy.

## Quickstart {hidden="true"}

import QuickstartModels from 'widgets/quickstart-models.js'

<QuickstartModels title="Quickstart" id="quickstart" description="Install a default trained pipeline package, get the code to load it from within spaCy and an example to test it. For more options, see the section on available packages below." />

## Language support {#languages}

spaCy currently provides support for the following languages. You can help by
improving the existing [language data](/usage/linguistic-features#language-data)
and extending the tokenization patterns.
[See here](https://github.com/explosion/spaCy/issues/3056) for details on how to
contribute to development. Also see the
[training documentation](/usage/training) for how to train your own pipelines on
your data.

> #### Usage note
>
> If a trained pipeline is available for a language, you can download it using
> the [`spacy download`](/api/cli#download) command. In order to use languages
> that don't yet come with a trained pipeline, you have to import them directly,
> or use [`spacy.blank`](/api/top-level#spacy.blank):
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
> $ pip install -U %%SPACY_PKG_NAME[lookups]%%SPACY_PKG_FLAGS
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
> nlp = spacy.blank("xx")
> ```

spaCy also supports pipelines trained on more than one language. This is
especially useful for named entity recognition. The language ID used for
multi-language or language-neutral pipelines is `xx`. The language class, a
generic subclass containing only the base language data, can be found in
[`lang/xx`](%%GITHUB_SPACY/spacy/lang/xx).

To train a pipeline using the neutral multi-language class, you can set
`lang = "xx"` in your [training config](/usage/training#config). You can also
import the `MultiLanguage` class directly, or call
[`spacy.blank("xx")`](/api/top-level#spacy.blank) for lazy-loading.

### Chinese language support {#chinese new="2.3"}

The Chinese language class supports three word segmentation options, `char`,
`jieba` and `pkuseg`.

> #### Manual setup
>
> ```python
> from spacy.lang.zh import Chinese
>
> # Character segmentation (default)
> nlp = Chinese()
> # Jieba
> cfg = {"segmenter": "jieba"}
> nlp = Chinese.from_config({"nlp": {"tokenizer": cfg}})
> # PKUSeg with "mixed" model provided by pkuseg
> cfg = {"segmenter": "pkuseg"}
> nlp = Chinese.from_config({"nlp": {"tokenizer": cfg}})
> nlp.tokenizer.initialize(pkuseg_model="mixed")
> ```

```ini
### config.cfg
[nlp.tokenizer]
@tokenizers = "spacy.zh.ChineseTokenizer"
segmenter = "char"
```

| Segmenter | Description                                                                                                                                                                                                                                                                                |
| --------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `char`    | **Character segmentation:** Character segmentation is the default segmentation option. It's enabled when you create a new `Chinese` language class or call `spacy.blank("zh")`.                                                                                                            |
| `jieba`   | **Jieba:** to use [Jieba](https://github.com/fxsjy/jieba) for word segmentation, you can set the option `segmenter` to `"jieba"`.                                                                                                                                                          |
| `pkuseg`  | **PKUSeg**: As of spaCy v2.3.0, support for [PKUSeg](https://github.com/explosion/spacy-pkuseg) has been added to support better segmentation for Chinese OntoNotes and the provided [Chinese pipelines](/models/zh). Enable PKUSeg by setting tokenizer option `segmenter` to `"pkuseg"`. |

<Infobox title="Changed in v3.0" variant="warning">

In v3.0, the default word segmenter has switched from Jieba to character
segmentation. Because the `pkuseg` segmenter depends on a model that can be
loaded from a file, the model is loaded on
[initialization](/usage/training#config-lifecycle) (typically before training).
This ensures that your packaged Chinese model doesn't depend on a local path at
runtime.

</Infobox>

<Accordion title="Details on spaCy's Chinese API">

The `initialize` method for the Chinese tokenizer class supports the following
config settings for loading `pkuseg` models:

| Name               | Description                                                                                                                                                            |
| ------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `pkuseg_model`     | Name of a model provided by `spacy-pkuseg` or the path to a local model directory. ~~str~~                                                                             |
| `pkuseg_user_dict` | Optional path to a file with one word per line which overrides the default `pkuseg` user dictionary. Defaults to `"default"`, the default provided dictionary. ~~str~~ |

The initialization settings are typically provided in the
[training config](/usage/training#config) and the data is loaded in before
training and serialized with the model. This allows you to load the data from a
local path and save out your pipeline and config, without requiring the same
local path at runtime. See the usage guide on the
[config lifecycle](/usage/training#config-lifecycle) for more background on
this.

```ini
### config.cfg
[initialize]

[initialize.tokenizer]
pkuseg_model = "/path/to/model"
pkuseg_user_dict = "default"
```

You can also initialize the tokenizer for a blank language class by calling its
`initialize` method:

```python
### Examples
# Initialize the pkuseg tokenizer
cfg = {"segmenter": "pkuseg"}
nlp = Chinese.from_config({"nlp": {"tokenizer": cfg}})

# Load spaCy's OntoNotes model
nlp.tokenizer.initialize(pkuseg_model="spacy_ontonotes")

# Load pkuseg's "news" model
nlp.tokenizer.initialize(pkuseg_model="news")

# Load local model
nlp.tokenizer.initialize(pkuseg_model="/path/to/pkuseg_model")

# Override the user directory
nlp.tokenizer.initialize(pkuseg_model="spacy_ontonotes", pkuseg_user_dict="/path/to/user_dict")
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

<Accordion title="Details on trained and custom Chinese pipelines" spaced>

The [Chinese pipelines](/models/zh) provided by spaCy include a custom `pkuseg`
model trained only on
[Chinese OntoNotes 5.0](https://catalog.ldc.upenn.edu/LDC2013T19), since the
models provided by `pkuseg` include data restricted to research use. For
research use, `pkuseg` provides models for several different domains (`"mixed"`
(equivalent to `"default"` from `pkuseg` packages), `"news"` `"web"`,
`"medicine"`, `"tourism"`) and for other uses, `pkuseg` provides a simple
[training API](https://github.com/explosion/spacy-pkuseg/blob/master/readme/readme_english.md#usage):

```python
import spacy_pkuseg as pkuseg
from spacy.lang.zh import Chinese

# Train pkuseg model
pkuseg.train("train.utf8", "test.utf8", "/path/to/pkuseg_model")

# Load pkuseg model in spaCy Chinese tokenizer
cfg = {"segmenter": "pkuseg"}
nlp = Chinese.from_config({"nlp": {"tokenizer": cfg}})
nlp.tokenizer.initialize(pkuseg_model="/path/to/pkuseg_model")
```

</Accordion>

### Japanese language support {#japanese new=2.3}

> #### Manual setup
>
> ```python
> from spacy.lang.ja import Japanese
>
> # Load SudachiPy with split mode A (default)
> nlp = Japanese()
> # Load SudachiPy with split mode B
> cfg = {"split_mode": "B"}
> nlp = Japanese.from_config({"nlp": {"tokenizer": cfg}})
> ```

The Japanese language class uses
[SudachiPy](https://github.com/WorksApplications/SudachiPy) for word
segmentation and part-of-speech tagging. The default Japanese language class and
the provided Japanese pipelines use SudachiPy split mode `A`. The tokenizer
config can be used to configure the split mode to `A`, `B` or `C`.

```ini
### config.cfg
[nlp.tokenizer]
@tokenizers = "spacy.ja.JapaneseTokenizer"
split_mode = "A"
```

Extra information, such as reading, inflection form, and the SudachiPy
normalized form, is available in `Token.morph`. For `B` or `C` split modes,
subtokens are stored in `Doc.user_data["sub_tokens"]`.

<Infobox variant="warning">

If you run into errors related to `sudachipy`, which is currently under active
development, we suggest downgrading to `sudachipy==0.4.9`, which is the version
used for training the current [Japanese pipelines](/models/ja).

</Infobox>

## Installing and using trained pipelines {#download}

The easiest way to download a trained pipeline is via spaCy's
[`download`](/api/cli#download) command. It takes care of finding the
best-matching package compatible with your spaCy installation.

> #### Important note for v3.0
>
> Note that as of spaCy v3.0, shortcut links like `en` that create (potentially
> brittle) symlinks in your spaCy installation are **deprecated**. To download
> and load an installed pipeline package, use its full name:
>
> ```diff
> - python -m spacy download en
> + python -m spacy download en_core_web_sm
> ```
>
> ```diff
> - nlp = spacy.load("en")
> + nlp = spacy.load("en_core_web_sm")
> ```

```cli
# Download best-matching version of a package for your spaCy installation
$ python -m spacy download en_core_web_sm

# Download exact package version
$ python -m spacy download en_core_web_sm-3.0.0 --direct
```

The download command will [install the package](/usage/models#download-pip) via
pip and place the package in your `site-packages` directory.

```cli
$ pip install -U %%SPACY_PKG_NAME%%SPACY_PKG_FLAGS
$ python -m spacy download en_core_web_sm
```

```python
import spacy
nlp = spacy.load("en_core_web_sm")
doc = nlp("This is a sentence.")
```

If you're in a **Jupyter notebook** or similar environment, you can use the `!`
prefix to
[execute commands](https://ipython.org/ipython-doc/3/interactive/tutorial.html#system-shell-commands).
Make sure to **restart your kernel** or runtime after installation (just like
you would when installing other Python packages) to make sure that the installed
pipeline package can be found.

```cli
!python -m spacy download en_core_web_sm
```

### Installation via pip {#download-pip}

To download a trained pipeline directly using
[pip](https://pypi.python.org/pypi/pip), point `pip install` to the URL or local
path of the wheel file or archive. Installing the wheel is usually more
efficient. To find the direct link to a package, head over to the
[releases](https://github.com/explosion/spacy-models/releases), right click on
the archive link and copy it to your clipboard.

```bash
# With external URL
$ pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.0.0/en_core_web_sm-3.0.0-py3-none-any.whl
$ pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.0.0/en_core_web_sm-3.0.0.tar.gz

# With local file
$ pip install /Users/you/en_core_web_sm-3.0.0-py3-none-any.whl
$ pip install /Users/you/en_core_web_sm-3.0.0.tar.gz
```

By default, this will install the pipeline package into your `site-packages`
directory. You can then use `spacy.load` to load it via its package name or
[import it](#usage-import) explicitly as a module. If you need to download
pipeline packages as part of an automated process, we recommend using pip with a
direct link, instead of relying on spaCy's [`download`](/api/cli#download)
command.

You can also add the direct download link to your application's
`requirements.txt`. For more details, see the section on
[working with pipeline packages in production](#production).

### Manual download and installation {#download-manual}

In some cases, you might prefer downloading the data manually, for example to
place it into a custom directory. You can download the package via your browser
from the [latest releases](https://github.com/explosion/spacy-models/releases),
or configure your own download script using the URL of the archive file. The
archive consists of a package directory that contains another directory with the
pipeline data.

```yaml
### Directory structure {highlight="6"}
└── en_core_web_md-3.0.0.tar.gz       # downloaded archive
    ├── setup.py                      # setup file for pip installation
    ├── meta.json                     # copy of pipeline meta
    └── en_core_web_md                # 📦 pipeline package
        ├── __init__.py               # init for pip installation
        └── en_core_web_md-3.0.0      # pipeline data
            ├── config.cfg            # pipeline config
            ├── meta.json             # pipeline meta
            └── ...                   # directories with component data
```

You can place the **pipeline package directory** anywhere on your local file
system.

### Installation from Python {#download-python}

Since the [`spacy download`](/api/cli#download) command installs the pipeline as
a **Python package**, we always recommend running it from the command line, just
like you install other Python packages with `pip install`. However, if you need
to, or if you want to integrate the download process into another CLI command,
you can also import and call the `download` function used by the CLI via Python.

<Infobox variant="warning">

Keep in mind that the `download` command installs a Python package into your
environment. In order for it to be found after installation, you will need to
**restart or reload** your Python process so that new packages are recognized.

</Infobox>

```python
import spacy
spacy.cli.download("en_core_web_sm")
```

### Using trained pipelines with spaCy {#usage}

To load a pipeline package, use [`spacy.load`](/api/top-level#spacy.load) with
the package name or a path to the data directory:

> #### Important note for v3.0
>
> Note that as of spaCy v3.0, shortcut links like `en` that create (potentially
> brittle) symlinks in your spaCy installation are **deprecated**. To download
> and load an installed pipeline package, use its full name:
>
> ```diff
> - python -m spacy download en
> + python -m spacy download en_core_web_sm
> ```

```python
import spacy
nlp = spacy.load("en_core_web_sm")           # load package "en_core_web_sm"
nlp = spacy.load("/path/to/en_core_web_sm")  # load package from a directory

doc = nlp("This is a sentence.")
```

<Infobox title="Tip: Preview model info" emoji="💡">

You can use the [`info`](/api/cli#info) command or
[`spacy.info()`](/api/top-level#spacy.info) method to print a pipeline
package's meta data before loading it. Each `Language` object with a loaded
pipeline also exposes the pipeline's meta data as the attribute `meta`. For
example, `nlp.meta['version']` will return the package version.

</Infobox>

### Importing pipeline packages as modules {#usage-import}

If you've installed a trained pipeline via [`spacy download`](/api/cli#download)
or directly via pip, you can also `import` it and then call its `load()` method
with no arguments:

```python
### {executable="true"}
import en_core_web_sm

nlp = en_core_web_sm.load()
doc = nlp("This is a sentence.")
```

How you choose to load your trained pipelines ultimately depends on personal
preference. However, **for larger code bases**, we usually recommend native
imports, as this will make it easier to integrate pipeline packages with your
existing build process, continuous integration workflow and testing framework.
It'll also prevent you from ever trying to load a package that is not installed,
as your code will raise an `ImportError` immediately, instead of failing
somewhere down the line when calling `spacy.load()`. For more details, see the
section on [working with pipeline packages in production](#production).

## Using trained pipelines in production {#production}

If your application depends on one or more trained pipeline packages, you'll
usually want to integrate them into your continuous integration workflow and
build process. While spaCy provides a range of useful helpers for downloading
and loading pipeline packages, the underlying functionality is entirely based on
native Python packaging. This allows your application to handle a spaCy pipeline
like any other package dependency.

### Downloading and requiring package dependencies {#models-download}

spaCy's built-in [`download`](/api/cli#download) command is mostly intended as a
convenient, interactive wrapper. It performs compatibility checks and prints
detailed error messages and warnings. However, if you're downloading pipeline
packages as part of an automated build process, this only adds an unnecessary
layer of complexity. If you know which packages your application needs, you
should be specifying them directly.

Because pipeline packages are valid Python packages, you can add them to your
application's `requirements.txt`. If you're running your own internal PyPi
installation, you can upload the pipeline packages there. pip's
[requirements file format](https://pip.pypa.io/en/latest/reference/pip_install/#requirements-file-format)
supports both package names to download via a PyPi server, as well as direct
URLs.

```text
### requirements.txt
spacy>=3.0.0,<4.0.0
https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.0.0/en_core_web_sm-3.0.0.tar.gz#egg=en_core_web_sm
```

Specifying `#egg=` with the package name tells pip which package to expect from
the download URL. This way, the package won't be re-downloaded and overwritten
if it's already installed - just like when you're downloading a package from
PyPi.

All pipeline packages are versioned and specify their spaCy dependency. This
ensures cross-compatibility and lets you specify exact version requirements for
each pipeline. If you've [trained](/usage/training) your own pipeline, you can
use the [`spacy package`](/api/cli#package) command to generate the required
meta data and turn it into a loadable package.

### Loading and testing pipeline packages {#models-loading}

Pipeline packages are regular Python packages, so you can also import them as a
package using Python's native `import` syntax, and then call the `load` method
to load the data and return an `nlp` object:

```python
import en_core_web_sm
nlp = en_core_web_sm.load()
```

In general, this approach is recommended for larger code bases, as it's more
"native", and doesn't rely on spaCy's loader to resolve string names to
packages. If a package can't be imported, Python will raise an `ImportError`
immediately. And if a package is imported but not used, any linter will catch
that.

Similarly, it'll give you more flexibility when writing tests that require
loading pipelines. For example, instead of writing your own `try` and `except`
logic around spaCy's loader, you can use
[pytest](http://pytest.readthedocs.io/en/latest/)'s
[`importorskip()`](https://docs.pytest.org/en/latest/builtin.html#_pytest.outcomes.importorskip)
method to only run a test if a specific pipeline package or version is
installed. Each pipeline package exposes a `__version__` attribute which you can
also use to perform your own version compatibility checks before loading it.
