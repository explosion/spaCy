---
title: Install spaCy
next: /usage/models
menu:
  - ['Quickstart', 'quickstart']
  - ['Instructions', 'installation']
  - ['Troubleshooting', 'troubleshooting']
  - ['Changelog', 'changelog']
---

spaCy is compatible with **64-bit CPython 3.6+** and runs on **Unix/Linux**,
**macOS/OS X** and **Windows**. The latest spaCy releases are available over
[pip](https://pypi.python.org/pypi/spacy) and
[conda](https://anaconda.org/conda-forge/spacy).

> #### 📖 Looking for the old docs?
>
> To help you make the transition from v2.x to v3.0, we've uploaded the old
> website to [**v2.spacy.io**](https://v2.spacy.io/docs). To see what's changed
> and how to migrate, see the guide on [v3.0 guide](/usage/v3).

## Quickstart {hidden="true"}

import QuickstartInstall from 'widgets/quickstart-install.js'

<QuickstartInstall title="Quickstart" id="quickstart" />

## Installation instructions {#installation}

### pip {#pip}

Using pip, spaCy releases are available as source packages and binary wheels.

```bash
$ pip install -U spacy
```

> #### Download models
>
> After installation you need to download a language model. For more info and
> available models, see the [docs on models](/models).
>
> ```cli
> $ python -m spacy download en_core_web_sm
>
> >>> import spacy
> >>> nlp = spacy.load("en_core_web_sm")
> ```

<Infobox variant="warning">

To install additional data tables for lemmatization you can run
`pip install spacy[lookups]` or install
[`spacy-lookups-data`](https://github.com/explosion/spacy-lookups-data)
separately. The lookups package is needed to create blank models with
lemmatization data, and to lemmatize in languages that don't yet come with
pretrained models and aren't powered by third-party libraries.

</Infobox>

When using pip it is generally recommended to install packages in a virtual
environment to avoid modifying system state:

```bash
$ python -m venv .env
$ source .env/bin/activate
$ pip install spacy
```

### conda {#conda}

Thanks to our great community, we've been able to re-add conda support. You can
also install spaCy via `conda-forge`:

```bash
$ conda install -c conda-forge spacy
```

For the feedstock including the build recipe and configuration, check out
[this repository](https://github.com/conda-forge/spacy-feedstock). Improvements
and pull requests to the recipe and setup are always appreciated.

### Upgrading spaCy {#upgrading}

> #### Upgrading from v2 to v3
>
> Although we've tried to keep breaking changes to a minimum, upgrading from
> spaCy v2.x to v3.x may still require some changes to your code base. For
> details see the sections on [backwards incompatibilities](/usage/v3#incompat)
> and [migrating](/usage/v3#migrating). Also remember to download the new
> models, and retrain your own models.

When updating to a newer version of spaCy, it's generally recommended to start
with a clean virtual environment. If you're upgrading to a new major version,
make sure you have the latest **compatible models** installed, and that there
are no old and incompatible model packages left over in your environment, as
this can often lead to unexpected results and errors. If you've trained your own
models, keep in mind that your train and runtime inputs must match. This means
you'll have to **retrain your models** with the new version.

spaCy also provides a [`validate`](/api/cli#validate) command, which lets you
verify that all installed models are compatible with your spaCy version. If
incompatible models are found, tips and installation instructions are printed.
The command is also useful to detect out-of-sync model links resulting from
links created in different virtual environments. It's recommended to run the
command with `python -m` to make sure you're executing the correct version of
spaCy.

```cli
$ pip install -U spacy
$ python -m spacy validate
```

### Run spaCy with GPU {#gpu new="2.0.14"}

As of v2.0, spaCy comes with neural network models that are implemented in our
machine learning library, [Thinc](https://github.com/explosion/thinc). For GPU
support, we've been grateful to use the work of Chainer's
[CuPy](https://cupy.chainer.org) module, which provides a numpy-compatible
interface for GPU arrays.

spaCy can be installed on GPU by specifying `spacy[cuda]`, `spacy[cuda90]`,
`spacy[cuda91]`, `spacy[cuda92]`, `spacy[cuda100]`, `spacy[cuda101]` or
`spacy[cuda102]`. If you know your cuda version, using the more explicit
specifier allows cupy to be installed via wheel, saving some compilation time.
The specifiers should install [`cupy`](https://cupy.chainer.org).

```bash
$ pip install -U spacy[cuda92]
```

Once you have a GPU-enabled installation, the best way to activate it is to call
[`spacy.prefer_gpu`](/api/top-level#spacy.prefer_gpu) or
[`spacy.require_gpu()`](/api/top-level#spacy.require_gpu) somewhere in your
script before any models have been loaded. `require_gpu` will raise an error if
no GPU is available.

```python
import spacy

spacy.prefer_gpu()
nlp = spacy.load("en_core_web_sm")
```

### Compile from source {#source}

The other way to install spaCy is to clone its
[GitHub repository](https://github.com/explosion/spaCy) and build it from
source. That is the common way if you want to make changes to the code base.
You'll need to make sure that you have a development environment consisting of a
Python distribution including header files, a compiler,
[pip](https://pip.pypa.io/en/latest/installing/),
[virtualenv](https://virtualenv.pypa.io/) and [git](https://git-scm.com)
installed. The compiler part is the trickiest. How to do that depends on your
system. See notes on [Ubuntu](#source-ubuntu), [macOS / OS X](#source-osx) and
[Windows](#source-windows) for details.

```bash
$ python -m pip install -U pip                  # update pip
$ git clone https://github.com/explosion/spaCy  # clone spaCy
$ cd spaCy                                      # navigate into dir

$ python -m venv .env                           # create environment in .env
$ source .env/bin/activate                      # activate virtual env
$ export PYTHONPATH=`pwd`                       # set Python path to spaCy dir
$ pip install -r requirements.txt               # install all requirements
$ python setup.py build_ext --inplace           # compile spaCy
```

Compared to regular install via pip, the
[`requirements.txt`](https://github.com/explosion/spaCy/tree/master/requirements.txt)
additionally installs developer dependencies such as Cython. See the
[quickstart widget](#quickstart) to get the right commands for your platform and
Python version.

#### Ubuntu {#source-ubuntu}

Install system-level dependencies via `apt-get`:

```bash
$ sudo apt-get install build-essential python-dev git
```

#### macOS / OS X {#source-osx}

Install a recent version of [XCode](https://developer.apple.com/xcode/),
including the so-called "Command Line Tools". macOS and OS X ship with Python
and git preinstalled.

#### Windows {#source-windows}

Install a version of the
[Visual C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/)
or
[Visual Studio Express](https://www.visualstudio.com/vs/visual-studio-express/)
that matches the version that was used to compile your Python interpreter.

### Run tests {#run-tests}

spaCy comes with an
[extensive test suite](https://github.com/explosion/spaCy/tree/master/spacy/tests).
In order to run the tests, you'll usually want to clone the
[repository](https://github.com/explosion/spaCy/tree/master/) and
[build spaCy from source](#source). This will also install the required
development dependencies and test utilities defined in the `requirements.txt`.

Alternatively, you can find out where spaCy is installed and run `pytest` on
that directory. Don't forget to also install the test utilities via spaCy's
[`requirements.txt`](https://github.com/explosion/spaCy/tree/master/requirements.txt):

```bash
$ python -c "import os; import spacy; print(os.path.dirname(spacy.__file__))"
$ pip install -r path/to/requirements.txt
$ python -m pytest [spacy directory]
```

Calling `pytest` on the spaCy directory will run only the basic tests. The flag
`--slow` is optional and enables additional tests that take longer.

```bash
$ python -m pip install -U pytest               # update pytest
$ python -m pytest [spacy directory]            # basic tests
$ python -m pytest [spacy directory] --slow     # basic and slow tests
```

## Troubleshooting guide {#troubleshooting}

This section collects some of the most common errors you may come across when
installing, loading and using spaCy, as well as their solutions.

> #### Help us improve this guide
>
> Did you come across a problem like the ones listed here and want to share the
> solution? You can find the "Suggest edits" button at the bottom of this page
> that points you to the source. We always appreciate
> [pull requests](https://github.com/explosion/spaCy/pulls)!

<Accordion title="No compatible model found" id="compatible-model">

```
No compatible model found for [lang] (spaCy vX.X.X).
```

This usually means that the model you're trying to download does not exist, or
isn't available for your version of spaCy. Check the
[compatibility table](https://github.com/explosion/spacy-models/tree/master/compatibility.json)
to see which models are available for your spaCy version. If you're using an old
version, consider upgrading to the latest release. Note that while spaCy
supports tokenization for [a variety of languages](/usage/models#languages), not
all of them come with statistical models. To only use the tokenizer, import the
language's `Language` class instead, for example
`from spacy.lang.fr import French`.

</Accordion>

<Accordion title="No such option: --no-cache-dir" id="no-cache-dir">

```
no such option: --no-cache-dir
```

The `download` command uses pip to install the models and sets the
`--no-cache-dir` flag to prevent it from requiring too much memory.
[This setting](https://pip.pypa.io/en/stable/reference/pip_install/#caching)
requires pip v6.0 or newer. Run `pip install -U pip` to upgrade to the latest
version of pip. To see which version you have installed, run `pip --version`.

</Accordion>

<Accordion title="sre_constants.error: bad character range" id="narrow-unicode">

```
sre_constants.error: bad character range
```

In [v2.1](/usage/v2-1), spaCy changed its implementation of regular expressions
for tokenization to make it up to 2-3 times faster. But this also means that
it's very important now that you run spaCy with a wide unicode build of Python.
This means that the build has 1114111 unicode characters available, instead of
only 65535 in a narrow unicode build. You can check this by running the
following command:

```bash
$ python -c "import sys; print(sys.maxunicode)"
```

If you're running a narrow unicode build, reinstall Python and use a wide
unicode build instead. You can also rebuild Python and set the
`--enable-unicode=ucs4` flag.

</Accordion>

<Accordion title="Unknown locale: UTF-8" id="unknown-locale">

```
ValueError: unknown locale: UTF-8
```

This error can sometimes occur on OSX and is likely related to a still
unresolved [Python bug](https://bugs.python.org/issue18378). However, it's easy
to fix: just add the following to your `~/.bash_profile` or `~/.zshrc` and then
run `source ~/.bash_profile` or `source ~/.zshrc`. Make sure to add **both
lines** for `LC_ALL` and `LANG`.

```bash
$ export LC_ALL=en_US.UTF-8
$ export LANG=en_US.UTF-8
```

</Accordion>

<Accordion title="Import error: No module named spacy" id="import-error">

```
Import Error: No module named spacy
```

This error means that the spaCy module can't be located on your system, or in
your environment. Make sure you have spaCy installed. If you're using a virtual
environment, make sure it's activated and check that spaCy is installed in that
environment – otherwise, you're trying to load a system installation. You can
also run `which python` to find out where your Python executable is located.

</Accordion>

<Accordion title="Import error: No module named [model]" id="import-error-models">

```
ImportError: No module named 'en_core_web_sm'
```

As of spaCy v1.7, all models can be installed as Python packages. This means
that they'll become importable modules of your application. If this fails, it's
usually a sign that the package is not installed in the current environment. Run
`pip list` or `pip freeze` to check which model packages you have installed, and
install the [correct models](/models) if necessary. If you're importing a model
manually at the top of a file, make sure to use the name of the package, not the
shortcut link you've created.

</Accordion>

<Accordion title="Command not found: spacy" id="command-not-found">

```
command not found: spacy
```

This error may occur when running the `spacy` command from the command line.
spaCy does not currently add an entry to your `PATH` environment variable, as
this can lead to unexpected results, especially when using a virtual
environment. Instead, spaCy adds an auto-alias that maps `spacy` to
`python -m spacy]`. If this is not working as expected, run the command with
`python -m`, yourself – for example `python -m spacy download en_core_web_sm`.
For more info on this, see the [`download`](/api/cli#download) command.

</Accordion>

<Accordion title="'module' object has no attribute 'load'" id="module-load">

```
AttributeError: 'module' object has no attribute 'load'
```

While this could technically have many causes, including spaCy being broken, the
most likely one is that your script's file or directory name is "shadowing" the
module – e.g. your file is called `spacy.py`, or a directory you're importing
from is called `spacy`. So, when using spaCy, never call anything else `spacy`.

</Accordion>

<Accordion title="NER model doesn't recognize other entities anymore after training" id="catastrophic-forgetting">

If your training data only contained new entities and you didn't mix in any
examples the model previously recognized, it can cause the model to "forget"
what it had previously learned. This is also referred to as the "catastrophic
forgetting problem". A solution is to pre-label some text, and mix it with the
new text in your updates. You can also do this by running spaCy over some text,
extracting a bunch of entities the model previously recognized correctly, and
adding them to your training examples.

</Accordion>

<Accordion title="Unhashable type: 'list'" id="unhashable-list">

```
TypeError: unhashable type: 'list'
```

If you're training models, writing them to disk, and versioning them with git,
you might encounter this error when trying to load them in a Windows
environment. This happens because a default install of Git for Windows is
configured to automatically convert Unix-style end-of-line characters (LF) to
Windows-style ones (CRLF) during file checkout (and the reverse when
committing). While that's mostly fine for text files, a trained model written to
disk has some binary files that should not go through this conversion. When they
do, you get the error above. You can fix it by either changing your
[`core.autocrlf`](https://git-scm.com/book/en/v2/Customizing-Git-Git-Configuration)
setting to `"false"`, or by committing a
[`.gitattributes`](https://git-scm.com/docs/gitattributes) file] to your
repository to tell git on which files or folders it shouldn't do LF-to-CRLF
conversion, with an entry like `path/to/spacy/model/** -text`. After you've done
either of these, clone your repository again.

</Accordion>

## Changelog {#changelog}

import Changelog from 'widgets/changelog.js'

<Changelog />
