import { Help } from 'components/typography'; import Link from 'components/link'

<!-- TODO: update, add project template -->

<figure>

| System                                                                    |            Parser |            Tagger |  NER | WPS<br />CPU <Help>words per second on CPU, higher is better</Help> | WPS<br/>GPU <Help>words per second on GPU, higher is better</Help> |
| ------------------------------------------------------------------------- | ----------------: | ----------------: | ---: | ------------------------------------------------------------------: | -----------------------------------------------------------------: |
| [`en_core_web_trf`](/models/en#en_core_web_trf) (spaCy v3)                |                   |                   |      |                                                                     |                                                                 6k |
| [`en_core_web_lg`](/models/en#en_core_web_lg) (spaCy v3)                  |                   |                   |      |                                                                     |                                                                    |
| `en_core_web_lg` (spaCy v2)                                               |              91.9 |              97.2 | 85.9 |                                                                 10k |                                                                    |
| [Stanza](https://stanfordnlp.github.io/stanza/) (StanfordNLP)<sup>1</sup> | _n/a_<sup>2</sup> | _n/a_<sup>2</sup> | 88.8 |                                                                 234 |                                                                 2k |
| <Link to="https://github.com/flairNLP/flair" hideIcon>Flair</Link>        |                 - |              97.9 | 89.3 |                                                                     |                                                                    |

<figcaption class="caption">

**Accuracy and speed on the
[OntoNotes 5.0](https://catalog.ldc.upenn.edu/LDC2013T19) corpus.**<br />**1. **
[Qi et al. (2020)](https://arxiv.org/pdf/2003.07082.pdf). **2. ** _Coming soon_:
Qi et al. don't report parsing and tagging results on OntoNotes. We're working
on training Stanza on this corpus to allow direct comparison.

</figcaption>

</figure>

<figure>

| System                                                                         |  POS |  UAS |  LAS |
| ------------------------------------------------------------------------------ | ---: | ---: | ---: |
| spaCy RoBERTa (2020)                                                           | 98.0 | 96.8 | 95.0 |
| spaCy CNN (2020)                                                               |      |      |      |
| [Mrini et al.](https://khalilmrini.github.io/Label_Attention_Layer.pdf) (2019) | 97.3 | 97.4 | 96.3 |
| [Zhou and Zhao](https://www.aclweb.org/anthology/P19-1230/) (2019)             | 97.3 | 97.2 | 95.7 |

<figcaption class="caption">

**Accuracy on the Penn Treebank.** See
[NLP-progress](http://nlpprogress.com/english/dependency_parsing.html) for more
results. For spaCy's evaluation, see the
[project template](https://github.com/explosion/projects/tree/v3/benchmarks/parsing_penn_treebank).

</figcaption>

</figure>
