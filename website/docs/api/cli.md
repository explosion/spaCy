---
title: Command Line Interface
teaser: Download, train and package models, and debug spaCy
source: spacy/cli
menu:
  - ['download', 'download']
  - ['info', 'info']
  - ['validate', 'validate']
  - ['init', 'init']
  - ['convert', 'convert']
  - ['debug', 'debug']
  - ['train', 'train']
  - ['pretrain', 'pretrain']
  - ['evaluate', 'evaluate']
  - ['package', 'package']
  - ['project', 'project']
---

spaCy's CLI provides a range of helpful commands for downloading and training
models, converting data and debugging your config, data and installation. For a
list of available commands, you can type `python -m spacy --help`. You can also
add the `--help` flag to any command or subcommand to see the description,
available arguments and usage.

## download {#download tag="command"}

Download [models](/usage/models) for spaCy. The downloader finds the
best-matching compatible version and uses `pip install` to download the model as
a package. Direct downloads don't perform any compatibility checks and require
the model name to be specified with its version (e.g. `en_core_web_sm-2.2.0`).

> #### Downloading best practices
>
> The `download` command is mostly intended as a convenient, interactive wrapper
> – it performs compatibility checks and prints detailed messages in case things
> go wrong. It's **not recommended** to use this command as part of an automated
> process. If you know which model your project needs, you should consider a
> [direct download via pip](/usage/models#download-pip), or uploading the model
> to a local PyPi installation and fetching it straight from there. This will
> also allow you to add it as a versioned package dependency to your project.

```cli
$ python -m spacy download [model] [--direct] [pip_args]
```

| Name                                  | Description                                                                                                                                                                                                                          |
| ------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `model`                               | Model name, e.g. [`en_core_web_sm`](/models/en#en_core_web_sm). ~~str (positional)~~                                                                                                                                                 |
| `--direct`, `-d`                      | Force direct download of exact model version. ~~bool (flag)~~                                                                                                                                                                        |
| `--help`, `-h`                        | Show help message and available arguments. ~~bool (flag)~~                                                                                                                                                                           |
| pip args <Tag variant="new">2.1</Tag> | Additional installation options to be passed to `pip install` when installing the model package. For example, `--user` to install to the user home directory or `--no-deps` to not install model dependencies. ~~Any (option/flag)~~ |
| **CREATES**                           | The installed model package in your `site-packages` directory.                                                                                                                                                                       |

## info {#info tag="command"}

Print information about your spaCy installation, models and local setup, and
generate [Markdown](https://en.wikipedia.org/wiki/Markdown)-formatted markup to
copy-paste into [GitHub issues](https://github.com/explosion/spaCy/issues).

```cli
$ python -m spacy info [--markdown] [--silent]
```

```cli
$ python -m spacy info [model] [--markdown] [--silent]
```

| Name                                             | Description                                                                    |
| ------------------------------------------------ | ------------------------------------------------------------------------------ |
| `model`                                          | A model, i.e. package name or path (optional). ~~Optional[str] \(positional)~~ |
| `--markdown`, `-md`                              | Print information as Markdown. ~~bool (flag)~~                                 |
| `--silent`, `-s` <Tag variant="new">2.0.12</Tag> | Don't print anything, just return the values. ~~bool (flag)~~                  |
| `--help`, `-h`                                   | Show help message and available arguments. ~~bool (flag)~~                     |
| **PRINTS**                                       | Information about your spaCy installation.                                     |

## validate {#validate new="2" tag="command"}

Find all models installed in the current environment and check whether they are
compatible with the currently installed version of spaCy. Should be run after
upgrading spaCy via `pip install -U spacy` to ensure that all installed models
are can be used with the new version. It will show a list of models and their
installed versions. If any model is out of date, the latest compatible versions
and command for updating are shown.

> #### Automated validation
>
> You can also use the `validate` command as part of your build process or test
> suite, to ensure all models are up to date before proceeding. If incompatible
> models are found, it will return `1`.

```cli
$ python -m spacy validate
```

| Name       | Description                                               |
| ---------- | --------------------------------------------------------- |
| **PRINTS** | Details about the compatibility of your installed models. |

## init {#init new="3"}

The `spacy init` CLI includes helpful commands for initializing training config
files and model directories.

### init config {#init-config new="3" tag="command"}

Initialize and save a [`config.cfg` file](/usage/training#config) using the
**recommended settings** for your use case. It works just like the
[quickstart widget](/usage/training#quickstart), only that it also auto-fills
all default values and exports a [training](/usage/training#config)-ready
config. The settings you specify will impact the suggested model architectures
and pipeline setup, as well as the hyperparameters. You can also adjust and
customize those settings in your config file later.

> #### Example
>
> ```cli
> $ python -m spacy init config config.cfg --lang en --pipeline ner,textcat --optimize accuracy
> ```

```cli
$ python -m spacy init config [output_file] [--lang] [--pipeline] [--optimize] [--cpu]
```

| Name               | Description                                                                                                                                                                                                                                                                                                                        |
| ------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `output_file`      | Path to output `.cfg` file or `-` to write the config to stdout (so you can pipe it forward to a file). Note that if you're writing to stdout, no additional logging info is printed. ~~Path (positional)~~                                                                                                                        |
| `--lang`, `-l`     | Optional code of the [language](/usage/models#languages) to use. Defaults to `"en"`. ~~str (option)~~                                                                                                                                                                                                                              |
| `--pipeline`, `-p` | Comma-separated list of trainable [pipeline components](/usage/processing-pipelines#built-in) to include in the model. Defaults to `"tagger,parser,ner"`. ~~str (option)~~                                                                                                                                                         |
| `--optimize`, `-o` | `"efficiency"` or `"accuracy"`. Whether to optimize for efficiency (faster inference, smaller model, lower memory consumption) or higher accuracy (potentially larger and slower model). This will impact the choice of architecture, pretrained weights and related hyperparameters. Defaults to `"efficiency"`. ~~str (option)~~ |
| `--cpu`, `-C`      | Whether the model needs to run on CPU. This will impact the choice of architecture, pretrained weights and related hyperparameters. ~~bool (flag)~~                                                                                                                                                                                |
| `--help`, `-h`     | Show help message and available arguments. ~~bool (flag)~~                                                                                                                                                                                                                                                                         |
| **CREATES**        | The config file for training.                                                                                                                                                                                                                                                                                                      |

### init fill-config {#init-fill-config new="3"}

Auto-fill a partial [`config.cfg` file](/usage/training#config) file with **all
default values**, e.g. a config generated with the
[quickstart widget](/usage/training#quickstart). Config files used for training
should always be complete and not contain any hidden defaults or missing values,
so this command helps you create your final training config. In order to find
the available settings and defaults, all functions referenced in the config will
be created, and their signatures are used to find the defaults. If your config
contains a problem that can't be resolved automatically, spaCy will show you a
validation error with more details.

> #### Example
>
> ```cli
> $ python -m spacy init fill-config base.cfg config.cfg
> ```

```cli
$ python -m spacy init fill-config [base_path] [output_file] [--diff]
```

| Name           | Description                                                                                                                         |
| -------------- | ----------------------------------------------------------------------------------------------------------------------------------- |
| `base_path`    | Path to base config to fill, e.g. generated by the [quickstart widget](/usage/training#quickstart). ~~Path (positional)~~           |
| `output_file`  | Path to output `.cfg` file. If not set, the config is written to stdout so you can pipe it forward to a file. ~~Path (positional)~~ |
| `--diff`, `-D` | Print a visual diff highlighting the changes. ~~bool (flag)~~                                                                       |
| `--help`, `-h` | Show help message and available arguments. ~~bool (flag)~~                                                                          |
| **CREATES**    | Complete and auto-filled config file for training.                                                                                  |

### init model {#init-model new="2" tag="command"}

Create a new model directory from raw data, like word frequencies, Brown
clusters and word vectors. Note that in order to populate the model's vocab, you
need to pass in a JSONL-formatted
[vocabulary file](/api/data-formats#vocab-jsonl) as `--jsonl-loc` with optional
`id` values that correspond to the vectors table. Just loading in vectors will
not automatically populate the vocab.

<Infobox title="New in v3.0" variant="warning">

The `init-model` command is now available as a subcommand of `spacy init`.

</Infobox>

```cli
$ python -m spacy init model [lang] [output_dir] [--jsonl-loc] [--vectors-loc] [--prune-vectors]
```

| Name                                                    | Description                                                                                                                                                                                                                                                                         |
| ------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `lang`                                                  | Model language [ISO code](https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes), e.g. `en`. ~~str (positional)~~                                                                                                                                                                   |
| `output_dir`                                            | Model output directory. Will be created if it doesn't exist. ~~Path (positional)~~                                                                                                                                                                                                  |
| `--jsonl-loc`, `-j`                                     | Optional location of JSONL-formatted [vocabulary file](/api/data-formats#vocab-jsonl) with lexical attributes. ~~Optional[Path] \(option)~~                                                                                                                                         |
| `--vectors-loc`, `-v`                                   | Optional location of vectors. Should be a file where the first row contains the dimensions of the vectors, followed by a space-separated Word2Vec table. File can be provided in `.txt` format or as a zipped text file in `.zip` or `.tar.gz` format. ~~Optional[Path] \(option)~~ |
| `--truncate-vectors`, `-t` <Tag variant="new">2.3</Tag> | Number of vectors to truncate to when reading in vectors file. Defaults to `0` for no truncation. ~~int (option)~~                                                                                                                                                                  |
| `--prune-vectors`, `-V`                                 | Number of vectors to prune the vocabulary to. Defaults to `-1` for no pruning. ~~int (option)~~                                                                                                                                                                                     |
| `--vectors-name`, `-vn`                                 | Name to assign to the word vectors in the `meta.json`, e.g. `en_core_web_md.vectors`. ~~str (option)~~                                                                                                                                                                              |
| `--help`, `-h`                                          | Show help message and available arguments. ~~bool (flag)~~                                                                                                                                                                                                                          |
| **CREATES**                                             | A spaCy model containing the vocab and vectors.                                                                                                                                                                                                                                     |

## convert {#convert tag="command"}

Convert files into spaCy's
[binary training data format](/api/data-formats#binary-training), a serialized
[`DocBin`](/api/docbin), for use with the `train` command and other experiment
management functions. The converter can be specified on the command line, or
chosen based on the file extension of the input file.

```cli
$ python -m spacy convert [input_file] [output_dir] [--converter] [--file-type] [--n-sents] [--seg-sents] [--model] [--morphology] [--merge-subtokens] [--ner-map] [--lang]
```

| Name                                             | Description                                                                                                                               |
| ------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------- |
| `input_file`                                     | Input file. ~~Path (positional)~~                                                                                                         |
| `output_dir`                                     | Output directory for converted file. Defaults to `"-"`, meaning data will be written to `stdout`. ~~Optional[Path] \(positional)~~        |
| `--converter`, `-c` <Tag variant="new">2</Tag>   | Name of converter to use (see below). ~~str (option)~~                                                                                    |
| `--file-type`, `-t` <Tag variant="new">2.1</Tag> | Type of file to create. Either `spacy` (default) for binary [`DocBin`](/api/docbin) data or `json` for v2.x JSON format. ~~str (option)~~ |
| `--n-sents`, `-n`                                | Number of sentences per document. ~~int (option)~~                                                                                        |
| `--seg-sents`, `-s` <Tag variant="new">2.2</Tag> | Segment sentences (for `--converter ner`). ~~bool (flag)~~                                                                                |
| `--model`, `-b` <Tag variant="new">2.2</Tag>     | Model for parser-based sentence segmentation (for `--seg-sents`). ~~Optional[str](option)~~                                               |
| `--morphology`, `-m`                             | Enable appending morphology to tags. ~~bool (flag)~~                                                                                      |
| `--ner-map`, `-nm`                               | NER tag mapping (as JSON-encoded dict of entity types). ~~Optional[Path](option)~~                                                        |
| `--lang`, `-l` <Tag variant="new">2.1</Tag>      | Language code (if tokenizer required). ~~Optional[str] \(option)~~                                                                        |
| `--help`, `-h`                                   | Show help message and available arguments. ~~bool (flag)~~                                                                                |
| **CREATES**                                      | Binary [`DocBin`](/api/docbin) training data that can be used with [`spacy train`](/api/cli#train).                                       |

### Converters {#converters}

| ID      | Description                                                                                                                                                                                                                                                                                                                                                                                    |
| ------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `auto`  | Automatically pick converter based on file extension and file content (default).                                                                                                                                                                                                                                                                                                               |
| `json`  | JSON-formatted training data used in spaCy v2.x.                                                                                                                                                                                                                                                                                                                                               |
| `conll` | Universal Dependencies `.conllu` or `.conll` format.                                                                                                                                                                                                                                                                                                                                           |
| `ner`   | NER with IOB/IOB2 tags, one token per line with columns separated by whitespace. The first column is the token and the final column is the IOB tag. Sentences are separated by blank lines and documents are separated by the line `-DOCSTART- -X- O O`. Supports CoNLL 2003 NER format. See [sample data](https://github.com/explosion/spaCy/tree/master/examples/training/ner_example_data). |
| `iob`   | NER with IOB/IOB2 tags, one sentence per line with tokens separated by whitespace and annotation separated by `|`, either `word|B-ENT` or `word|POS|B-ENT`. See [sample data](https://github.com/explosion/spaCy/tree/master/examples/training/ner_example_data).                                                                                                                              |

## debug {#debug new="3"}

The `spacy debug` CLI includes helpful commands for debugging and profiling your
configs, data and implementations.

### debug config {#debug-config new="3" tag="command"}

Debug a [`config.cfg` file](/usage/training#config) and show validation errors.
The command will create all objects in the tree and validate them. Note that
some config validation errors are blocking and will prevent the rest of the
config from being resolved. This means that you may not see all validation
errors at once and some issues are only shown once previous errors have been
fixed. To auto-fill a partial config and save the result, you can use the
[`init fillconfig`](/api/cli#init-fill-config) command.

```cli
$ python -m spacy debug config [config_path] [--code_path] [overrides]
```

> #### Example
>
> ```cli
> $ python -m spacy debug config ./config.cfg
> ```

<Accordion title="Example output" spaced>

```
✘ Config validation error

training -> dropout     field required
training -> optimizer   field required
training -> optimize    extra fields not permitted

{'vectors': 'en_vectors_web_lg', 'seed': 0, 'accumulate_gradient': 1, 'init_tok2vec': None, 'raw_text': None, 'patience': 1600, 'max_epochs': 0, 'max_steps': 20000, 'eval_frequency': 200, 'frozen_components': [], 'optimize': None, 'batcher': {'@batchers': 'batch_by_words.v1', 'discard_oversize': False, 'tolerance': 0.2, 'get_length': None, 'size': {'@schedules': 'compounding.v1', 'start': 100, 'stop': 1000, 'compound': 1.001, 't': 0.0}}, 'dev_corpus': {'@readers': 'spacy.Corpus.v1', 'path': '', 'max_length': 0, 'gold_preproc': False, 'limit': 0}, 'score_weights': {'tag_acc': 0.5, 'dep_uas': 0.25, 'dep_las': 0.25, 'sents_f': 0.0}, 'train_corpus': {'@readers': 'spacy.Corpus.v1', 'path': '', 'max_length': 0, 'gold_preproc': False, 'limit': 0}}

If your config contains missing values, you can run the 'init fill-config'
command to fill in all the defaults, if possible:

python -m spacy init fill-config tmp/starter-config_invalid.cfg --base tmp/starter-config_invalid.cfg
```

</Accordion>

| Name                | Description                                                                                                                                                                                |
| ------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `config_path`       | Path to [training config](/api/data-formats#config) file containing all settings and hyperparameters. ~~Path (positional)~~                                                                |
| `--code_path`, `-c` | Path to Python file with additional code to be imported. Allows [registering custom functions](/usage/training#custom-functions) for new architectures. ~~Optional[Path] \(option)~~       |
| `--help`, `-h`      | Show help message and available arguments. ~~bool (flag)~~                                                                                                                                 |
| overrides           | Config parameters to override. Should be options starting with `--` that correspond to the config section and value to override, e.g. `--paths.train ./train.spacy`. ~~Any (option/flag)~~ |
| **PRINTS**          | Config validation errors, if available.                                                                                                                                                    |

### debug data {#debug-data tag="command"}

Analyze, debug, and validate your training and development data. Get useful
stats, and find problems like invalid entity annotations, cyclic dependencies,
low data labels and more.

<Infobox title="New in v3.0" variant="warning">

The `debug data` command is now available as a subcommand of `spacy debug`. It
takes the same arguments as `train` and reads settings off the
[`config.cfg` file](/usage/training#config) and optional
[overrides](/usage/training#config-overrides) on the CLI.

</Infobox>

```cli
$ python -m spacy debug data [config_path] [--code] [--ignore-warnings] [--verbose] [--no-format] [overrides]
```

> #### Example
>
> ```cli
> $ python -m spacy debug data ./config.cfg
> ```

<Accordion title="Example output" spaced>

```
=========================== Data format validation ===========================
✔ Corpus is loadable

=============================== Training stats ===============================
Training pipeline: tagger, parser, ner
Starting with blank model 'en'
18127 training docs
2939 evaluation docs
⚠ 34 training examples also in evaluation data

============================== Vocab & Vectors ==============================
ℹ 2083156 total words in the data (56962 unique)
⚠ 13020 misaligned tokens in the training data
⚠ 2423 misaligned tokens in the dev data
10 most common words: 'the' (98429), ',' (91756), '.' (87073), 'to' (50058),
'of' (49559), 'and' (44416), 'a' (34010), 'in' (31424), 'that' (22792), 'is'
(18952)
ℹ No word vectors present in the model

========================== Named Entity Recognition ==========================
ℹ 18 new labels, 0 existing labels
528978 missing values (tokens with '-' label)
New: 'ORG' (23860), 'PERSON' (21395), 'GPE' (21193), 'DATE' (18080), 'CARDINAL'
(10490), 'NORP' (9033), 'MONEY' (5164), 'PERCENT' (3761), 'ORDINAL' (2122),
'LOC' (2113), 'TIME' (1616), 'WORK_OF_ART' (1229), 'QUANTITY' (1150), 'FAC'
(1134), 'EVENT' (974), 'PRODUCT' (935), 'LAW' (444), 'LANGUAGE' (338)
✔ Good amount of examples for all labels
✔ Examples without occurences available for all labels
✔ No entities consisting of or starting/ending with whitespace

=========================== Part-of-speech Tagging ===========================
ℹ 49 labels in data (57 labels in tag map)
'NN' (266331), 'IN' (227365), 'DT' (185600), 'NNP' (164404), 'JJ' (119830),
'NNS' (110957), '.' (101482), ',' (92476), 'RB' (90090), 'PRP' (90081), 'VB'
(74538), 'VBD' (68199), 'CC' (62862), 'VBZ' (50712), 'VBP' (43420), 'VBN'
(42193), 'CD' (40326), 'VBG' (34764), 'TO' (31085), 'MD' (25863), 'PRP$'
(23335), 'HYPH' (13833), 'POS' (13427), 'UH' (13322), 'WP' (10423), 'WDT'
(9850), 'RP' (8230), 'WRB' (8201), ':' (8168), '''' (7392), '``' (6984), 'NNPS'
(5817), 'JJR' (5689), '$' (3710), 'EX' (3465), 'JJS' (3118), 'RBR' (2872),
'-RRB-' (2825), '-LRB-' (2788), 'PDT' (2078), 'XX' (1316), 'RBS' (1142), 'FW'
(794), 'NFP' (557), 'SYM' (440), 'WP$' (294), 'LS' (293), 'ADD' (191), 'AFX'
(24)
✔ All labels present in tag map for language 'en'

============================= Dependency Parsing =============================
ℹ Found 111703 sentences with an average length of 18.6 words.
ℹ Found 2251 nonprojective train sentences
ℹ Found 303 nonprojective dev sentences
ℹ 47 labels in train data
ℹ 211 labels in projectivized train data
'punct' (236796), 'prep' (188853), 'pobj' (182533), 'det' (172674), 'nsubj'
(169481), 'compound' (116142), 'ROOT' (111697), 'amod' (107945), 'dobj' (93540),
'aux' (86802), 'advmod' (86197), 'cc' (62679), 'conj' (59575), 'poss' (36449),
'ccomp' (36343), 'advcl' (29017), 'mark' (27990), 'nummod' (24582), 'relcl'
(21359), 'xcomp' (21081), 'attr' (18347), 'npadvmod' (17740), 'acomp' (17204),
'auxpass' (15639), 'appos' (15368), 'neg' (15266), 'nsubjpass' (13922), 'case'
(13408), 'acl' (12574), 'pcomp' (10340), 'nmod' (9736), 'intj' (9285), 'prt'
(8196), 'quantmod' (7403), 'dep' (4300), 'dative' (4091), 'agent' (3908), 'expl'
(3456), 'parataxis' (3099), 'oprd' (2326), 'predet' (1946), 'csubj' (1494),
'subtok' (1147), 'preconj' (692), 'meta' (469), 'csubjpass' (64), 'iobj' (1)
⚠ Low number of examples for label 'iobj' (1)
⚠ Low number of examples for 130 labels in the projectivized dependency
trees used for training. You may want to projectivize labels such as punct
before training in order to improve parser performance.
⚠ Projectivized labels with low numbers of examples: appos||attr: 12
advmod||dobj: 13 prep||ccomp: 12 nsubjpass||ccomp: 15 pcomp||prep: 14
amod||dobj: 9 attr||xcomp: 14 nmod||nsubj: 17 prep||advcl: 2 prep||prep: 5
nsubj||conj: 12 advcl||advmod: 18 ccomp||advmod: 11 ccomp||pcomp: 5 acl||pobj:
10 npadvmod||acomp: 7 dobj||pcomp: 14 nsubjpass||pcomp: 1 nmod||pobj: 8
amod||attr: 6 nmod||dobj: 12 aux||conj: 1 neg||conj: 1 dative||xcomp: 11
pobj||dative: 3 xcomp||acomp: 19 advcl||pobj: 2 nsubj||advcl: 2 csubj||ccomp: 1
advcl||acl: 1 relcl||nmod: 2 dobj||advcl: 10 advmod||advcl: 3 nmod||nsubjpass: 6
amod||pobj: 5 cc||neg: 1 attr||ccomp: 16 advcl||xcomp: 3 nmod||attr: 4
advcl||nsubjpass: 5 advcl||ccomp: 4 ccomp||conj: 1 punct||acl: 1 meta||acl: 1
parataxis||acl: 1 prep||acl: 1 amod||nsubj: 7 ccomp||ccomp: 3 acomp||xcomp: 5
dobj||acl: 5 prep||oprd: 6 advmod||acl: 2 dative||advcl: 1 pobj||agent: 5
xcomp||amod: 1 dep||advcl: 1 prep||amod: 8 relcl||compound: 1 advcl||csubj: 3
npadvmod||conj: 2 npadvmod||xcomp: 4 advmod||nsubj: 3 ccomp||amod: 7
advcl||conj: 1 nmod||conj: 2 advmod||nsubjpass: 2 dep||xcomp: 2 appos||ccomp: 1
advmod||dep: 1 advmod||advmod: 5 aux||xcomp: 8 dep||advmod: 1 dative||ccomp: 2
prep||dep: 1 conj||conj: 1 dep||ccomp: 4 cc||ROOT: 1 prep||ROOT: 1 nsubj||pcomp:
3 advmod||prep: 2 relcl||dative: 1 acl||conj: 1 advcl||attr: 4 prep||npadvmod: 1
nsubjpass||xcomp: 1 neg||advmod: 1 xcomp||oprd: 1 advcl||advcl: 1 dobj||dep: 3
nsubjpass||parataxis: 1 attr||pcomp: 1 ccomp||parataxis: 1 advmod||attr: 1
nmod||oprd: 1 appos||nmod: 2 advmod||relcl: 1 appos||npadvmod: 1 appos||conj: 1
prep||expl: 1 nsubjpass||conj: 1 punct||pobj: 1 cc||pobj: 1 conj||pobj: 1
punct||conj: 1 ccomp||dep: 1 oprd||xcomp: 3 ccomp||xcomp: 1 ccomp||nsubj: 1
nmod||dep: 1 xcomp||ccomp: 1 acomp||advcl: 1 intj||advmod: 1 advmod||acomp: 2
relcl||oprd: 1 advmod||prt: 1 advmod||pobj: 1 appos||nummod: 1 relcl||npadvmod:
3 mark||advcl: 1 aux||ccomp: 1 amod||nsubjpass: 1 npadvmod||advmod: 1 conj||dep:
1 nummod||pobj: 1 amod||npadvmod: 1 intj||pobj: 1 nummod||npadvmod: 1
xcomp||xcomp: 1 aux||dep: 1 advcl||relcl: 1
⚠ The following labels were found only in the train data: xcomp||amod,
advcl||relcl, prep||nsubjpass, acl||nsubj, nsubjpass||conj, xcomp||oprd,
advmod||conj, advmod||advmod, iobj, advmod||nsubjpass, dobj||conj, ccomp||amod,
meta||acl, xcomp||xcomp, prep||attr, prep||ccomp, advcl||acomp, acl||dobj,
advcl||advcl, pobj||agent, prep||advcl, nsubjpass||xcomp, prep||dep,
acomp||xcomp, aux||ccomp, ccomp||dep, conj||dep, relcl||compound,
nsubjpass||ccomp, nmod||dobj, advmod||advcl, advmod||acl, dobj||advcl,
dative||xcomp, prep||nsubj, ccomp||ccomp, nsubj||ccomp, xcomp||acomp,
prep||acomp, dep||advmod, acl||pobj, appos||dobj, npadvmod||acomp, cc||ROOT,
relcl||nsubj, nmod||pobj, acl||nsubjpass, ccomp||advmod, pcomp||prep,
amod||dobj, advmod||attr, advcl||csubj, appos||attr, dobj||pcomp, prep||ROOT,
relcl||pobj, advmod||pobj, amod||nsubj, ccomp||xcomp, prep||oprd,
npadvmod||advmod, appos||nummod, advcl||pobj, neg||advmod, acl||attr,
appos||nsubjpass, csubj||ccomp, amod||nsubjpass, intj||pobj, dep||advcl,
cc||neg, xcomp||ccomp, dative||ccomp, nmod||oprd, pobj||dative, prep||dobj,
dep||ccomp, relcl||attr, ccomp||nsubj, advcl||xcomp, nmod||dep, advcl||advmod,
ccomp||conj, pobj||prep, advmod||acomp, advmod||relcl, attr||pcomp,
ccomp||parataxis, oprd||xcomp, intj||advmod, nmod||nsubjpass, prep||npadvmod,
parataxis||acl, prep||pobj, advcl||dobj, amod||pobj, prep||acl, conj||pobj,
advmod||dep, punct||pobj, ccomp||acomp, acomp||advcl, nummod||npadvmod,
dobj||dep, npadvmod||xcomp, advcl||conj, relcl||npadvmod, punct||acl,
relcl||dobj, dobj||xcomp, nsubjpass||parataxis, dative||advcl, relcl||nmod,
advcl||ccomp, appos||npadvmod, ccomp||pcomp, prep||amod, mark||advcl,
prep||advmod, prep||xcomp, appos||nsubj, attr||ccomp, advmod||prt, dobj||ccomp,
aux||conj, advcl||nsubj, conj||conj, advmod||ccomp, advcl||nsubjpass,
attr||xcomp, nmod||conj, npadvmod||conj, relcl||dative, prep||expl,
nsubjpass||pcomp, advmod||xcomp, advmod||dobj, appos||pobj, nsubj||conj,
relcl||nsubjpass, advcl||attr, appos||ccomp, advmod||prep, prep||conj,
nmod||attr, punct||conj, neg||conj, dep||xcomp, aux||xcomp, dobj||acl,
nummod||pobj, amod||npadvmod, nsubj||pcomp, advcl||acl, appos||nmod,
relcl||oprd, prep||prep, cc||pobj, nmod||nsubj, amod||attr, aux||dep,
appos||conj, advmod||nsubj, nsubj||advcl, acl||conj
To train a parser, your data should include at least 20 instances of each label.
⚠ Multiple root labels (ROOT, nsubj, aux, npadvmod, prep) found in
training data. spaCy's parser uses a single root label ROOT so this distinction
will not be available.

================================== Summary ==================================
✔ 5 checks passed
⚠ 8 warnings
```

</Accordion>

| Name                       | Description                                                                                                                                                                                |
| -------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `config_path`              | Path to [training config](/api/data-formats#config) file containing all settings and hyperparameters. ~~Path (positional)~~                                                                |
| `--code`, `-c`             | Path to Python file with additional code to be imported. Allows [registering custom functions](/usage/training#custom-functions) for new architectures. ~~Optional[Path] \(option)~~       |
| `--ignore-warnings`, `-IW` | Ignore warnings, only show stats and errors. ~~bool (flag)~~                                                                                                                               |
| `--verbose`, `-V`          | Print additional information and explanations. ~~bool (flag)~~                                                                                                                             |
| `--no-format`, `-NF`       | Don't pretty-print the results. Use this if you want to write to a file. ~~bool (flag)~~                                                                                                   |
| `--help`, `-h`             | Show help message and available arguments. ~~bool (flag)~~                                                                                                                                 |
| overrides                  | Config parameters to override. Should be options starting with `--` that correspond to the config section and value to override, e.g. `--paths.train ./train.spacy`. ~~Any (option/flag)~~ |
| **PRINTS**                 | Debugging information.                                                                                                                                                                     |

### debug profile {#debug-profile tag="command"}

Profile which functions take the most time in a spaCy pipeline. Input should be
formatted as one JSON object per line with a key `"text"`. It can either be
provided as a JSONL file, or be read from `sys.sytdin`. If no input file is
specified, the IMDB dataset is loaded via
[`ml_datasets`](https://github.com/explosion/ml_datasets).

<Infobox title="New in v3.0" variant="warning">

The `profile` command is now available as a subcommand of `spacy debug`.

</Infobox>

```cli
$ python -m spacy debug profile [model] [inputs] [--n-texts]
```

| Name              | Description                                                                        |
| ----------------- | ---------------------------------------------------------------------------------- |
| `model`           | A loadable spaCy model. ~~str (positional)~~                                       |
| `inputs`          | Optional path to input file, or `-` for standard input. ~~Path (positional)~~      |
| `--n-texts`, `-n` | Maximum number of texts to use if available. Defaults to `10000`. ~~int (option)~~ |
| `--help`, `-h`    | Show help message and available arguments. ~~bool (flag)~~                         |
| **PRINTS**        | Profiling information for the model.                                               |

### debug model {#debug-model new="3" tag="command"}

Debug a Thinc [`Model`](https://thinc.ai/docs/api-model) by running it on a
sample text and checking how it updates its internal weights and parameters.

```cli
$ python -m spacy debug model [config_path] [component] [--layers] [-DIM] [-PAR] [-GRAD] [-ATTR] [-P0] [-P1] [-P2] [P3] [--gpu-id]
```

<Accordion title="Example outputs" spaced>

In this example log, we just print the name of each layer after creation of the
model ("Step 0"), which helps us to understand the internal structure of the
Neural Network, and to focus on specific layers that we want to inspect further
(see next example).

```cli
$ python -m spacy debug model ./config.cfg tagger -P0
```

```
ℹ Using CPU
ℹ Fixing random seed: 0
ℹ Analysing model with ID 62

========================== STEP 0 - before training ==========================
ℹ Layer 0: model ID 62:
'extract_features>>list2ragged>>with_array-ints-getitem>>hashembed|ints-getitem>>hashembed|ints-getitem>>hashembed|ints-getitem>>hashembed>>with_array-maxout>>layernorm>>dropout>>ragged2list>>with_array-residual>>residual>>residual>>residual>>with_array-softmax'
ℹ Layer 1: model ID 59:
'extract_features>>list2ragged>>with_array-ints-getitem>>hashembed|ints-getitem>>hashembed|ints-getitem>>hashembed|ints-getitem>>hashembed>>with_array-maxout>>layernorm>>dropout>>ragged2list>>with_array-residual>>residual>>residual>>residual'
ℹ Layer 2: model ID 61: 'with_array-softmax'
ℹ Layer 3: model ID 24:
'extract_features>>list2ragged>>with_array-ints-getitem>>hashembed|ints-getitem>>hashembed|ints-getitem>>hashembed|ints-getitem>>hashembed>>with_array-maxout>>layernorm>>dropout>>ragged2list'
ℹ Layer 4: model ID 58: 'with_array-residual>>residual>>residual>>residual'
ℹ Layer 5: model ID 60: 'softmax'
ℹ Layer 6: model ID 13: 'extract_features'
ℹ Layer 7: model ID 14: 'list2ragged'
ℹ Layer 8: model ID 16:
'with_array-ints-getitem>>hashembed|ints-getitem>>hashembed|ints-getitem>>hashembed|ints-getitem>>hashembed'
ℹ Layer 9: model ID 22: 'with_array-maxout>>layernorm>>dropout'
ℹ Layer 10: model ID 23: 'ragged2list'
ℹ Layer 11: model ID 57: 'residual>>residual>>residual>>residual'
ℹ Layer 12: model ID 15:
'ints-getitem>>hashembed|ints-getitem>>hashembed|ints-getitem>>hashembed|ints-getitem>>hashembed'
ℹ Layer 13: model ID 21: 'maxout>>layernorm>>dropout'
ℹ Layer 14: model ID 32: 'residual'
ℹ Layer 15: model ID 40: 'residual'
ℹ Layer 16: model ID 48: 'residual'
ℹ Layer 17: model ID 56: 'residual'
ℹ Layer 18: model ID 3: 'ints-getitem>>hashembed'
ℹ Layer 19: model ID 6: 'ints-getitem>>hashembed'
ℹ Layer 20: model ID 9: 'ints-getitem>>hashembed'
...
```

In this example log, we see how initialization of the model (Step 1) propagates
the correct values for the `nI` (input) and `nO` (output) dimensions of the
various layers. In the `softmax` layer, this step also defines the `W` matrix as
an all-zero matrix determined by the `nO` and `nI` dimensions. After a first
training step (Step 2), this matrix has clearly updated its values through the
training feedback loop.

```cli
$ python -m spacy debug model ./config.cfg tagger -l "5,15" -DIM -PAR -P0 -P1 -P2
```

```
ℹ Using CPU
ℹ Fixing random seed: 0
ℹ Analysing model with ID 62

========================= STEP 0 - before training =========================
ℹ Layer 5: model ID 60: 'softmax'
ℹ  - dim nO: None
ℹ  - dim nI: 96
ℹ  - param W: None
ℹ  - param b: None
ℹ Layer 15: model ID 40: 'residual'
ℹ  - dim nO: None
ℹ  - dim nI: None

======================= STEP 1 - after initialization =======================
ℹ Layer 5: model ID 60: 'softmax'
ℹ  - dim nO: 4
ℹ  - dim nI: 96
ℹ  - param W: (4, 96) - sample: [0. 0. 0. 0. 0.]
ℹ  - param b: (4,) - sample: [0. 0. 0. 0.]
ℹ Layer 15: model ID 40: 'residual'
ℹ  - dim nO: 96
ℹ  - dim nI: None

========================== STEP 2 - after training ==========================
ℹ Layer 5: model ID 60: 'softmax'
ℹ  - dim nO: 4
ℹ  - dim nI: 96
ℹ  - param W: (4, 96) - sample: [ 0.00283958 -0.00294119  0.00268396 -0.00296219
-0.00297141]
ℹ  - param b: (4,) - sample: [0.00300002 0.00300002 0.00300002 0.00300002]
ℹ Layer 15: model ID 40: 'residual'
ℹ  - dim nO: 96
ℹ  - dim nI: None
```

</Accordion>

| Name                    | Description                                                                                                                 |
| ----------------------- | --------------------------------------------------------------------------------------------------------------------------- |
| `config_path`           | Path to [training config](/api/data-formats#config) file containing all settings and hyperparameters. ~~Path (positional)~~ |
| `component`             | Name of the pipeline component of which the model should be analyzed. ~~str (positional)~~                                  |
| `--layers`, `-l`        | Comma-separated names of layer IDs to print. ~~str (option)~~                                                               |
| `--dimensions`, `-DIM`  | Show dimensions of each layer. ~~bool (flag)~~                                                                              |
| `--parameters`, `-PAR`  | Show parameters of each layer. ~~bool (flag)~~                                                                              |
| `--gradients`, `-GRAD`  | Show gradients of each layer. ~~bool (flag)~~                                                                               |
| `--attributes`, `-ATTR` | Show attributes of each layer. ~~bool (flag)~~                                                                              |
| `--print-step0`, `-P0`  | Print model before training. ~~bool (flag)~~                                                                                |
| `--print-step1`, `-P1`  | Print model after initialization. ~~bool (flag)~~                                                                           |
| `--print-step2`, `-P2`  | Print model after training. ~~bool (flag)~~                                                                                 |
| `--print-step3`, `-P3`  | Print final predictions. ~~bool (flag)~~                                                                                    |
| `--gpu-id`, `-g`        | GPU ID or `-1` for CPU. Defaults to `-1`. ~~int (option)~~                                                                  |
| `--help`, `-h`          | Show help message and available arguments. ~~bool (flag)~~                                                                  |
| **PRINTS**              | Debugging information.                                                                                                      |

## train {#train tag="command"}

Train a model. Expects data in spaCy's
[binary format](/api/data-formats#training) and a
[config file](/api/data-formats#config) with all settings and hyperparameters.
Will save out the best model from all epochs, as well as the final model. The
`--code` argument can be used to provide a Python file that's imported before
the training process starts. This lets you register
[custom functions](/usage/training#custom-functions) and architectures and refer
to them in your config, all while still using spaCy's built-in `train` workflow.
If you need to manage complex multi-step training workflows, check out the new
[spaCy projects](/usage/projects).

<Infobox title="New in v3.0" variant="warning">

The `train` command doesn't take a long list of command-line arguments anymore
and instead expects a single [`config.cfg` file](/usage/training#config)
containing all settings for the pipeline, training process and hyperparameters.
Config values can be [overwritten](/usage/training#config-overrides) on the CLI
if needed. For example, `--paths.train ./train.spacy` sets the variable `train`
in the section `[paths]`.

</Infobox>

```cli
$ python -m spacy train [config_path] [--output] [--code] [--verbose] [overrides]
```

| Name              | Description                                                                                                                                                                                |
| ----------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `config_path`     | Path to [training config](/api/data-formats#config) file containing all settings and hyperparameters. ~~Path (positional)~~                                                                |
| `--output`, `-o`  | Directory to store model in. Will be created if it doesn't exist. ~~Optional[Path] \(positional)~~                                                                                         |
| `--code`, `-c`    | Path to Python file with additional code to be imported. Allows [registering custom functions](/usage/training#custom-functions) for new architectures. ~~Optional[Path] \(option)~~       |
| `--verbose`, `-V` | Show more detailed messages during training. ~~bool (flag)~~                                                                                                                               |
| `--help`, `-h`    | Show help message and available arguments. ~~bool (flag)~~                                                                                                                                 |
| overrides         | Config parameters to override. Should be options starting with `--` that correspond to the config section and value to override, e.g. `--paths.train ./train.spacy`. ~~Any (option/flag)~~ |
| **CREATES**       | The final model and the best model.                                                                                                                                                        |

## pretrain {#pretrain new="2.1" tag="command,experimental"}

Pretrain the "token to vector" ([`Tok2vec`](/api/tok2vec)) layer of pipeline
components on [raw text](/api/data-formats#pretrain), using an approximate
language-modeling objective. Specifically, we load pretrained vectors, and train
a component like a CNN, BiLSTM, etc to predict vectors which match the
pretrained ones. The weights are saved to a directory after each epoch. You can
then include a **path to one of these pretrained weights files** in your
[training config](/usage/training#config) as the `init_tok2vec` setting when you
train your model. This technique may be especially helpful if you have little
labelled data. See the usage docs on [pretraining](/usage/training#pretraining)
for more info.

<Infobox title="Changed in v3.0" variant="warning">

As of spaCy v3.0, the `pretrain` command takes the same
[config file](/usage/training#config) as the `train` command. This ensures that
settings are consistent between pretraining and training. Settings for
pretraining can be defined in the `[pretraining]` block of the config file. See
the [data format](/api/data-formats#config) for details.

</Infobox>

```cli
$ python -m spacy pretrain [texts_loc] [output_dir] [config_path] [--code] [--resume-path] [--epoch-resume] [overrides]
```

| Name                    | Description                                                                                                                                                                                        |
| ----------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `texts_loc`             | Path to JSONL file with raw texts to learn from, with text provided as the key `"text"` or tokens as the key `"tokens"`. [See here](/api/data-formats#pretrain) for details. ~~Path (positional)~~ |
| `output_dir`            | Directory to write models to on each epoch. ~~Path (positional)~~                                                                                                                                  |
| `config_path`           | Path to [training config](/api/data-formats#config) file containing all settings and hyperparameters. ~~Path (positional)~~                                                                        |
| `--code`, `-c`          | Path to Python file with additional code to be imported. Allows [registering custom functions](/usage/training#custom-functions) for new architectures. ~~Optional[Path] \(option)~~               |
| `--resume-path`, `-r`   | Path to pretrained weights from which to resume pretraining. ~~Optional[Path] \(option)~~                                                                                                          |
| `--epoch-resume`, `-er` | The epoch to resume counting from when using `--resume-path`. Prevents unintended overwriting of existing weight files. ~~Optional[int] \(option)~~                                                |
| `--help`, `-h`          | Show help message and available arguments. ~~bool (flag)~~                                                                                                                                         |
| overrides               | Config parameters to override. Should be options starting with `--` that correspond to the config section and value to override, e.g. `--training.dropout 0.2`. ~~Any (option/flag)~~              |
| **CREATES**             | The pretrained weights that can be used to initialize `spacy train`.                                                                                                                               |

## evaluate {#evaluate new="2" tag="command"}

Evaluate a model. Expects a loadable spaCy model and evaluation data in the
[binary `.spacy` format](/api/data-formats#binary-training). The
`--gold-preproc` option sets up the evaluation examples with gold-standard
sentences and tokens for the predictions. Gold preprocessing helps the
annotations align to the tokenization, and may result in sequences of more
consistent length. However, it may reduce runtime accuracy due to train/test
skew. To render a sample of dependency parses in a HTML file using the
[displaCy visualizations](/usage/visualizers), set as output directory as the
`--displacy-path` argument.

```cli
$ python -m spacy evaluate [model] [data_path] [--output] [--gold-preproc] [--gpu-id] [--displacy-path] [--displacy-limit]
```

| Name                      | Description                                                                                                                                                               |
| ------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `model`                   | Model to evaluate. Can be a package or a path to a model data directory. ~~str (positional)~~                                                                             |
| `data_path`               | Location of evaluation data in spaCy's [binary format](/api/data-formats#training). ~~Path (positional)~~                                                                 |
| `--output`, `-o`          | Output JSON file for metrics. If not set, no metrics will be exported. ~~Optional[Path] \(option)~~                                                                       |
| `--gold-preproc`, `-G`    | Use gold preprocessing. ~~bool (flag)~~                                                                                                                                   |
| `--gpu-id`, `-g`          | GPU to use, if any. Defaults to `-1` for CPU. ~~int (option)~~                                                                                                            |
| `--displacy-path`, `-dp`  | Directory to output rendered parses as HTML. If not set, no visualizations will be generated. ~~Optional[Path] \(option)~~                                                |
| `--displacy-limit`, `-dl` | Number of parses to generate per file. Defaults to `25`. Keep in mind that a significantly higher number might cause the `.html` files to render slowly. ~~int (option)~~ |
| `--help`, `-h`            | Show help message and available arguments. ~~bool (flag)~~                                                                                                                |
| **CREATES**               | Training results and optional metrics and visualizations.                                                                                                                 |

## package {#package tag="command"}

Generate an installable
[model Python package](/usage/training#models-generating) from an existing model
data directory. All data files are copied over. If the path to a
[`meta.json`](/api/data-formats#meta) is supplied, or a `meta.json` is found in
the input directory, this file is used. Otherwise, the data can be entered
directly from the command line. spaCy will then create a `.tar.gz` archive file
that you can distribute and install with `pip install`.

<Infobox title="New in v3.0" variant="warning">

The `spacy package` command now also builds the `.tar.gz` archive automatically,
so you don't have to run `python setup.py sdist` separately anymore. To disable
this, you can set the `--no-sdist` flag.

</Infobox>

```cli
$ python -m spacy package [input_dir] [output_dir] [--meta-path] [--create-meta] [--no-sdist] [--version] [--force]
```

> #### Example
>
> ```cli
> $ python -m spacy package /input /output
> $ cd /output/en_model-0.0.0
> $ pip install dist/en_model-0.0.0.tar.gz
> ```

| Name                                             | Description                                                                                                                                                                                                     |
| ------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `input_dir`                                      | Path to directory containing model data. ~~Path (positional)~~                                                                                                                                                  |
| `output_dir`                                     | Directory to create package folder in. ~~Path (positional)~~                                                                                                                                                    |
| `--meta-path`, `-m` <Tag variant="new">2</Tag>   | Path to [`meta.json`](/api/data-formats#meta) file (optional). ~~Optional[Path] \(option)~~                                                                                                                     |
| `--create-meta`, `-C` <Tag variant="new">2</Tag> | Create a `meta.json` file on the command line, even if one already exists in the directory. If an existing file is found, its entries will be shown as the defaults in the command line prompt. ~~bool (flag)~~ |
| `--no-sdist`, `-NS`,                             | Don't build the `.tar.gz` sdist automatically. Can be set if you want to run this step manually. ~~bool (flag)~~                                                                                                |
| `--version`, `-v` <Tag variant="new">3</Tag>     | Package version to override in meta. Useful when training new versions, as it doesn't require editing the meta template. ~~Optional[str] \(option)~~                                                            |
| `--force`, `-f`                                  | Force overwriting of existing folder in output directory. ~~bool (flag)~~                                                                                                                                       |
| `--help`, `-h`                                   | Show help message and available arguments. ~~bool (flag)~~                                                                                                                                                      |
| **CREATES**                                      | A Python package containing the spaCy model.                                                                                                                                                                    |

## project {#project new="3"}

The `spacy project` CLI includes subcommands for working with
[spaCy projects](/usage/projects), end-to-end workflows for building and
deploying custom spaCy models.

### project clone {#project-clone tag="command"}

Clone a project template from a Git repository. Calls into `git` under the hood
and uses the sparse checkout feature, so you're only downloading what you need.
By default, spaCy's
[project templates repo](https://github.com/explosion/projects) is used, but you
can provide any other repo (public or private) that you have access to using the
`--repo` option.

<!-- TODO: update example once we've decided on repo structure -->

```cli
$ python -m spacy project clone [name] [dest] [--repo]
```

> #### Example
>
> ```cli
> $ python -m spacy project clone some_example
> ```
>
> Clone from custom repo:
>
> ```cli
> $ python -m spacy project clone template --repo https://github.com/your_org/your_repo
> ```

| Name           | Description                                                                                                                                       |
| -------------- | ------------------------------------------------------------------------------------------------------------------------------------------------- |
| `name`         | The name of the template to clone, relative to the repo. Can be a top-level directory or a subdirectory like `dir/template`. ~~str (positional)~~ |
| `dest`         | Where to clone the project. Defaults to current working directory. ~~Path (positional)~~                                                          |
| `--repo`, `-r` | The repository to clone from. Can be any public or private Git repo you have access to. ~~str (option)~~                                          |
| `--help`, `-h` | Show help message and available arguments. ~~bool (flag)~~                                                                                        |
| **CREATES**    | The cloned [project directory](/usage/projects#project-files).                                                                                    |

### project assets {#project-assets tag="command"}

Fetch project assets like datasets and pretrained weights. Assets are defined in
the `assets` section of the [`project.yml`](/usage/projects#project-yml). If a
`checksum` is provided, the file is only downloaded if no local file with the
same checksum exists and spaCy will show an error if the checksum of the
downloaded file doesn't match. If assets don't specify a `url` they're
considered "private" and you have to take care of putting them into the
destination directory yourself. If a local path is provided, the asset is copied
into the current project.

```cli
$ python -m spacy project assets [project_dir]
```

> #### Example
>
> ```cli
> $ python -m spacy project assets
> ```

| Name           | Description                                                                             |
| -------------- | --------------------------------------------------------------------------------------- |
| `project_dir`  | Path to project directory. Defaults to current working directory. ~~Path (positional)~~ |
| `--help`, `-h` | Show help message and available arguments. ~~bool (flag)~~                              |
| **CREATES**    | Downloaded or copied assets defined in the `project.yml`.                               |

### project run {#project-run tag="command"}

Run a named command or workflow defined in the
[`project.yml`](/usage/projects#project-yml). If a workflow name is specified,
all commands in the workflow are run, in order. If commands define
[dependencies or outputs](/usage/projects#deps-outputs), they will only be
re-run if state has changed. For example, if the input dataset changes, a
preprocessing command that depends on those files will be re-run.

```cli
$ python -m spacy project run [subcommand] [project_dir] [--force] [--dry]
```

> #### Example
>
> ```cli
> $ python -m spacy project run train
> ```

| Name            | Description                                                                             |
| --------------- | --------------------------------------------------------------------------------------- |
| `subcommand`    | Name of the command or workflow to run. ~~str (positional)~~                            |
| `project_dir`   | Path to project directory. Defaults to current working directory. ~~Path (positional)~~ |
| `--force`, `-F` | Force re-running steps, even if nothing changed. ~~bool (flag)~~                        |
| `--dry`, `-D`   |  Perform a dry run and don't execute scripts. ~~bool (flag)~~                           |
| `--help`, `-h`  | Show help message and available arguments. ~~bool (flag)~~                              |
| **EXECUTES**    | The command defined in the `project.yml`.                                               |

### project push {#project-push tag="command"}

Upload all available files or directories listed as in the `outputs` section of
commands to a remote storage. Outputs are archived and compressed prior to
upload, and addressed in the remote storage using the output's relative path
(URL encoded), a hash of its command string and dependencies, and a hash of its
file contents. This means `push` should **never overwrite** a file in your
remote. If all the hashes match, the contents are the same and nothing happens.
If the contents are different, the new version of the file is uploaded. Deleting
obsolete files is left up to you.

Remotes can be defined in the `remotes` section of the
[`project.yml`](/usage/projects#project-yml). Under the hood, spaCy uses the
[`smart-open`](https://github.com/RaRe-Technologies/smart_open) library to
communicate with the remote storages, so you can use any protocol that
`smart-open` supports, including [S3](https://aws.amazon.com/s3/),
[Google Cloud Storage](https://cloud.google.com/storage), SSH and more, although
you may need to install extra dependencies to use certain protocols.

```cli
$ python -m spacy project push [remote] [project_dir]
```

> #### Example
>
> ```cli
> $ python -m spacy project push my_bucket
> ```
>
> ```yaml
> ### project.yml
> remotes:
>   my_bucket: 's3://my-spacy-bucket'
> ```

| Name           | Description                                                                             |
| -------------- | --------------------------------------------------------------------------------------- |
| `remote`       | The name of the remote to upload to. Defaults to `"default"`. ~~str (positional)~~      |
| `project_dir`  | Path to project directory. Defaults to current working directory. ~~Path (positional)~~ |
| `--help`, `-h` | Show help message and available arguments. ~~bool (flag)~~                              |
| **UPLOADS**    | All project outputs that exist and are not already stored in the remote.                |

### project pull {#project-pull tag="command"}

Download all files or directories listed as `outputs` for commands, unless they
are not already present locally. When searching for files in the remote, `pull`
won't just look at the output path, but will also consider the **command
string** and the **hashes of the dependencies**. For instance, let's say you've
previously pushed a model checkpoint to the remote, but now you've changed some
hyper-parameters. Because you've changed the inputs to the command, if you run
`pull`, you won't retrieve the stale result. If you train your model and push
the outputs to the remote, the outputs will be saved alongside the prior
outputs, so if you change the config back, you'll be able to fetch back the
result.

Remotes can be defined in the `remotes` section of the
[`project.yml`](/usage/projects#project-yml). Under the hood, spaCy uses the
[`smart-open`](https://github.com/RaRe-Technologies/smart_open) library to
communicate with the remote storages, so you can use any protocol that
`smart-open` supports, including [S3](https://aws.amazon.com/s3/),
[Google Cloud Storage](https://cloud.google.com/storage), SSH and more, although
you may need to install extra dependencies to use certain protocols.

```cli
$ python -m spacy project pull [remote] [project_dir]
```

> #### Example
>
> ```cli
> $ python -m spacy project pull my_bucket
> ```
>
> ```yaml
> ### project.yml
> remotes:
>   my_bucket: 's3://my-spacy-bucket'
> ```

| Name           | Description                                                                             |
| -------------- | --------------------------------------------------------------------------------------- |
| `remote`       | The name of the remote to download from. Defaults to `"default"`. ~~str (positional)~~  |
| `project_dir`  | Path to project directory. Defaults to current working directory. ~~Path (positional)~~ |
| `--help`, `-h` | Show help message and available arguments. ~~bool (flag)~~                              |
| **DOWNLOADS**  | All project outputs that do not exist locally and can be found in the remote.           |

### project dvc {#project-dvc tag="command"}

Auto-generate [Data Version Control](https://dvc.org) (DVC) config file. Calls
[`dvc run`](https://dvc.org/doc/command-reference/run) with `--no-exec` under
the hood to generate the `dvc.yaml`. A DVC project can only define one pipeline,
so you need to specify one workflow defined in the
[`project.yml`](/usage/projects#project-yml). If no workflow is specified, the
first defined workflow is used. The DVC config will only be updated if the
`project.yml` changed. For details, see the
[DVC integration](/usage/projects#dvc) docs.

<Infobox variant="warning">

This command requires DVC to be installed and initialized in the project
directory, e.g. via [`dvc init`](https://dvc.org/doc/command-reference/init).
You'll also need to add the assets you want to track with
[`dvc add`](https://dvc.org/doc/command-reference/add).

</Infobox>

```cli
$ python -m spacy project dvc [project_dir] [workflow] [--force] [--verbose]
```

> #### Example
>
> ```cli
> $ git init
> $ dvc init
> $ python -m spacy project dvc all
> ```

| Name              | Description                                                                                                       |
| ----------------- | ----------------------------------------------------------------------------------------------------------------- |
| `project_dir`     | Path to project directory. Defaults to current working directory. ~~Path (positional)~~                           |
| `workflow`        | Name of workflow defined in `project.yml`. Defaults to first workflow if not set. ~~Optional[str] \(positional)~~ |
| `--force`, `-F`   | Force-updating config file. ~~bool (flag)~~                                                                       |
| `--verbose`, `-V` |  Print more output generated by DVC. ~~bool (flag)~~                                                              |
| `--help`, `-h`    | Show help message and available arguments. ~~bool (flag)~~                                                        |
| **CREATES**       | A `dvc.yaml` file in the project directory, based on the steps defined in the given workflow.                     |
