---
title: Facts & Figures
teaser: The hard numbers for spaCy and how it compares to other tools
next: /usage/spacy-101
menu:
  - ['Feature Comparison', 'comparison']
  - ['Benchmarks', 'benchmarks']
  - ['Powered by spaCy', 'powered-by']
  - ['Other Libraries', 'other-libraries']
---

## Feature comparison {#comparison}

Here's a quick comparison of the functionalities offered by spaCy,
[NLTK](http://www.nltk.org/py-modindex.html) and
[CoreNLP](http://stanfordnlp.github.io/CoreNLP/).

|                         | spaCy  |  NLTK  |    CoreNLP    |
| ----------------------- | :----: | :----: | :-----------: |
| Programming language    | Python | Python | Java / Python |
| Neural network models   |   ✅   |   ❌   |      ✅       |
| Integrated word vectors |   ✅   |   ❌   |      ❌       |
| Multi-language support  |   ✅   |   ✅   |      ✅       |
| Tokenization            |   ✅   |   ✅   |      ✅       |
| Part-of-speech tagging  |   ✅   |   ✅   |      ✅       |
| Sentence segmentation   |   ✅   |   ✅   |      ✅       |
| Dependency parsing      |   ✅   |   ❌   |      ✅       |
| Entity recognition      |   ✅   |   ✅   |      ✅       |
| Entity linking          |   ❌   |   ❌   |      ❌       |
| Coreference resolution  |   ❌   |   ❌   |      ✅       |

### When should I use what? {#comparison-usage}

Natural Language Understanding is an active area of research and development, so
there are many different tools or technologies catering to different use-cases.
The table below summarizes a few libraries (spaCy,
[NLTK](http://www.nltk.org/py-modindex.html), [AllenNLP](https://allennlp.org/),
[StanfordNLP](https://stanfordnlp.github.io/stanfordnlp/) and
[TensorFlow](https://www.tensorflow.org/)) to help you get a feel for things fit
together.

|                                                                   | spaCy | NLTK | Allen-<br />NLP | Stanford-<br />NLP | Tensor-<br />Flow |
| ----------------------------------------------------------------- | :---: | :--: | :-------------: | :----------------: | :---------------: |
| I'm a beginner and just getting started with NLP.                 |  ✅   |  ✅  |       ❌        |         ✅         |        ❌         |
| I want to build an end-to-end production application.             |  ✅   |  ❌  |       ❌        |         ❌         |        ✅         |
| I want to try out different neural network architectures for NLP. |  ❌   |  ❌  |       ✅        |         ❌         |        ✅         |
| I want to try the latest models with state-of-the-art accuracy.   |  ❌   |  ❌  |       ✅        |         ✅         |        ✅         |
| I want to train models from my own data.                          |  ✅   |  ✅  |       ✅        |         ✅         |        ✅         |
| I want my application to be efficient on CPU.                     |  ✅   |  ✅  |       ❌        |         ❌         |        ❌         |

## Benchmarks {#benchmarks}

Two peer-reviewed papers in 2015 confirmed that spaCy offers the **fastest
syntactic parser in the world** and that **its accuracy is within 1% of the
best** available. The few systems that are more accurate are 20× slower or more.

> #### About the evaluation
>
> The first of the evaluations was published by **Yahoo! Labs** and **Emory
> University**, as part of a survey of current parsing technologies
> ([Choi et al., 2015](https://aclweb.org/anthology/P/P15/P15-1038.pdf)). Their
> results and subsequent discussions helped us develop a novel
> psychologically-motivated technique to improve spaCy's accuracy, which we
> published in joint work with Macquarie University
> ([Honnibal and Johnson, 2015](https://www.aclweb.org/anthology/D/D15/D15-1162.pdf)).

import BenchmarksChoi from 'usage/\_benchmarks-choi.md'

<BenchmarksChoi />

### Algorithm comparison {#algorithm}

In this section, we compare spaCy's algorithms to recently published systems,
using some of the most popular benchmarks. These benchmarks are designed to help
isolate the contributions of specific algorithmic decisions, so they promote
slightly "idealized" conditions. Specifically, the text comes pre-processed with
"gold standard" token and sentence boundaries. The data sets also tend to be
fairly small, to help researchers iterate quickly. These conditions mean the
models trained on these data sets are not always useful for practical purposes.

#### Parse accuracy (Penn Treebank / Wall Street Journal) {#parse-accuracy-penn}

This is the "classic" evaluation, so it's the number parsing researchers are
most easily able to put in context. However, it's quite far removed from actual
usage: it uses sentences with gold-standard segmentation and tokenization, from
a pretty specific type of text (articles from a single newspaper, 1984-1989).

> #### Methodology
>
> [Andor et al. (2016)](http://arxiv.org/abs/1603.06042) chose slightly
> different experimental conditions from
> [Choi et al. (2015)](https://aclweb.org/anthology/P/P15/P15-1038.pdf), so the
> two accuracy tables here do not present directly comparable figures.

| System                                                       | Year | Type   |  Accuracy |
| ------------------------------------------------------------ | ---- | ------ | --------: |
| spaCy v2.0.0                                                 | 2017 | neural |     94.48 |
| spaCy v1.1.0                                                 | 2016 | linear |     92.80 |
| [Dozat and Manning][dozat and manning]                       | 2017 | neural | **95.75** |
| [Andor et al.][andor et al.]                                 | 2016 | neural |     94.44 |
| [SyntaxNet Parsey McParseface][syntaxnet parsey mcparseface] | 2016 | neural |     94.15 |
| [Weiss et al.][weiss et al.]                                 | 2015 | neural |     93.91 |
| [Zhang and McDonald][zhang and mcdonald]                     | 2014 | linear |     93.32 |
| [Martins et al.][martins et al.]                             | 2013 | linear |     93.10 |

[dozat and manning]: https://arxiv.org/pdf/1611.01734.pdf
[andor et al.]: http://arxiv.org/abs/1603.06042
[syntaxnet parsey mcparseface]:
  https://github.com/tensorflow/models/tree/master/research/syntaxnet
[weiss et al.]:
  http://static.googleusercontent.com/media/research.google.com/en//pubs/archive/43800.pdf
[zhang and mcdonald]: http://research.google.com/pubs/archive/38148.pdf
[martins et al.]: http://www.cs.cmu.edu/~ark/TurboParser/

#### NER accuracy (OntoNotes 5, no pre-process) {#ner-accuracy-ontonotes5}

This is the evaluation we use to tune spaCy's parameters to decide which
algorithms are better than the others. It's reasonably close to actual usage,
because it requires the parses to be produced from raw text, without any
pre-processing.

| System                                             | Year | Type   |  Accuracy |
| -------------------------------------------------- | ---- | ------ | --------: |
| spaCy [`en_core_web_lg`][en_core_web_lg] v2.0.0a3  | 2017 | neural |     85.85 |
| [Strubell et al.][strubell et al.]                 | 2017 | neural | **86.81** |
| [Chiu and Nichols][chiu and nichols]               | 2016 | neural |     86.19 |
| [Durrett and Klein][durrett and klein]             | 2014 | neural |     84.04 |
| [Ratinov and Roth][ratinov and roth]               | 2009 | linear |     83.45 |

[en_core_web_lg]: /models/en#en_core_web_lg
[strubell et al.]: https://arxiv.org/pdf/1702.02098.pdf
[chiu and nichols]:
  https://www.semanticscholar.org/paper/Named-Entity-Recognition-with-Bidirectional-LSTM-C-Chiu-Nichols/10a4db59e81d26b2e0e896d3186ef81b4458b93f
[durrett and klein]:
  https://www.semanticscholar.org/paper/A-Joint-Model-for-Entity-Analysis-Coreference-Typi-Durrett-Klein/28eb033eee5f51c5e5389cbb6b777779203a6778
[ratinov and roth]: http://www.aclweb.org/anthology/W09-1119

### Model comparison {#spacy-models}

In this section, we provide benchmark accuracies for the pre-trained model
pipelines we distribute with spaCy. Evaluations are conducted end-to-end from
raw text, with no "gold standard" pre-processing, over text from a mix of genres
where possible.

> #### Methodology
>
> The evaluation was conducted on raw text with no gold standard information.
> The parser, tagger and entity recognizer were trained on the
> [OntoNotes 5](https://www.gabormelli.com/RKB/OntoNotes_Corpus) corpus, the
> word vectors on [Common Crawl](http://commoncrawl.org).

#### English {#benchmarks-models-english}

| Model                                               | spaCy | Type   |      UAS |    NER F |      POS |       WPS |     Size |
| --------------------------------------------------- | ----- | ------ | -------: | -------: | -------: | --------: | -------: |
| [`en_core_web_sm`](/models/en#en_core_web_sm) 2.0.0 | 2.x   | neural |     91.7 |     85.3 |     97.0 |     10.1k | **35MB** |
| [`en_core_web_md`](/models/en#en_core_web_md) 2.0.0 | 2.x   | neural |     91.7 | **85.9** |     97.1 |     10.0k |    115MB |
| [`en_core_web_lg`](/models/en#en_core_web_lg) 2.0.0 | 2.x   | neural | **91.9** | **85.9** | **97.2** |     10.0k |    812MB |
| `en_core_web_sm` 1.2.0                              | 1.x   | linear |     86.6 |     78.5 |     96.6 | **25.7k** |     50MB |
| `en_core_web_md` 1.2.1                              | 1.x   | linear |     90.6 |     81.4 |     96.7 |     18.8k |      1GB |

#### Spanish {#benchmarks-models-spanish}

> #### Evaluation note
>
> The NER accuracy refers to the "silver standard" annotations in the WikiNER
> corpus. Accuracy on these annotations tends to be higher than correct human
> annotations.

| Model                                                 | spaCy | Type   |      UAS |    NER F |      POS |   WPS |     Size |
| ----------------------------------------------------- | ----- | ------ | -------: | -------: | -------: | ----: | -------: |
| [`es_core_news_sm`](/models/es#es_core_news_sm) 2.0.0 | 2.x   | neural |     89.8 |     88.7 | **96.9** | _n/a_ | **35MB** |
| [`es_core_news_md`](/models/es#es_core_news_md) 2.0.0 | 2.x   | neural | **90.2** |     89.0 |     97.8 | _n/a_ |     93MB |
| `es_core_web_md` 1.1.0                                | 1.x   | linear |     87.5 | **94.2** |     96.7 | _n/a_ |    377MB |

### Detailed speed comparison {#speed-comparison}

Here we compare the per-document processing time of various spaCy
functionalities against other NLP libraries. We show both absolute timings (in
ms) and relative performance (normalized to spaCy). Lower is better.

<Infobox title="Important note" variant="warning">

This evaluation was conducted in 2015. We're working on benchmarks on current
CPU and GPU hardware. In the meantime, we're grateful to the Stanford folks for
drawing our attention to what seems to be
[a long-standing error](https://nlp.stanford.edu/software/tokenizer.html#Speed)
in our CoreNLP benchmarks, especially for their tokenizer. Until we run
corrected experiments, we have updated the table using their figures.

</Infobox>

> #### Methodology
>
> - **Set up:** 100,000 plain-text documents were streamed from an SQLite3
>   database, and processed with an NLP library, to one of three levels of
>   detail — tokenization, tagging, or parsing. The tasks are additive: to parse
>   the text you have to tokenize and tag it. The pre-processing was not
>   subtracted from the times — we report the time required for the pipeline to
>   complete. We report mean times per document, in milliseconds.
> - **Hardware**: Intel i7-3770 (2012)
> - **Implementation**:
>   [`spacy-benchmarks`](https://github.com/explosion/spacy-benchmarks)

<Table>
<thead>
    <Tr>
        <Th></Th>
        <Th colSpan="3">Absolute (ms per doc)</Th>
        <Th colSpan="3">Relative (to spaCy)</Th>
    </Tr>
    <Tr>
        <Th>System</Th>
        <Th>Tokenize</Th>
        <Th>Tag</Th>
        <Th>Parse</Th>
        <Th>Tokenize</Th>
        <Th>Tag</Th>
        <Th>Parse</Th>
    </Tr>
</thead>
<tbody style="text-align: right">
    <Tr>
        <Td style="text-align: left"><strong>spaCy</strong></Td>
        <Td>0.2ms</Td>
        <Td>1ms</Td>
        <Td>19ms</Td>
        <Td>1x</Td>
        <Td>1x</Td>
        <Td>1x</Td>
    </Tr>
    <Tr>
        <Td style="text-align: left">CoreNLP</Td>
        <Td>0.18ms</Td>
        <Td>10ms</Td>
        <Td>49ms</Td>
        <Td>0.9x</Td>
        <Td>10x</Td>
        <Td>2.6x</Td>
    </Tr>
    <Tr>
        <Td style="text-align: left">ZPar</Td>
        <Td>1ms</Td>
        <Td>8ms</Td>
        <Td>850ms</Td>
        <Td>5x</Td>
        <Td>8x</Td>
        <Td>44.7x</Td>
    </Tr>
    <Tr>
        <Td style="text-align: left">NLTK</Td>
        <Td>4ms</Td>
        <Td>443ms</Td>
        <Td><em>n/a</em></Td>
        <Td>20x</Td>
        <Td>443x</Td>
        <Td><em>n/a</em></Td>
    </Tr>
</tbody>
</Table>
