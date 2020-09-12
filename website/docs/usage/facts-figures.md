---
title: Facts & Figures
teaser: The hard numbers for spaCy and how it compares to other tools
next: /usage/spacy-101
menu:
  - ['Feature Comparison', 'comparison']
  - ['Benchmarks', 'benchmarks']
  # TODO: - ['Citing spaCy', 'citation']
---

## Comparison {#comparison hidden="true"}

### When should I use spaCy? {#comparison-usage}

<!-- TODO: update -->

| Use Cases                                                                                                                                                                                                                                                                                                  |
| ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| ✅ **I'm a beginner and just getting started with NLP.**<br />spaCy makes it easy to get started and comes with extensive documentation, including a beginner-friendly [101 guide](/usage/spacy-101) and a free interactive [online course](https://course.spacy.io).                                      |
| ✅ **I want to build an end-to-end production application.**                                                                                                                                                                                                                                               |
| ✅ **I want my application to be efficient on CPU.**<br />While spaCy lets you train modern NLP models that are best run on GPU, it also offers CPU-optimized pipelines, which may be less accurate but much cheaper to run.                                                                               |
| ✅ **I want to try out different neural network architectures for NLP.**                                                                                                                                                                                                                                   |
| ❌ **I want to build a language generation application.**<br />spaCy's focus is natural language _processing_ and extracting information from large volumes of text. While you can use it to help you re-write existing text, it doesn't include any specific functionality for language generation tasks. |
| ❌ **I want to research machine learning algorithms.**                                                                                                                                                                                                                                                     |

## Benchmarks {#benchmarks}

spaCy v3.0 introduces transformer-based pipelines that bring spaCy's accuracy
right up to **current state-of-the-art**. You can also use a CPU-optimized
pipeline, which is less accurate but much cheaper to run.

<!-- TODO: -->

> #### Evaluation details
>
> - **OntoNotes 5.0:** spaCy's English models are trained on this corpus, as
>   it's several times larger than other English treebanks. However, most
>   systems do not report accuracies on it.
> - **Penn Treebank:** The "classic" parsing evaluation for research. However,
>   it's quite far removed from actual usage: it uses sentences with
>   gold-standard segmentation and tokenization, from a pretty specific type of
>   text (articles from a single newspaper, 1984-1989).

import Benchmarks from 'usage/\_benchmarks-models.md'

<Benchmarks />

<!-- TODO: update -->

<Project id="benchmarks/penn_treebank">

The easiest way to reproduce spaCy's benchmarks on the Penn Treebank is to clone
our project template.

</Project>

<!-- ## Citing spaCy {#citation}

<!-- TODO: update -->
