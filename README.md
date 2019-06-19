<a href="https://explosion.ai"><img src="https://explosion.ai/assets/img/logo.svg" width="125" height="125" align="right" /></a>

# spaCy: Industrial-strength NLP

spaCy is a library for advanced Natural Language Processing in Python and
Cython. It's built on the very latest research, and was designed from day one
to be used in real products. spaCy comes with
[pre-trained statistical models](https://spacy.io/models) and word vectors, and
currently supports tokenization for **49+ languages**. It features
state-of-the-art speed, convolutional **neural network models** for tagging,
parsing and **named entity recognition** and easy **deep learning** integration.
It's commercial open-source software, released under the MIT license.

💫 **Version 2.1 out now!** [Check out the release notes here.](https://github.com/explosion/spaCy/releases)

[![Azure Pipelines](https://img.shields.io/azure-devops/build/explosion-ai/public/8/master.svg?logo=azure-devops&style=flat-square)](https://dev.azure.com/explosion-ai/public/_build?definitionId=8)
[![Travis Build Status](https://img.shields.io/travis/explosion/spaCy/master.svg?style=flat-square&logo=travis)](https://travis-ci.org/explosion/spaCy)
[![Current Release Version](https://img.shields.io/github/release/explosion/spacy.svg?style=flat-square)](https://github.com/explosion/spaCy/releases)
[![pypi Version](https://img.shields.io/pypi/v/spacy.svg?style=flat-square)](https://pypi.org/project/spacy/)
[![conda Version](https://img.shields.io/conda/vn/conda-forge/spacy.svg?style=flat-square)](https://anaconda.org/conda-forge/spacy)
[![Python wheels](https://img.shields.io/badge/wheels-%E2%9C%93-4c1.svg?longCache=true&style=flat-square&logo=python&logoColor=white)](https://github.com/explosion/wheelwright/releases)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg?style=flat-square)](https://github.com/ambv/black)
[![spaCy on Twitter](https://img.shields.io/twitter/follow/spacy_io.svg?style=social&label=Follow)](https://twitter.com/spacy_io)

## 📖 Documentation

| Documentation   |                                                                |
| --------------- | -------------------------------------------------------------- |
| [spaCy 101]     | New to spaCy? Here's everything you need to know!              |
| [Usage Guides]  | How to use spaCy and its features.                             |
| [New in v2.1]   | New features, backwards incompatibilities and migration guide. |
| [API Reference] | The detailed reference for spaCy's API.                        |
| [Models]        | Download statistical language models for spaCy.                |
| [Universe]      | Libraries, extensions, demos, books and courses.               |
| [Changelog]     | Changes and version history.                                   |
| [Contribute]    | How to contribute to the spaCy project and code base.          |

[spacy 101]: https://spacy.io/usage/spacy-101
[new in v2.1]: https://spacy.io/usage/v2-1
[usage guides]: https://spacy.io/usage/
[api reference]: https://spacy.io/api/
[models]: https://spacy.io/models
[universe]: https://spacy.io/universe
[changelog]: https://spacy.io/usage#changelog
[contribute]: https://github.com/explosion/spaCy/blob/master/CONTRIBUTING.md

## 💬 Where to ask questions

The spaCy project is maintained by [@honnibal](https://github.com/honnibal)
and [@ines](https://github.com/ines). Please understand that we won't be able
to provide individual support via email. We also believe that help is much more
valuable if it's shared publicly, so that more people can benefit from it.

| Type                     | Platforms                                              |
| ------------------------ | ------------------------------------------------------ |
| 🚨 **Bug Reports**       | [GitHub Issue Tracker]                                 |
| 🎁 **Feature Requests**  | [GitHub Issue Tracker]                                 |
| 👩‍💻 **Usage Questions**   | [Stack Overflow] · [Gitter Chat] · [Reddit User Group] |
| 🗯 **General Discussion** | [Gitter Chat] · [Reddit User Group]                    |

[github issue tracker]: https://github.com/explosion/spaCy/issues
[stack overflow]: https://stackoverflow.com/questions/tagged/spacy
[gitter chat]: https://gitter.im/explosion/spaCy
[reddit user group]: https://www.reddit.com/r/spacynlp

## Features

-   Non-destructive **tokenization**
-   **Named entity** recognition
-   Support for **49+ languages**
-   Pre-trained [statistical models](https://spacy.io/models) and word vectors
-   State-of-the-art speed
-   Easy **deep learning** integration
-   Part-of-speech tagging
-   Labelled dependency parsing
-   Syntax-driven sentence segmentation
-   Built in **visualizers** for syntax and NER
-   Convenient string-to-hash mapping
-   Export to numpy data arrays
-   Efficient binary serialization
-   Easy **model packaging** and deployment
-   Robust, rigorously evaluated accuracy

📖 **For more details, see the
[facts, figures and benchmarks](https://spacy.io/usage/facts-figures).**

## Install spaCy

For detailed installation instructions, see the
[documentation](https://spacy.io/usage).

-   **Operating system**: macOS / OS X · Linux · Windows (Cygwin, MinGW, Visual Studio)
-   **Python version**: Python 2.7, 3.5+ (only 64 bit)
-   **Package managers**: [pip] · [conda] (via `conda-forge`)

[pip]: https://pypi.org/project/spacy/
[conda]: https://anaconda.org/conda-forge/spacy

### pip

Using pip, spaCy releases are available as source packages and binary wheels
(as of `v2.0.13`).

```bash
pip install spacy
```

When using pip it is generally recommended to install packages in a virtual
environment to avoid modifying system state:

```bash
python -m venv .env
source .env/bin/activate
pip install spacy
```

### conda

Thanks to our great community, we've finally re-added conda support. You can now
install spaCy via `conda-forge`:

```bash
conda config --add channels conda-forge
conda install spacy
```

For the feedstock including the build recipe and configuration,
check out [this repository](https://github.com/conda-forge/spacy-feedstock).
Improvements and pull requests to the recipe and setup are always appreciated.

### Updating spaCy

Some updates to spaCy may require downloading new statistical models. If you're
running spaCy v2.0 or higher, you can use the `validate` command to check if
your installed models are compatible and if not, print details on how to update
them:

```bash
pip install -U spacy
python -m spacy validate
```

If you've trained your own models, keep in mind that your training and runtime
inputs must match. After updating spaCy, we recommend **retraining your models**
with the new version.

📖 **For details on upgrading from spaCy 1.x to spaCy 2.x, see the
[migration guide](https://spacy.io/usage/v2#migrating).**

## Download models

As of v1.7.0, models for spaCy can be installed as **Python packages**.
This means that they're a component of your application, just like any
other module. Models can be installed using spaCy's `download` command,
or manually by pointing pip to a path or URL.

| Documentation          |                                                               |
| ---------------------- | ------------------------------------------------------------- |
| [Available Models]     | Detailed model descriptions, accuracy figures and benchmarks. |
| [Models Documentation] | Detailed usage instructions.                                  |

[available models]: https://spacy.io/models
[models documentation]: https://spacy.io/docs/usage/models

```bash
# download best-matching version of specific model for your spaCy installation
python -m spacy download en_core_web_sm

# out-of-the-box: download best-matching default model
python -m spacy download en

# pip install .tar.gz archive from path or URL
pip install /Users/you/en_core_web_sm-2.1.0.tar.gz
pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-2.1.0/en_core_web_sm-2.1.0.tar.gz
```

### Loading and using models

To load a model, use `spacy.load()` with the model name, a shortcut link or a
path to the model data directory.

```python
import spacy
nlp = spacy.load("en_core_web_sm")
doc = nlp(u"This is a sentence.")
```

You can also `import` a model directly via its full name and then call its
`load()` method with no arguments.

```python
import spacy
import en_core_web_sm

nlp = en_core_web_sm.load()
doc = nlp(u"This is a sentence.")
```

📖 **For more info and examples, check out the
[models documentation](https://spacy.io/docs/usage/models).**

### Support for older versions

If you're using an older version (`v1.6.0` or below), you can still download
and install the old models from within spaCy using `python -m spacy.en.download all`
or `python -m spacy.de.download all`. The `.tar.gz` archives are also
[attached to the v1.6.0 release](https://github.com/explosion/spaCy/tree/v1.6.0).
To download and install the models manually, unpack the archive, drop the
contained directory into `spacy/data` and load the model via `spacy.load('en')`
or `spacy.load('de')`.

## Compile from source

The other way to install spaCy is to clone its
[GitHub repository](https://github.com/explosion/spaCy) and build it from
source. That is the common way if you want to make changes to the code base.
You'll need to make sure that you have a development environment consisting of a
Python distribution including header files, a compiler,
[pip](https://pip.pypa.io/en/latest/installing/),
[virtualenv](https://virtualenv.pypa.io/en/latest/) and [git](https://git-scm.com)
installed. The compiler part is the trickiest. How to do that depends on your
system. See notes on Ubuntu, OS X and Windows for details.

```bash
# make sure you are using the latest pip
python -m pip install -U pip
git clone https://github.com/explosion/spaCy
cd spaCy

python -m venv .env
source .env/bin/activate
export PYTHONPATH=`pwd`
pip install -r requirements.txt
python setup.py build_ext --inplace
```

Compared to regular install via pip, [requirements.txt](requirements.txt)
additionally installs developer dependencies such as Cython. For more details
and instructions, see the documentation on
[compiling spaCy from source](https://spacy.io/usage#source) and the
[quickstart widget](https://spacy.io/usage#section-quickstart) to get
the right commands for your platform and Python version.

### Ubuntu

Install system-level dependencies via `apt-get`:

```bash
sudo apt-get install build-essential python-dev git
```

### macOS / OS X

Install a recent version of [XCode](https://developer.apple.com/xcode/),
including the so-called "Command Line Tools". macOS and OS X ship with Python
and git preinstalled.

### Windows

Install a version of the [Visual C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/) or
[Visual Studio Express](https://visualstudio.microsoft.com/vs/express/)
that matches the version that was used to compile your Python
interpreter. For official distributions these are VS 2008 (Python 2.7),
VS 2010 (Python 3.4) and VS 2015 (Python 3.5).

## Run tests

spaCy comes with an [extensive test suite](spacy/tests). In order to run the
tests, you'll usually want to clone the repository and build spaCy from source.
This will also install the required development dependencies and test utilities
defined in the `requirements.txt`.

Alternatively, you can find out where spaCy is installed and run `pytest` on
that directory. Don't forget to also install the test utilities via spaCy's
`requirements.txt`:

```bash
python -c "import os; import spacy; print(os.path.dirname(spacy.__file__))"
pip install -r path/to/requirements.txt
python -m pytest <spacy-directory>
```

See [the documentation](https://spacy.io/usage#tests) for more details and
examples.
