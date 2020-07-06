---
title: Projects
new: 3
menu:
  - ['Intro & Workflow', 'intro']
  - ['Directory & Assets', 'directory']
  - ['Custom Projects', 'custom']
---

> #### Project templates
>
> Our [`projects`](https://github.com/explosion/projects) repo includes various
> project templates for different tasks and models that you can clone and run.

<!-- TODO: write more about templates in aside -->

spaCy projects let you manage and share **end-to-end spaCy workflows** for
training, packaging and serving your custom models. You can start off by cloning
a pre-defined project template, adjust it to fit your needs, load in your data,
train a model, export it as a Python package and share the project templates
with your team. Under the hood, project use
[Data Version Control](https://dvc.org) (DVC) to track and version inputs and
outputs, and make sure you're only re-running what's needed. spaCy projects can
be used via the new [`spacy project`](/api/cli#project) command. For an overview
of the available project templates, check out the
[`projects`](https://github.com/explosion/projects) repo.

## Introduction and workflow {#intro}

<!-- TODO: decide how to introduce concept -->

<Project id="some_example_project">

Lorem ipsum dolor sit amet, consectetur adipiscing elit. Phasellus interdum
sodales lectus, ut sodales orci ullamcorper id. Sed condimentum neque ut erat
mattis pretium.

</Project>

### 1. Clone a project template {#clone}

The [`spacy project clone`](/api/cli#project-clone) command clones an existing
project template and copies the files to a local directory. You can then run the
project, e.g. to train a model and edit the commands and scripts to build fully
custom workflows.

> #### Cloning under the hood
>
> To clone a project, spaCy calls into `git` and uses the "sparse checkout"
> feature to only clone the relevant directory or directories.

```bash
$ python -m spacy clone some_example_project
```

By default, the project will be cloned into the current working directory. You
can specify an optional second argument to define the output directory. The
`--repo` option lets you define a custom repo to clone from, if you don't want
to use the spaCy [`projects`](https://github.com/explosion/projects) repo. You
can also use any private repo you have access to with Git.

If you plan on making the project a Git repo, you can set the `--git` flag to
set it up automatically _before_ initializing DVC, so DVC can integrate with
Git. This means that it will automatically add asset files to a `.gitignore` (so
you never check assets into the repo, only the asset meta files).

### 2. Fetch the project assets {#assets}

Assets are data files your project needs – for example, the training and
evaluation data or pretrained vectors and embeddings to initialize your model
with. <!-- TODO: ... -->

```bash
cd some_example_project
python -m spacy project assets
```

### 3. Run the steps {#run-all}

```bash
$ python -m spacy project run-all
```

### 4. Run single commands {#run}

```bash
$ python -m spacy project run visualize
```

## Project directory and assets {#directory}

### project.yml {#project-yml}

The project config, `project.yml`, defines the assets a project depends on, like
datasets and pretrained weights, as well as a series of commands that can be run
separately or as a pipeline – for instance, to preprocess the data, convert it
to spaCy's format, train a model, evaluate it and export metrics, package it and
spin up a quick web demo. It looks pretty similar to a config file used to
define CI pipelines.

<!-- TODO: include example etc. -->

### Files and directory structure {#project-files}

A project directory created by [`spacy project clone`](/api/cli#project-clone)
includes the following files and directories. They can optionally be
pre-populated by a project template (most commonly used for metas, configs or
scripts).

```yaml
### Project directory
├── project.yml          # the project configuration
├── dvc.yaml             # auto-generated Data Version Control config
├── dvc.lock             # auto-generated Data Version control lock file
├── assets/              # downloaded data assets and DVC meta files
├── metrics/             # output directory for evaluation metrics
├── training/            # output directory for trained models
├── corpus/              # output directory for training corpus
├── packages/            # output directory for model Python packages
├── metrics/             # output directory for evaluation metrics
├── notebooks/           # directory for Jupyter notebooks
├── scripts/             # directory for scripts, e.g. referenced in commands
├── metas/               # model meta.json templates used for packaging
├── configs/             # model config.cfg files used for training
└── ...                  # any other files, like a requirements.txt etc.
```

When the project is initialized, spaCy will auto-generate a `dvc.yaml` based on
the project config. The file is updated whenever the project config has changed
and includes all commands defined in the `run` section of the project config.
This allows DVC to track the inputs and outputs and know which steps need to be
re-run.

#### Why Data Version Control (DVC)?

Data assets like training corpora or pretrained weights are at the core of any
NLP project, but they're often difficult to manage: you can't just check them
into your Git repo to version and keep track of them. And if you have multiple
steps that depend on each other, like a preprocessing step that generates your
training data, you need to make sure the data is always up-to-date, and re-run
all steps of your process every time, just to be safe.

[Data Version Control (DVC)](https://dvc.org) is a standalone open-source tool
that integrates into your workflow like Git, builds a dependency graph for your
data pipelines and tracks and caches your data files. If you're downloading data
from an external source, like a storage bucket, DVC can tell whether the
resource has changed. It can also determine whether to re-run a step, depending
on whether its input have changed or not. All metadata can be checked into a Git
repo, so you'll always be able to reproduce your experiments. `spacy project`
uses DVC under the hood and you typically don't have to think about it if you
don't want to. But if you do want to integrate with DVC more deeply, you can.
Each spaCy project is also a regular DVC project.

#### Checking projects into Git

---

## Custom projects and scripts {#custom}
