---
title: Trained Models & Pipelines
teaser: Downloadable trained pipelines and weights for spaCy
menu:
  - ['Quickstart', 'quickstart']
  - ['Conventions', 'conventions']
---

<!-- TODO: include interactive demo -->

### Quickstart {hidden="true"}

> #### 📖 Installation and usage
>
> For more details on how to use trained pipelines with spaCy, see the
> [usage guide](/usage/models).

import QuickstartModels from 'widgets/quickstart-models.js'

<QuickstartModels id="quickstart" />

## Package naming conventions {#conventions}

In general, spaCy expects all pipeline packages to follow the naming convention
of `[lang]\_[name]`. For spaCy's pipelines, we also chose to divide the name
into three components:

1. **Type:** Capabilities (e.g. `core` for general-purpose pipeline with
   vocabulary, syntax, entities and word vectors, or `dep` for only vocab and
   syntax).
2. **Genre:** Type of text the pipeline is trained on, e.g. `web` or `news`.
3. **Size:** Package size indicator, `sm`, `md` or `lg`.

For example, [`en_core_web_sm`](/models/en#en_core_web_sm) is a small English
pipeline trained on written web text (blogs, news, comments), that includes
vocabulary, vectors, syntax and entities.

### Package versioning {#model-versioning}

Additionally, the pipeline package versioning reflects both the compatibility
with spaCy, as well as the major and minor version. A package version `a.b.c`
translates to:

- `a`: **spaCy major version**. For example, `2` for spaCy v2.x.
- `b`: **Package major version**. Pipelines with a different major version can't
  be loaded by the same code. For example, changing the width of the model,
  adding hidden layers or changing the activation changes the major version.
- `c`: **Package minor version**. Same pipeline structure, but different
  parameter values, e.g. from being trained on different data, for different
  numbers of iterations, etc.

For a detailed compatibility overview, see the
[`compatibility.json`](https://github.com/explosion/spacy-models/tree/master/compatibility.json).
This is also the source of spaCy's internal compatibility check, performed when
you run the [`download`](/api/cli#download) command.
