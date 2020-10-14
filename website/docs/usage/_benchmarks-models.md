import { Help } from 'components/typography'; import Link from 'components/link'

<!-- TODO: update speed and v2 NER numbers -->

<figure>

| Pipeline                                                   | Parser | Tagger |  NER | WPS<br />CPU <Help>words per second on CPU, higher is better</Help> | WPS<br/>GPU <Help>words per second on GPU, higher is better</Help> |
| ---------------------------------------------------------- | -----: | -----: | ---: | ------------------------------------------------------------------: | -----------------------------------------------------------------: |
| [`en_core_web_trf`](/models/en#en_core_web_trf) (spaCy v3) |   95.5 |   98.3 | 89.7 |                                                                  1k |                                                                 8k |
| [`en_core_web_lg`](/models/en#en_core_web_lg) (spaCy v3)   |   92.2 |   97.4 | 85.8 |                                                                  7k |                                                                    |
| `en_core_web_lg` (spaCy v2)                                |   91.9 |   97.2 |      |                                                                 10k |                                                                    |

<figcaption class="caption">

**Full pipeline accuracy and speed** on the
[OntoNotes 5.0](https://catalog.ldc.upenn.edu/LDC2013T19) corpus.

</figcaption>

</figure>

<figure>

| Named Entity Recognition System                                                | OntoNotes | CoNLL '03 |
| ------------------------------------------------------------------------------ | --------: | --------: |
| spaCy RoBERTa (2020)                                                           |      89.7 |      91.6 |
| spaCy CNN (2020)                                                               |      84.5 |           |
| spaCy CNN (2017)                                                               |           |           |
| [Stanza](https://stanfordnlp.github.io/stanza/) (StanfordNLP)<sup>1</sup>      |      88.8 |      92.1 |
| <Link to="https://github.com/flairNLP/flair" hideIcon>Flair</Link><sup>2</sup> |      89.7 |      93.1 |
| BERT Base<sup>3</sup>                                                          |         - |      92.4 |

<figcaption class="caption">

**Named entity recognition accuracy** on the
[OntoNotes 5.0](https://catalog.ldc.upenn.edu/LDC2013T19) and
[CoNLL-2003](https://www.aclweb.org/anthology/W03-0419.pdf) corpora. See
[NLP-progress](http://nlpprogress.com/english/named_entity_recognition.html) for
more results. **1. ** [Qi et al. (2020)](https://arxiv.org/pdf/2003.07082.pdf).
**2. ** [Akbik et al. (2018)](https://www.aclweb.org/anthology/C18-1139/). **3.
** [Devlin et al. (2018)](https://arxiv.org/abs/1810.04805).

</figcaption>

</figure>
