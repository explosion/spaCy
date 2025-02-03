<a href="https://explosion.ai"><img src="https://explosion.ai/assets/img/logo.svg" width="125" height="125" align="right" /></a>

# spaCy: Industrial-strength NLP

spaCy is a library for **advanced Natural Language Processing** in Python and
Cython. It's built on the very latest research, and was designed from day one to
be used in real products.

spaCy comes with [pretrained pipelines](https://spacy.io/models) and currently
supports tokenization and training for **70+ languages**. It features
state-of-the-art speed and **neural network models** for tagging, parsing,
**named entity recognition**, **text classification** and more, multi-task
learning with pretrained **transformers** like BERT, as well as a
production-ready [**training system**](https://spacy.io/usage/training) and easy
model packaging, deployment and workflow management. spaCy is commercial
open-source software, released under the
[MIT license](https://github.com/explosion/spaCy/blob/master/LICENSE).

💫 **Version 3.8 out now!**
[Check out the release notes here.](https://github.com/explosion/spaCy/releases)

[![tests](https://github.com/explosion/spaCy/actions/workflows/tests.yml/badge.svg)](https://github.com/explosion/spaCy/actions/workflows/tests.yml)
[![Current Release Version](https://img.shields.io/github/release/explosion/spacy.svg?style=flat-square&logo=github)](https://github.com/explosion/spaCy/releases)
[![pypi Version](https://img.shields.io/pypi/v/spacy.svg?style=flat-square&logo=pypi&logoColor=white)](https://pypi.org/project/spacy/)
[![conda Version](https://img.shields.io/conda/vn/conda-forge/spacy.svg?style=flat-square&logo=conda-forge&logoColor=white)](https://anaconda.org/conda-forge/spacy)
[![Python wheels](https://img.shields.io/badge/wheels-%E2%9C%93-4c1.svg?longCache=true&style=flat-square&logo=python&logoColor=white)](https://github.com/explosion/wheelwright/releases)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg?style=flat-square)](https://github.com/ambv/black)
<br />
[![PyPi downloads](https://static.pepy.tech/personalized-badge/spacy?period=total&units=international_system&left_color=grey&right_color=orange&left_text=pip%20downloads)](https://pypi.org/project/spacy/)
[![Conda downloads](https://img.shields.io/conda/dn/conda-forge/spacy?label=conda%20downloads)](https://anaconda.org/conda-forge/spacy)

## 📖 Documentation

| Documentation                                                                                                                                                                                                             |                                                                                                                                                                                                                                                                                                                                              |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| ⭐️ **[spaCy 101]**                                                                                                                                                                                                       | New to spaCy? Here's everything you need to know!                                                                                                                                                                                                                                                                                            |
| 📚 **[Usage Guides]**                                                                                                                                                                                                     | How to use spaCy and its features.                                                                                                                                                                                                                                                                                                           |
| 🚀 **[New in v3.0]**                                                                                                                                                                                                      | New features, backwards incompatibilities and migration guide.                                                                                                                                                                                                                                                                               |
| 🪐 **[Project Templates]**                                                                                                                                                                                                | End-to-end workflows you can clone, modify and run.                                                                                                                                                                                                                                                                                          |
| 🎛 **[API Reference]**                                                                                                                                                                                                     | The detailed reference for spaCy's API.                                                                                                                                                                                                                                                                                                      |
| ⏩ **[GPU Processing]**                                                                                                                                                                                                    | Use spaCy with CUDA-compatible GPU processing.                                                                                                                                                                                                                                                                                               |
| 📦 **[Models]**                                                                                                                                                                                                           | Download trained pipelines for spaCy.                                                                                                                                                                                                                                                                                                        |
| 🦙 **[Large Language Models]**                                                                                                                                                                                            | Integrate LLMs into spaCy pipelines.                                                                                                                                                                                                                                                                                                        |
| 🌌 **[Universe]**                                                                                                                                                                                                         | Plugins, extensions, demos and books from the spaCy ecosystem.                                                                                                                                                                                                                                                                               |
| ⚙️ **[spaCy VS Code Extension]**                                                                                                                                                                                          | Additional tooling and features for working with spaCy's config files.                                                                                                                                                                                                                                                                       |
| 👩‍🏫 **[Online Course]**                                                                                                                                                                                                    | Learn spaCy in this free and interactive online course.                                                                                                                                                                                                                                                                                      |
| 📰 **[Blog]**                                                                                                                                                                                                             | Read about current spaCy and Prodigy development, releases, talks and more from Explosion.                                                                                                                                                                                                                 |
| 📺 **[Videos]**                                                                                                                                                                                                           | Our YouTube channel with video tutorials, talks and more.                                                                                                                                                                                                                                                                                    |
| 🔴 **[Live Stream]**                                                                                                                                                                                                       | Join Matt as he works on spaCy and chat about NLP, live every week.                                                                                                                                                                                                                                                                         |
| 🛠 **[Changelog]**                                                                                                                                                                                                         | Changes and version history.                                                                                                                                                                                                                                                                                                                 |
| 💝 **[Contribute]**                                                                                                                                                                                                       | How to contribute to the spaCy project and code base.                                                                                                                                                                                                                                                                                        |
| 👕 **[Swag]**                                                                                                                                                                                                             | Support us and our work with unique, custom-designed swag!                                                                                                                                                                                                                                                                                   |
| <a href="https://explosion.ai/tailored-solutions"><img src="https://github.com/explosion/spaCy/assets/13643239/36d2a42e-98c0-4599-90e1-788ef75181be" width="150" alt="Tailored Solutions"/></a> | Custom NLP consulting, implementation and strategic advice by spaCy’s core development team. Streamlined, production-ready, predictable and maintainable. Send us an email or take our 5-minute questionnaire, and well'be in touch! **[Learn more &rarr;](https://explosion.ai/tailored-solutions)**                 |

[spacy 101]: https://spacy.io/usage/spacy-101
[new in v3.0]: https://spacy.io/usage/v3
[usage guides]: https://spacy.io/usage/
[api reference]: https://spacy.io/api/
[gpu processing]: https://spacy.io/usage#gpu
[models]: https://spacy.io/models
[large language models]: https://spacy.io/usage/large-language-models
[universe]: https://spacy.io/universe
[spacy vs code extension]: https://github.com/explosion/spacy-vscode
[videos]: https://www.youtube.com/c/ExplosionAI
[live stream]: https://www.youtube.com/playlist?list=PLBmcuObd5An5_iAxNYLJa_xWmNzsYce8c
[online course]: https://course.spacy.io
[blog]: https://explosion.ai
[project templates]: https://github.com/explosion/projects
[changelog]: https://spacy.io/usage#changelog
[contribute]: https://github.com/explosion/spaCy/blob/master/CONTRIBUTING.md
[swag]: https://explosion.ai/merch

## 💬 Where to ask questions

The spaCy project is maintained by the [spaCy team](https://explosion.ai/about).
Please understand that we won't be able to provide individual support via email.
We also believe that help is much more valuable if it's shared publicly, so that
more people can benefit from it.

| Type                            | Platforms                               |
| ------------------------------- | --------------------------------------- |
| 🚨 **Bug Reports**              | [GitHub Issue Tracker]                  |
| 🎁 **Feature Requests & Ideas** | [GitHub Discussions] · [Live Stream]    |
| 👩‍💻 **Usage Questions**          | [GitHub Discussions] · [Stack Overflow] |
| 🗯 **General Discussion**        | [GitHub Discussions] · [Live Stream]   |

[github issue tracker]: https://github.com/explosion/spaCy/issues
[github discussions]: https://github.com/explosion/spaCy/discussions
[stack overflow]: https://stackoverflow.com/questions/tagged/spacy
[live stream]: https://www.youtube.com/playlist?list=PLBmcuObd5An5_iAxNYLJa_xWmNzsYce8c

## Features

- Support for **70+ languages**
- **Trained pipelines** for different languages and tasks
- Multi-task learning with pretrained **transformers** like BERT
- Support for pretrained **word vectors** and embeddings
- State-of-the-art speed
- Production-ready **training system**
- Linguistically-motivated **tokenization**
- Components for named **entity recognition**, part-of-speech-tagging,
  dependency parsing, sentence segmentation, **text classification**,
  lemmatization, morphological analysis, entity linking and more
- Easily extensible with **custom components** and attributes
- Support for custom models in **PyTorch**, **TensorFlow** and other frameworks
- Built in **visualizers** for syntax and NER
- Easy **model packaging**, deployment and workflow management
- Robust, rigorously evaluated accuracy

📖 **For more details, see the
[facts, figures and benchmarks](https://spacy.io/usage/facts-figures).**

## ⏳ Install spaCy

For detailed installation instructions, see the
[documentation](https://spacy.io/usage).

- **Operating system**: macOS / OS X · Linux · Windows (Cygwin, MinGW, Visual
  Studio)
- **Python version**: Python 3.7+ (only 64 bit)
- **Package managers**: [pip] · [conda] (via `conda-forge`)

[pip]: https://pypi.org/project/spacy/
[conda]: https://anaconda.org/conda-forge/spacy

### pip

Using pip, spaCy releases are available as source packages and binary wheels.
Before you install spaCy and its dependencies, make sure that your `pip`,
`setuptools` and `wheel` are up to date.

```bash
pip install -U pip setuptools wheel
pip install spacy
```

To install additional data tables for lemmatization and normalization you can
run `pip install spacy[lookups]` or install
[`spacy-lookups-data`](https://github.com/explosion/spacy-lookups-data)
separately. The lookups package is needed to create blank models with
lemmatization data, and to lemmatize in languages that don't yet come with
pretrained models and aren't powered by third-party libraries.

When using pip it is generally recommended to install packages in a virtual
environment to avoid modifying system state:

```bash
python -m venv .env
source .env/bin/activate
pip install -U pip setuptools wheel
pip install spacy
```

### conda

You can also install spaCy from `conda` via the `conda-forge` channel. For the
feedstock including the build recipe and configuration, check out
[this repository](https://github.com/conda-forge/spacy-feedstock).

```bash
conda install -c conda-forge spacy
```

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

📖 **For details on upgrading from spaCy 2.x to spaCy 3.x, see the
[migration guide](https://spacy.io/usage/v3#migrating).**

## 📦 Download model packages

Trained pipelines for spaCy can be installed as **Python packages**. This means
that they're a component of your application, just like any other module. Models
can be installed using spaCy's [`download`](https://spacy.io/api/cli#download)
command, or manually by pointing pip to a path or URL.

| Documentation              |                                                                  |
| -------------------------- | ---------------------------------------------------------------- |
| **[Available Pipelines]**  | Detailed pipeline descriptions, accuracy figures and benchmarks. |
| **[Models Documentation]** | Detailed usage and installation instructions.                    |
| **[Training]**             | How to train your own pipelines on your data.                    |

[available pipelines]: https://spacy.io/models
[models documentation]: https://spacy.io/usage/models
[training]: https://spacy.io/usage/training

```bash
# Download best-matching version of specific model for your spaCy installation
python -m spacy download en_core_web_sm

# pip install .tar.gz archive or .whl from path or URL
pip install /Users/you/en_core_web_sm-3.0.0.tar.gz
pip install /Users/you/en_core_web_sm-3.0.0-py3-none-any.whl
pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.0.0/en_core_web_sm-3.0.0.tar.gz
```

### Loading and using models

To load a model, use [`spacy.load()`](https://spacy.io/api/top-level#spacy.load)
with the model name or a path to the model data directory.

```python
import spacy
nlp = spacy.load("en_core_web_sm")
doc = nlp("This is a sentence.")
```

You can also `import` a model directly via its full name and then call its
`load()` method with no arguments.

```python
import spacy
import en_core_web_sm

nlp = en_core_web_sm.load()
doc = nlp("This is a sentence.")
```

📖 **For more info and examples, check out the
[models documentation](https://spacy.io/docs/usage/models).**

## ⚒ Compile from source

The other way to install spaCy is to clone its
[GitHub repository](https://github.com/explosion/spaCy) and build it from
source. That is the common way if you want to make changes to the code base.
You'll need to make sure that you have a development environment consisting of a
Python distribution including header files, a compiler,
[pip](https://pip.pypa.io/en/latest/installing/),
[virtualenv](https://virtualenv.pypa.io/en/latest/) and
[git](https://git-scm.com) installed. The compiler part is the trickiest. How to
do that depends on your system.

| Platform    |                                                                                                                                                                                                                                                                     |
| ----------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Ubuntu**  | Install system-level dependencies via `apt-get`: `sudo apt-get install build-essential python-dev git` .                                                                                                                                                            |
| **Mac**     | Install a recent version of [XCode](https://developer.apple.com/xcode/), including the so-called "Command Line Tools". macOS and OS X ship with Python and git preinstalled.                                                                                        |
| **Windows** | Install a version of the [Visual C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/) or [Visual Studio Express](https://visualstudio.microsoft.com/vs/express/) that matches the version that was used to compile your Python interpreter. |

For more details and instructions, see the documentation on
[compiling spaCy from source](https://spacy.io/usage#source) and the
[quickstart widget](https://spacy.io/usage#section-quickstart) to get the right
commands for your platform and Python version.

```bash
git clone https://github.com/explosion/spaCy
cd spaCy

python -m venv .env
source .env/bin/activate

# make sure you are using the latest pip
python -m pip install -U pip setuptools wheel

pip install -r requirements.txt
pip install --no-build-isolation --editable .
```

To install with extras:

```bash
pip install --no-build-isolation --editable .[lookups,cuda102]
```

## 🚦 Run tests

spaCy comes with an [extensive test suite](spacy/tests). In order to run the
tests, you'll usually want to clone the repository and build spaCy from source.
This will also install the required development dependencies and test utilities
defined in the [`requirements.txt`](requirements.txt).

Alternatively, you can run `pytest` on the tests from within the installed
`spacy` package. Don't forget to also install the test utilities via spaCy's
[`requirements.txt`](requirements.txt):

```bash
pip install -r requirements.txt
python -m pytest --pyargs spacy
```
