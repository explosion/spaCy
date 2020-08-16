---
title: Models
teaser: Downloadable pretrained models for spaCy
menu:
  - ['Quickstart', 'quickstart']
  - ['Conventions', 'conventions']
---

<!-- Update page, refer to new /api/architectures and training docs -->

The models directory includes two types of pretrained models:

1. **Core models:** General-purpose pretrained models to predict named entities,
   part-of-speech tags and syntactic dependencies. Can be used out-of-the-box
   and fine-tuned on more specific data.
2. **Starter models:** Transfer learning starter packs with pretrained weights
   you can initialize your models with to achieve better accuracy. They can
   include word vectors (which will be used as features during training) or
   other pretrained representations like BERT. These models don't include
   components for specific tasks like NER or text classification and are
   intended to be used as base models when training your own models.

### Quickstart {hidden="true"}

import QuickstartModels from 'widgets/quickstart-models.js'

<QuickstartModels title="Quickstart" id="quickstart" description="Install a default model, get the code to load it from within spaCy and test it." />

<Infobox title="Installation and usage" emoji="📖">

For more details on how to use models with spaCy, see the
[usage guide on models](/usage/models).

</Infobox>

## Model naming conventions {#conventions}

In general, spaCy expects all model packages to follow the naming convention of
`[lang`\_[name]]. For spaCy's models, we also chose to divide the name into
three components:

1. **Type:** Model capabilities (e.g. `core` for general-purpose model with
   vocabulary, syntax, entities and word vectors, or `depent` for only vocab,
   syntax and entities).
2. **Genre:** Type of text the model is trained on, e.g. `web` or `news`.
3. **Size:** Model size indicator, `sm`, `md` or `lg`.

For example, [`en_core_web_sm`](/models/en#en_core_web_sm) is a small English
model trained on written web text (blogs, news, comments), that includes
vocabulary, vectors, syntax and entities.

### Model versioning {#model-versioning}

Additionally, the model versioning reflects both the compatibility with spaCy,
as well as the major and minor model version. A model version `a.b.c` translates
to:

- `a`: **spaCy major version**. For example, `2` for spaCy v2.x.
- `b`: **Model major version**. Models with a different major version can't be
  loaded by the same code. For example, changing the width of the model, adding
  hidden layers or changing the activation changes the model major version.
- `c`: **Model minor version**. Same model structure, but different parameter
  values, e.g. from being trained on different data, for different numbers of
  iterations, etc.

For a detailed compatibility overview, see the
[`compatibility.json`](https://github.com/explosion/spacy-models/tree/master/compatibility.json)
in the models repository. This is also the source of spaCy's internal
compatibility check, performed when you run the [`download`](/api/cli#download)
command.
