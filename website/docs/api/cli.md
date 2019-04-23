---
title: Command Line Interface
teaser: Download, train and package models, and debug spaCy
source: spacy/cli
menu:
  - ['Download', 'download']
  - ['Link', 'link']
  - ['Info', 'info']
  - ['Validate', 'validate']
  - ['Convert', 'convert']
  - ['Train', 'train']
  - ['Pretrain', 'pretrain']
  - ['Init Model', 'init-model']
  - ['Evaluate', 'evaluate']
  - ['Package', 'package']
---

As of v1.7.0, spaCy comes with new command line helpers to download and link
models and show useful debugging information. For a list of available commands,
type `spacy --help`.

## Download {#download}

Download [models](/usage/models) for spaCy. The downloader finds the
best-matching compatible version, uses pip to download the model as a package
and automatically creates a [shortcut link](/usage/models#usage) to load the
model by name. Direct downloads don't perform any compatibility checks and
require the model name to be specified with its version (e.g.
`en_core_web_sm-2.0.0`).

> #### Downloading best practices
>
> The `download` command is mostly intended as a convenient, interactive wrapper
> – it performs compatibility checks and prints detailed messages in case things
> go wrong. It's **not recommended** to use this command as part of an automated
> process. If you know which model your project needs, you should consider a
> [direct download via pip](/usage/models#download-pip), or uploading the model
> to a local PyPi installation and fetching it straight from there. This will
> also allow you to add it as a versioned package dependency to your project.

```bash
$ python -m spacy download [model] [--direct]
```

| Argument                           | Type               | Description                                                                                                                                                   |
| ---------------------------------- | ------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `model`                            | positional         | Model name or shortcut (`en`, `de`, `en_core_web_sm`).                                                                                                        |
| `--direct`, `-d`                   | flag               | Force direct download of exact model version.                                                                                                                 |
| other <Tag variant="new">2.1</Tag> | -                  | Additional installation options to be passed to `pip install` when installing the model package. For example, `--user` to install to the user home directory. |
| `--help`, `-h`                     | flag               | Show help message and available arguments.                                                                                                                    |
| **CREATES**                        | directory, symlink | The installed model package in your `site-packages` directory and a shortcut link as a symlink in `spacy/data`.                                               |

## Link {#link}

Create a [shortcut link](/usage/models#usage) for a model, either a Python
package or a local directory. This will let you load models from any location
using a custom name via [`spacy.load()`](/api/top-level#spacy.load).

<Infobox title="Important note" variant="warning">

In spaCy v1.x, you had to use the model data directory to set up a shortcut link
for a local path. As of v2.0, spaCy expects all shortcut links to be **loadable
model packages**. If you want to load a data directory, call
[`spacy.load()`](/api/top-level#spacy.load) or
[`Language.from_disk()`](/api/language#from_disk) with the path, or use the
[`package`](/api/cli#package) command to create a model package.

</Infobox>

```bash
$ python -m spacy link [origin] [link_name] [--force]
```

| Argument        | Type       | Description                                                     |
| --------------- | ---------- | --------------------------------------------------------------- |
| `origin`        | positional | Model name if package, or path to local directory.              |
| `link_name`     | positional | Name of the shortcut link to create.                            |
| `--force`, `-f` | flag       | Force overwriting of existing link.                             |
| `--help`, `-h`  | flag       | Show help message and available arguments.                      |
| **CREATES**     | symlink    | A shortcut link of the given name as a symlink in `spacy/data`. |

## Info {#info}

Print information about your spaCy installation, models and local setup, and
generate [Markdown](https://en.wikipedia.org/wiki/Markdown)-formatted markup to
copy-paste into [GitHub issues](https://github.com/explosion/spaCy/issues).

```bash
$ python -m spacy info [--markdown]
```

```bash
$ python -m spacy info [model] [--markdown]
```

| Argument                                         | Type       | Description                                                   |
| ------------------------------------------------ | ---------- | ------------------------------------------------------------- |
| `model`                                          | positional | A model, i.e. shortcut link, package name or path (optional). |
| `--markdown`, `-md`                              | flag       | Print information as Markdown.                                |
| `--silent`, `-s` <Tag variant="new">2.0.12</Tag> | flag       | Don't print anything, just return the values.                 |
| `--help`, `-h`                                   | flag       | Show help message and available arguments.                    |
| **PRINTS**                                       | `stdout`   | Information about your spaCy installation.                    |

## Validate {#validate new="2"}

Find all models installed in the current environment (both packages and shortcut
links) and check whether they are compatible with the currently installed
version of spaCy. Should be run after upgrading spaCy via `pip install -U spacy`
to ensure that all installed models are can be used with the new version. The
command is also useful to detect out-of-sync model links resulting from links
created in different virtual environments. It will a list of models, the
installed versions, the latest compatible version (if out of date) and the
commands for updating.

> #### Automated validation
>
> You can also use the `validate` command as part of your build process or test
> suite, to ensure all models are up to date before proceeding. If incompatible
> models or shortcut links are found, it will return `1`.

```bash
$ python -m spacy validate
```

| Argument   | Type     | Description                                               |
| ---------- | -------- | --------------------------------------------------------- |
| **PRINTS** | `stdout` | Details about the compatibility of your installed models. |

## Convert {#convert}

Convert files into spaCy's [JSON format](/api/annotation#json-input) for use
with the `train` command and other experiment management functions. The
converter can be specified on the command line, or chosen based on the file
extension of the input file.

```bash
$ python -m spacy convert [input_file] [output_dir] [--file-type] [--converter]
[--n-sents] [--morphology] [--lang]
```

| Argument                                         | Type       | Description                                                                                       |
| ------------------------------------------------ | ---------- | ------------------------------------------------------------------------------------------------- |
| `input_file`                                     | positional | Input file.                                                                                       |
| `output_dir`                                     | positional | Output directory for converted file. Defaults to `"-"`, meaning data will be written to `stdout`. |
| `--file-type`, `-t` <Tag variant="new">2.1</Tag> | option     | Type of file to create (see below).                                                               |
| `--converter`, `-c` <Tag variant="new">2</Tag>   | option     | Name of converter to use (see below).                                                             |
| `--n-sents`, `-n`                                | option     | Number of sentences per document.                                                                 |
| `--morphology`, `-m`                             | option     | Enable appending morphology to tags.                                                              |
| `--lang`, `-l` <Tag variant="new">2.1</Tag>      | option     | Language code (if tokenizer required).                                                            |
| `--help`, `-h`                                   | flag       | Show help message and available arguments.                                                        |
| **CREATES**                                      | JSON       | Data in spaCy's [JSON format](/api/annotation#json-input).                                        |

### Output file types {new="2.1"}

> #### Which format should I choose?
>
> If you're not sure, go with the default `jsonl`. Newline-delimited JSON means
> that there's one JSON object per line. Unlike a regular JSON file, it can also
> be read in line-by-line and you won't have to parse the _entire file_ first.
> This makes it a very convenient format for larger corpora.

All output files generated by this command are compatible with
[`spacy train`](/api/cli#train).

| ID      | Description                       |
| ------- | --------------------------------- |
| `jsonl` | Newline-delimited JSON (default). |
| `json`  | Regular JSON.                     |
| `msg`   | Binary MessagePack format.        |

### Converter options

<!-- TODO: document jsonl option – maybe update it? -->

| ID                             | Description                                                     |
| ------------------------------ | --------------------------------------------------------------- |
| `auto`                         | Automatically pick converter based on file extension (default). |
| `conll`, `conllu`, `conllubio` | Universal Dependencies `.conllu` or `.conll` format.            |
| `ner`                          | Tab-based named entity recognition format.                      |
| `iob`                          | IOB or IOB2 named entity recognition format.                    |

## Train {#train}

Train a model. Expects data in spaCy's
[JSON format](/api/annotation#json-input). On each epoch, a model will be saved
out to the directory. Accuracy scores and model details will be added to a
[`meta.json`](/usage/training#models-generating) to allow packaging the model
using the [`package`](/api/cli#package) command.

<Infobox title="Changed in v2.1" variant="warning">

As of spaCy 2.1, the `--no-tagger`, `--no-parser` and `--no-entities` flags have
been replaced by a `--pipeline` option, which lets you define comma-separated
names of pipeline components to train. For example, `--pipeline tagger,parser`
will only train the tagger and parser.

</Infobox>

```bash
$ python -m spacy train [lang] [output_path] [train_path] [dev_path]
[--base-model] [--pipeline] [--vectors] [--n-iter] [--n-early-stopping] [--n-examples] [--use-gpu]
[--version] [--meta-path] [--init-tok2vec] [--parser-multitasks]
[--entity-multitasks] [--gold-preproc] [--noise-level] [--learn-tokens]
[--verbose]
```

| Argument                                              | Type          | Description                                                                                                                                                       |
| ----------------------------------------------------- | ------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `lang`                                                | positional    | Model language.                                                                                                                                                   |
| `output_path`                                         | positional    | Directory to store model in. Will be created if it doesn't exist.                                                                                                 |
| `train_path`                                          | positional    | Location of JSON-formatted training data. Can be a file or a directory of files.                                                                                  |
| `dev_path`                                            | positional    | Location of JSON-formatted development data for evaluation. Can be a file or a directory of files.                                                                |
| `--base-model`, `-b`                                  | option        | Optional name of base model to update. Can be any loadable spaCy model.                                                                                           |
| `--pipeline`, `-p` <Tag variant="new">2.1</Tag>       | option        | Comma-separated names of pipeline components to train. Defaults to `'tagger,parser,ner'`.                                                                         |
| `--vectors`, `-v`                                     | option        | Model to load vectors from.                                                                                                                                       |
| `--n-iter`, `-n`                                      | option        | Number of iterations (default: `30`).                                                                                                                             |
| `--n-early-stopping`, `-ne`                           | option        | Maximum number of training epochs without dev accuracy improvement.                                                                                               |
| `--n-examples`, `-ns`                                 | option        | Number of examples to use (defaults to `0` for all examples).                                                                                                     |
| `--use-gpu`, `-g`                                     | option        | Whether to use GPU. Can be either `0`, `1` or `-1`.                                                                                                               |
| `--version`, `-V`                                     | option        | Model version. Will be written out to the model's `meta.json` after training.                                                                                     |
| `--meta-path`, `-m` <Tag variant="new">2</Tag>        | option        | Optional path to model [`meta.json`](/usage/training#models-generating). All relevant properties like `lang`, `pipeline` and `spacy_version` will be overwritten. |
| `--init-tok2vec`, `-t2v` <Tag variant="new">2.1</Tag> | option        | Path to pretrained weights for the token-to-vector parts of the models. See `spacy pretrain`. Experimental.                                                       |
| `--parser-multitasks`, `-pt`                          | option        | Side objectives for parser CNN, e.g. `'dep'` or `'dep,tag'`                                                                                                       |
| `--entity-multitasks`, `-et`                          | option        | Side objectives for NER CNN, e.g. `'dep'` or `'dep,tag'`                                                                                                          |
| `--noise-level`, `-nl`                                | option        | Float indicating the amount of corruption for data augmentation.                                                                                                  |
| `--gold-preproc`, `-G`                                | flag          | Use gold preprocessing.                                                                                                                                           |
| `--learn-tokens`, `-T`                                | flag          | Make parser learn gold-standard tokenization by merging ] subtokens. Typically used for languages like Chinese.                                                   |
| `--verbose`, `-VV` <Tag variant="new">2.0.13</Tag>    | flag          | Show more detailed messages during training.                                                                                                                      |
| `--help`, `-h`                                        | flag          | Show help message and available arguments.                                                                                                                        |
| **CREATES**                                           | model, pickle | A spaCy model on each epoch.                                                                                                                                      |

### Environment variables for hyperparameters {#train-hyperparams new="2"}

spaCy lets you set hyperparameters for training via environment variables. For
example:

```bash
$ token_vector_width=256 learn_rate=0.0001 spacy train [...]
```

> #### Usage with alias
>
> Environment variables keep the command simple and allow you to to
> [create an alias](https://askubuntu.com/questions/17536/how-do-i-create-a-permanent-bash-alias/17537#17537)
> for your custom `train` command while still being able to easily tweak the
> hyperparameters.
>
> ```bash
> alias train-parser="python -m spacy train en /output /data /train /dev -n 1000"
> token_vector_width=256 train-parser
> ```

| Name                 | Description                                         | Default |
| -------------------- | --------------------------------------------------- | ------- |
| `dropout_from`       | Initial dropout rate.                               | `0.2`   |
| `dropout_to`         | Final dropout rate.                                 | `0.2`   |
| `dropout_decay`      | Rate of dropout change.                             | `0.0`   |
| `batch_from`         | Initial batch size.                                 | `1`     |
| `batch_to`           | Final batch size.                                   | `64`    |
| `batch_compound`     | Rate of batch size acceleration.                    | `1.001` |
| `token_vector_width` | Width of embedding tables and convolutional layers. | `128`   |
| `embed_size`         | Number of rows in embedding tables.                 | `7500`  |
| `hidden_width`       | Size of the parser's and NER's hidden layers.       | `128`   |
| `learn_rate`         | Learning rate.                                      | `0.001` |
| `optimizer_B1`       | Momentum for the Adam solver.                       | `0.9`   |
| `optimizer_B2`       | Adagrad-momentum for the Adam solver.               | `0.999` |
| `optimizer_eps`      | Epsilon value for the Adam solver.                  | `1e-08` |
| `L2_penalty`         | L2 regularization penalty.                          | `1e-06` |
| `grad_norm_clip`     | Gradient L2 norm constraint.                        | `1.0`   |

## Pretrain {#pretrain new="2.1" tag="experimental"}

Pre-train the "token to vector" (`tok2vec`) layer of pipeline components, using
an approximate language-modeling objective. Specifically, we load pre-trained
vectors, and train a component like a CNN, BiLSTM, etc to predict vectors which
match the pre-trained ones. The weights are saved to a directory after each
epoch. You can then pass a path to one of these pre-trained weights files to the
`spacy train` command.

This technique may be especially helpful if you have little labelled data.
However, it's still quite experimental, so your mileage may vary. To load the
weights back in during `spacy train`, you need to ensure all settings are the
same between pretraining and training. The API and errors around this need some
improvement.

```bash
$ python -m spacy pretrain [texts_loc] [vectors_model] [output_dir] [--width]
[--depth] [--embed-rows] [--dropout] [--seed] [--n-iter] [--use-vectors]
[--n-save_every]
```

| Argument                | Type       | Description                                                                                                                       |
| ----------------------- | ---------- | --------------------------------------------------------------------------------------------------------------------------------- |
| `texts_loc`             | positional | Path to JSONL file with raw texts to learn from, with text provided as the key `"text"`. [See here](#pretrain-jsonl) for details. |
| `vectors_model`         | positional | Name or path to spaCy model with vectors to learn from.                                                                           |
| `output_dir`            | positional | Directory to write models to on each epoch.                                                                                       |
| `--width`, `-cw`        | option     | Width of CNN layers.                                                                                                              |
| `--depth`, `-cd`        | option     | Depth of CNN layers.                                                                                                              |
| `--embed-rows`, `-er`   | option     | Number of embedding rows.                                                                                                         |
| `--dropout`, `-d`       | option     | Dropout rate.                                                                                                                     |
| `--batch-size`, `-bs`   | option     | Number of words per training batch.                                                                                               |
| `--max-length`, `-xw`   | option     | Maximum words per example. Longer examples are discarded.                                                                         |
| `--min-length`, `-nw`   | option     | Minimum words per example. Shorter examples are discarded.                                                                        |
| `--seed`, `-s`          | option     | Seed for random number generators.                                                                                                |
| `--n-iter`, `-i`        | option     | Number of iterations to pretrain.                                                                                                 |
| `--use-vectors`, `-uv`  | flag       | Whether to use the static vectors as input features.                                                                              |
| `--n-save_every`, `-se` | option     | Save model every X batches.                                                                                                       |
| **CREATES**             | weights    | The pre-trained weights that can be used to initialize `spacy train`.                                                             |

### JSONL format for raw text {#pretrain-jsonl}

Raw text can be provided as a `.jsonl` (newline-delimited JSON) file containing
one input text per line (roughly paragraph length is good). Optionally, custom
tokenization can be provided.

> #### Tip: Writing JSONL
>
> Our utility library [`srsly`](https://github.com/explosion/srsly) provides a
> handy `write_jsonl` helper that takes a file path and list of dictionaries and
> writes out JSONL-formatted data.
>
> ```python
> import srsly
> data = [{"text": "Some text"}, {"text": "More..."}]
> srsly.write_jsonl("/path/to/text.jsonl", data)
> ```

| Key      | Type    | Description                                  |
| -------- | ------- | -------------------------------------------- |
| `text`   | unicode | The raw input text.                          |
| `tokens` | list    | Optional tokenization, one string per token. |

```json
### Example
{"text": "Can I ask where you work now and what you do, and if you enjoy it?"}
{"text": "They may just pull out of the Seattle market completely, at least until they have autonomous vehicles."}
{"text": "My cynical view on this is that it will never be free to the public. Reason: what would be the draw of joining the military? Right now their selling point is free Healthcare and Education. Ironically both are run horribly and most, that I've talked to, come out wishing they never went in."}
```

## Init Model {#init-model new="2"}

Create a new model directory from raw data, like word frequencies, Brown
clusters and word vectors. This command is similar to the `spacy model` command
in v1.x.

<Infobox title="Deprecation note" variant="warning">

As of v2.1.0, the `--freqs-loc` and `--clusters-loc` are deprecated and have
been replaced with the `--jsonl-loc` argument, which lets you pass in a a
[newline-delimited JSON](http://jsonlines.org/) (JSONL) file containing one
lexical entry per line. For more details on the format, see the
[annotation specs](/api/annotation#vocab-jsonl).

</Infobox>

```bash
$ python -m spacy init-model [lang] [output_dir] [--jsonl-loc] [--vectors-loc]
[--prune-vectors]
```

| Argument                | Type       | Description                                                                                                                                                                                                                                                       |
| ----------------------- | ---------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `lang`                  | positional | Model language [ISO code](https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes), e.g. `en`.                                                                                                                                                                      |
| `output_dir`            | positional | Model output directory. Will be created if it doesn't exist.                                                                                                                                                                                                      |
| `--jsonl-loc`, `-j`     | option     | Optional location of JSONL-formatted vocabulary file with lexical attributes.                                                                                                                                                                                     |
| `--vectors-loc`, `-v`   | option     | Optional location of vectors file. Should be a tab-separated file in Word2Vec format where the first column contains the word and the remaining columns the values. File can be provided in `.txt` format or as a zipped text file in `.zip` or `.tar.gz` format. |
| `--prune-vectors`, `-V` | flag       | Number of vectors to prune the vocabulary to. Defaults to `-1` for no pruning.                                                                                                                                                                                    |
| **CREATES**             | model      | A spaCy model containing the vocab and vectors.                                                                                                                                                                                                                   |

## Evaluate {#evaluate new="2"}

Evaluate a model's accuracy and speed on JSON-formatted annotated data. Will
print the results and optionally export
[displaCy visualizations](/usage/visualizers) of a sample set of parses to
`.html` files. Visualizations for the dependency parse and NER will be exported
as separate files if the respective component is present in the model's
pipeline.

```bash
$ python -m spacy evaluate [model] [data_path] [--displacy-path] [--displacy-limit]
[--gpu-id] [--gold-preproc] [--return-scores]
```

| Argument                  | Type           | Description                                                                                                                                              |
| ------------------------- | -------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `model`                   | positional     | Model to evaluate. Can be a package or shortcut link name, or a path to a model data directory.                                                          |
| `data_path`               | positional     | Location of JSON-formatted evaluation data.                                                                                                              |
| `--displacy-path`, `-dp`  | option         | Directory to output rendered parses as HTML. If not set, no visualizations will be generated.                                                            |
| `--displacy-limit`, `-dl` | option         | Number of parses to generate per file. Defaults to `25`. Keep in mind that a significantly higher number might cause the `.html` files to render slowly. |
| `--gpu-id`, `-g`          | option         | GPU to use, if any. Defaults to `-1` for CPU.                                                                                                            |
| `--gold-preproc`, `-G`    | flag           | Use gold preprocessing.                                                                                                                                  |
| `--return-scores`, `-R`   | flag           | Return dict containing model scores.                                                                                                                     |
| **CREATES**               | `stdout`, HTML | Training results and optional displaCy visualizations.                                                                                                   |

## Package {#package}

Generate a [model Python package](/usage/training#models-generating) from an
existing model data directory. All data files are copied over. If the path to a
`meta.json` is supplied, or a `meta.json` is found in the input directory, this
file is used. Otherwise, the data can be entered directly from the command line.
After packaging, you can run `python setup.py sdist` from the newly created
directory to turn your model into an installable archive file.

```bash
$ python -m spacy package [input_dir] [output_dir] [--meta-path] [--create-meta] [--force]
```

```bash
### Example
python -m spacy package /input /output
cd /output/en_model-0.0.0
python setup.py sdist
pip install dist/en_model-0.0.0.tar.gz
```

| Argument                                         | Type       | Description                                                                                                                                                                                     |
| ------------------------------------------------ | ---------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `input_dir`                                      | positional | Path to directory containing model data.                                                                                                                                                        |
| `output_dir`                                     | positional | Directory to create package folder in.                                                                                                                                                          |
| `--meta-path`, `-m` <Tag variant="new">2</Tag>   | option     | Path to `meta.json` file (optional).                                                                                                                                                            |
| `--create-meta`, `-c` <Tag variant="new">2</Tag> | flag       | Create a `meta.json` file on the command line, even if one already exists in the directory. If an existing file is found, its entries will be shown as the defaults in the command line prompt. | `--force`, `-f` | flag | Force overwriting of existing folder in output directory. |
| `--help`, `-h`                                   | flag       | Show help message and available arguments.                                                                                                                                                      |
| **CREATES**                                      | directory  | A Python package containing the spaCy model.                                                                                                                                                    |
