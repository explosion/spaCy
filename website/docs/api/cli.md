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
  - ['Debug data', 'debug-data']
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
best-matching compatible version, uses `pip install` to download the model as a
package and creates a [shortcut link](/usage/models#usage) if the model was
downloaded via a shortcut. Direct downloads don't perform any compatibility
checks and require the model name to be specified with its version (e.g.
`en_core_web_sm-2.2.0`).

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
$ python -m spacy download [model] [--direct] [pip args]
```

| Argument                              | Type               | Description                                                                                                                                                                                                    |
| ------------------------------------- | ------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `model`                               | positional         | Model name or shortcut (`en`, `de`, `en_core_web_sm`).                                                                                                                                                         |
| `--direct`, `-d`                      | flag               | Force direct download of exact model version.                                                                                                                                                                  |
| pip args <Tag variant="new">2.1</Tag> | -                  | Additional installation options to be passed to `pip install` when installing the model package. For example, `--user` to install to the user home directory or `--no-deps` to not install model dependencies. |
| `--help`, `-h`                        | flag               | Show help message and available arguments.                                                                                                                                                                     |
| **CREATES**                           | directory, symlink | The installed model package in your `site-packages` directory and a shortcut link as a symlink in `spacy/data` if installed via shortcut.                                                                      |

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
$ python -m spacy info [--markdown] [--silent]
```

```bash
$ python -m spacy info [model] [--markdown] [--silent]
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
created in different virtual environments. It will show a list of models and
their installed versions. If any model is out of date, the latest compatible
versions and command for updating are shown.

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
| `--seg-sents`, `-s` <Tag variant="new">2.2</Tag> | flag       | Segment sentences (for `-c ner`)                                                                  |
| `--model`, `-b` <Tag variant="new">2.2</Tag>     | option     | Model for parser-based sentence segmentation (for `-s`)                                           |
| `--morphology`, `-m`                             | option     | Enable appending morphology to tags.                                                              |
| `--lang`, `-l` <Tag variant="new">2.1</Tag>      | option     | Language code (if tokenizer required).                                                            |
| `--help`, `-h`                                   | flag       | Show help message and available arguments.                                                        |
| **CREATES**                                      | JSON       | Data in spaCy's [JSON format](/api/annotation#json-input).                                        |

### Output file types {new="2.1"}

All output files generated by this command are compatible with
[`spacy train`](/api/cli#train).

| ID      | Description                |
| ------- | -------------------------- |
| `json`  | Regular JSON (default).    |
| `jsonl` | Newline-delimited JSON.    |
| `msg`   | Binary MessagePack format. |

### Converter options

| ID                             | Description                                                                                                                                                                                                                                                                                                                                                                                    |
| ------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `auto`                         | Automatically pick converter based on file extension and file content (default).                                                                                                                                                                                                                                                                                                               |
| `conll`, `conllu`, `conllubio` | Universal Dependencies `.conllu` or `.conll` format.                                                                                                                                                                                                                                                                                                                                           |
| `ner`                          | NER with IOB/IOB2 tags, one token per line with columns separated by whitespace. The first column is the token and the final column is the IOB tag. Sentences are separated by blank lines and documents are separated by the line `-DOCSTART- -X- O O`. Supports CoNLL 2003 NER format. See [sample data](https://github.com/explosion/spaCy/tree/master/examples/training/ner_example_data). |
| `iob`                          | NER with IOB/IOB2 tags, one sentence per line with tokens separated by whitespace and annotation separated by `|`, either `word|B-ENT` or `word|POS|B-ENT`. See [sample data](https://github.com/explosion/spaCy/tree/master/examples/training/ner_example_data).                                                                                                                              |
| `jsonl`                        | NER data formatted as JSONL with one dict per line and a `"text"` and `"spans"` key. This is also the format exported by the [Prodigy](https://prodi.gy) annotation tool. See [sample data](https://raw.githubusercontent.com/explosion/projects/master/ner-fashion-brands/fashion_brands_training.jsonl).                                                                                     |

## Debug data {#debug-data new="2.2"}

Analyze, debug, and validate your training and development data. Get useful
stats, and find problems like invalid entity annotations, cyclic dependencies,
low data labels and more.

```bash
$ python -m spacy debug-data [lang] [train_path] [dev_path] [--base-model] [--pipeline] [--ignore-warnings] [--verbose] [--no-format]
```

| Argument                                               | Type       | Description                                                                                        |
| ------------------------------------------------------ | ---------- | -------------------------------------------------------------------------------------------------- |
| `lang`                                                 | positional | Model language.                                                                                    |
| `train_path`                                           | positional | Location of JSON-formatted training data. Can be a file or a directory of files.                   |
| `dev_path`                                             | positional | Location of JSON-formatted development data for evaluation. Can be a file or a directory of files. |
| `--tag-map-path`, `-tm` <Tag variant="new">2.2.4</Tag> | option     | Location of JSON-formatted tag map.                                                                |
| `--base-model`, `-b`                                   | option     | Optional name of base model to update. Can be any loadable spaCy model.                            |
| `--pipeline`, `-p`                                     | option     | Comma-separated names of pipeline components to train. Defaults to `'tagger,parser,ner'`.          |
| `--ignore-warnings`, `-IW`                             | flag       | Ignore warnings, only show stats and errors.                                                       |
| `--verbose`, `-V`                                      | flag       | Print additional information and explanations.                                                     |
| --no-format, `-NF`                                     | flag       | Don't pretty-print the results. Use this if you want to write to a file.                           |

<Accordion title="Example output">

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
[--base-model] [--pipeline] [--vectors] [--n-iter] [--n-early-stopping]
[--n-examples] [--use-gpu] [--version] [--meta-path] [--init-tok2vec]
[--parser-multitasks] [--entity-multitasks] [--gold-preproc] [--noise-level]
[--orth-variant-level] [--learn-tokens] [--textcat-arch] [--textcat-multilabel]
[--textcat-positive-label] [--verbose]
```

| Argument                                                        | Type          | Description                                                                                                                                                       |
| --------------------------------------------------------------- | ------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `lang`                                                          | positional    | Model language.                                                                                                                                                   |
| `output_path`                                                   | positional    | Directory to store model in. Will be created if it doesn't exist.                                                                                                 |
| `train_path`                                                    | positional    | Location of JSON-formatted training data. Can be a file or a directory of files.                                                                                  |
| `dev_path`                                                      | positional    | Location of JSON-formatted development data for evaluation. Can be a file or a directory of files.                                                                |
| `--base-model`, `-b` <Tag variant="new">2.1</Tag>               | option        | Optional name of base model to update. Can be any loadable spaCy model.                                                                                           |
| `--pipeline`, `-p` <Tag variant="new">2.1</Tag>                 | option        | Comma-separated names of pipeline components to train. Defaults to `'tagger,parser,ner'`.                                                                         |
| `--replace-components`, `-R`                                    | flag          | Replace components from the base model.                                                                                                                           |
| `--vectors`, `-v`                                               | option        | Model to load vectors from.                                                                                                                                       |
| `--n-iter`, `-n`                                                | option        | Number of iterations (default: `30`).                                                                                                                             |
| `--n-early-stopping`, `-ne`                                     | option        | Maximum number of training epochs without dev accuracy improvement.                                                                                               |
| `--n-examples`, `-ns`                                           | option        | Number of examples to use (defaults to `0` for all examples).                                                                                                     |
| `--use-gpu`, `-g`                                               | option        | GPU ID or `-1` for CPU only (default: `-1`).                                                                                                                      |
| `--version`, `-V`                                               | option        | Model version. Will be written out to the model's `meta.json` after training.                                                                                     |
| `--meta-path`, `-m` <Tag variant="new">2</Tag>                  | option        | Optional path to model [`meta.json`](/usage/training#models-generating). All relevant properties like `lang`, `pipeline` and `spacy_version` will be overwritten. |
| `--init-tok2vec`, `-t2v` <Tag variant="new">2.1</Tag>           | option        | Path to pretrained weights for the token-to-vector parts of the models. See `spacy pretrain`. Experimental.                                                       |
| `--parser-multitasks`, `-pt`                                    | option        | Side objectives for parser CNN, e.g. `'dep'` or `'dep,tag'`                                                                                                       |
| `--entity-multitasks`, `-et`                                    | option        | Side objectives for NER CNN, e.g. `'dep'` or `'dep,tag'`                                                                                                          |
| `--width`, `-cw` <Tag variant="new">2.2.4</Tag>                 | option        | Width of CNN layers of `Tok2Vec` component.                                                                                                                       |
| `--conv-depth`, `-cd` <Tag variant="new">2.2.4</Tag>            | option        | Depth of CNN layers of `Tok2Vec` component.                                                                                                                       |
| `--cnn-window`, `-cW` <Tag variant="new">2.2.4</Tag>            | option        | Window size for CNN layers of `Tok2Vec` component.                                                                                                                |
| `--cnn-pieces`, `-cP` <Tag variant="new">2.2.4</Tag>            | option        | Maxout size for CNN layers of `Tok2Vec` component.                                                                                                                |
| `--use-chars`, `-chr` <Tag variant="new">2.2.4</Tag>            | flag          | Whether to use character-based embedding of `Tok2Vec` component.                                                                                                  |
| `--bilstm-depth`, `-lstm` <Tag variant="new">2.2.4</Tag>        | option        | Depth of BiLSTM layers of `Tok2Vec` component (requires PyTorch).                                                                                                 |
| `--embed-rows`, `-er` <Tag variant="new">2.2.4</Tag>            | option        | Number of embedding rows of `Tok2Vec` component.                                                                                                                  |
| `--noise-level`, `-nl`                                          | option        | Float indicating the amount of corruption for data augmentation.                                                                                                  |
| `--orth-variant-level`, `-ovl` <Tag variant="new">2.2</Tag>     | option        | Float indicating the orthography variation for data augmentation (e.g. `0.3` for making 30% of occurrences of some tokens subject to replacement).                |
| `--gold-preproc`, `-G`                                          | flag          | Use gold preprocessing.                                                                                                                                           |
| `--learn-tokens`, `-T`                                          | flag          | Make parser learn gold-standard tokenization by merging ] subtokens. Typically used for languages like Chinese.                                                   |
| `--textcat-multilabel`, `-TML` <Tag variant="new">2.2</Tag>     | flag          | Text classification classes aren't mutually exclusive (multilabel).                                                                                               |
| `--textcat-arch`, `-ta` <Tag variant="new">2.2</Tag>            | option        | Text classification model architecture. Defaults to `"bow"`.                                                                                                      |
| `--textcat-positive-label`, `-tpl` <Tag variant="new">2.2</Tag> | option        | Text classification positive label for binary classes with two labels.                                                                                            |
| `--tag-map-path`, `-tm` <Tag variant="new">2.2.4</Tag>          | option        | Location of JSON-formatted tag map.                                                                                                                               |
| `--verbose`, `-VV` <Tag variant="new">2.0.13</Tag>              | flag          | Show more detailed messages during training.                                                                                                                      |
| `--help`, `-h`                                                  | flag          | Show help message and available arguments.                                                                                                                        |
| **CREATES**                                                     | model, pickle | A spaCy model on each epoch.                                                                                                                                      |

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
an approximate language-modeling objective. Specifically, we load pretrained
vectors, and train a component like a CNN, BiLSTM, etc to predict vectors which
match the pretrained ones. The weights are saved to a directory after each
epoch. You can then pass a path to one of these pretrained weights files to the
`spacy train` command.

This technique may be especially helpful if you have little labelled data.
However, it's still quite experimental, so your mileage may vary. To load the
weights back in during `spacy train`, you need to ensure all settings are the
same between pretraining and training. The API and errors around this need some
improvement.

```bash
$ python -m spacy pretrain [texts_loc] [vectors_model] [output_dir]
[--width] [--depth] [--cnn-window] [--cnn-pieces] [--use-chars] [--sa-depth]
[--embed-rows] [--loss_func] [--dropout] [--batch-size] [--max-length]
[--min-length]  [--seed] [--n-iter] [--use-vectors] [--n-save-every]
[--init-tok2vec] [--epoch-start]
```

| Argument                                              | Type       | Description                                                                                                                                                                     |
| ----------------------------------------------------- | ---------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `texts_loc`                                           | positional | Path to JSONL file with raw texts to learn from, with text provided as the key `"text"` or tokens as the key `"tokens"`. [See here](#pretrain-jsonl) for details.               |
| `vectors_model`                                       | positional | Name or path to spaCy model with vectors to learn from.                                                                                                                         |
| `output_dir`                                          | positional | Directory to write models to on each epoch.                                                                                                                                     |
| `--width`, `-cw`                                      | option     | Width of CNN layers.                                                                                                                                                            |
| `--depth`, `-cd`                                      | option     | Depth of CNN layers.                                                                                                                                                            |
| `--cnn-window`, `-cW` <Tag variant="new">2.2.2</Tag>  | option     | Window size for CNN layers.                                                                                                                                                     |
| `--cnn-pieces`, `-cP` <Tag variant="new">2.2.2</Tag>  | option     | Maxout size for CNN layers. `1` for [Mish](https://github.com/digantamisra98/Mish).                                                                                             |
| `--use-chars`, `-chr` <Tag variant="new">2.2.2</Tag>  | flag       | Whether to use character-based embedding.                                                                                                                                       |
| `--sa-depth`, `-sa` <Tag variant="new">2.2.2</Tag>    | option     | Depth of self-attention layers.                                                                                                                                                 |
| `--embed-rows`, `-er`                                 | option     | Number of embedding rows.                                                                                                                                                       |
| `--loss-func`, `-L`                                   | option     | Loss function to use for the objective. Either `"L2"` or `"cosine"`.                                                                                                            |
| `--dropout`, `-d`                                     | option     | Dropout rate.                                                                                                                                                                   |
| `--batch-size`, `-bs`                                 | option     | Number of words per training batch.                                                                                                                                             |
| `--max-length`, `-xw`                                 | option     | Maximum words per example. Longer examples are discarded.                                                                                                                       |
| `--min-length`, `-nw`                                 | option     | Minimum words per example. Shorter examples are discarded.                                                                                                                      |
| `--seed`, `-s`                                        | option     | Seed for random number generators.                                                                                                                                              |
| `--n-iter`, `-i`                                      | option     | Number of iterations to pretrain.                                                                                                                                               |
| `--use-vectors`, `-uv`                                | flag       | Whether to use the static vectors as input features.                                                                                                                            |
| `--n-save-every`, `-se`                               | option     | Save model every X batches.                                                                                                                                                     |
| `--init-tok2vec`, `-t2v` <Tag variant="new">2.1</Tag> | option     | Path to pretrained weights for the token-to-vector parts of the models. See `spacy pretrain`. Experimental.                                                                     |
| `--epoch-start`, `-es` <Tag variant="new">2.1.5</Tag> | option     | The epoch to start counting at. Only relevant when using `--init-tok2vec` and the given weight file has been renamed. Prevents unintended overwriting of existing weight files. |
| **CREATES**                                           | weights    | The pretrained weights that can be used to initialize `spacy train`.                                                                                                            |

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

| Key      | Type    | Description                                                |
| -------- | ------- | ---------------------------------------------------------- |
| `text`   | unicode | The raw input text. Is not required if `tokens` available. |
| `tokens` | list    | Optional tokenization, one string per token.               |

```json
### Example
{"text": "Can I ask where you work now and what you do, and if you enjoy it?"}
{"text": "They may just pull out of the Seattle market completely, at least until they have autonomous vehicles."}
{"text": "My cynical view on this is that it will never be free to the public. Reason: what would be the draw of joining the military? Right now their selling point is free Healthcare and Education. Ironically both are run horribly and most, that I've talked to, come out wishing they never went in."}
{"tokens": ["If", "tokens", "are", "provided", "then", "we", "can", "skip", "the", "raw", "input", "text"]}
```

## Init Model {#init-model new="2"}

Create a new model directory from raw data, like word frequencies, Brown
clusters and word vectors. This command is similar to the `spacy model` command
in v1.x. Note that in order to populate the model's vocab, you need to pass in a
JSONL-formatted [vocabulary file](<(/api/annotation#vocab-jsonl)>) as
`--jsonl-loc` with optional `id` values that correspond to the vectors table.
Just loading in vectors will not automatically populate the vocab.

<Infobox title="Deprecation note" variant="warning">

As of v2.1.0, the `--freqs-loc` and `--clusters-loc` are deprecated and have
been replaced with the `--jsonl-loc` argument, which lets you pass in a a
[JSONL](http://jsonlines.org/) file containing one lexical entry per line. For
more details on the format, see the
[annotation specs](/api/annotation#vocab-jsonl).

</Infobox>

```bash
$ python -m spacy init-model [lang] [output_dir] [--jsonl-loc] [--vectors-loc]
[--prune-vectors]
```

| Argument                | Type       | Description                                                                                                                                                                                                                                            |
| ----------------------- | ---------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `lang`                  | positional | Model language [ISO code](https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes), e.g. `en`.                                                                                                                                                           |
| `output_dir`            | positional | Model output directory. Will be created if it doesn't exist.                                                                                                                                                                                           |
| `--jsonl-loc`, `-j`     | option     | Optional location of JSONL-formatted [vocabulary file](/api/annotation#vocab-jsonl) with lexical attributes.                                                                                                                                           |
| `--vectors-loc`, `-v`   | option     | Optional location of vectors. Should be a file where the first row contains the dimensions of the vectors, followed by a space-separated Word2Vec table. File can be provided in `.txt` format or as a zipped text file in `.zip` or `.tar.gz` format. |
| `--truncate-vectors`, `-t` | option  | Number of vectors to truncate to when reading in vectors file. Defaults to `0` for no truncation.                                                                                                                                                      |
| `--prune-vectors`, `-V` | option     | Number of vectors to prune the vocabulary to. Defaults to `-1` for no pruning.                                                                                                                                                                         |
| `--vectors-name`, `-vn` | option     | Name to assign to the word vectors in the `meta.json`, e.g. `en_core_web_md.vectors`.                                                                                                                                                                  |
| **CREATES**             | model      | A spaCy model containing the vocab and vectors.                                                                                                                                                                                                        |

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
| `--create-meta`, `-c` <Tag variant="new">2</Tag> | flag       | Create a `meta.json` file on the command line, even if one already exists in the directory. If an existing file is found, its entries will be shown as the defaults in the command line prompt. |
| `--force`, `-f`                                  | flag       | Force overwriting of existing folder in output directory.                                                                                                                                       |
| `--help`, `-h`                                   | flag       | Show help message and available arguments.                                                                                                                                                      |
| **CREATES**                                      | directory  | A Python package containing the spaCy model.                                                                                                                                                    |
