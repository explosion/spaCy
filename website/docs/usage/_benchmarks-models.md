import { Help } from 'components/typography'; import Link from 'components/link'

<!-- TODO: update numbers, add note on previous NER evaluation issues -->

<figure>

| Pipeline                                                   | Parser | Tagger |  NER | WPS<br />CPU <Help>words per second on CPU, higher is better</Help> | WPS<br/>GPU <Help>words per second on GPU, higher is better</Help> |
| ---------------------------------------------------------- | -----: | -----: | ---: | ------------------------------------------------------------------: | -----------------------------------------------------------------: |
| [`en_core_web_trf`](/models/en#en_core_web_trf) (spaCy v3) |        |        |      |                                                                     |                                                                 6k |
| [`en_core_web_lg`](/models/en#en_core_web_lg) (spaCy v3)   |   92.2 |   97.4 | 85.8 |                                                                  7k |                                                                    |
| `en_core_web_lg` (spaCy v2)                                |   91.9 |   97.2 | 85.9 |                                                                 10k |                                                                    |

<figcaption class="caption">

**Full pipeline accuracy and speed** on the
[OntoNotes 5.0](https://catalog.ldc.upenn.edu/LDC2013T19) corpus.

</figcaption>

</figure>

<figure>

| Named Entity Recognition System                                                | OntoNotes | CoNLL '03 |
| ------------------------------------------------------------------------------ | --------: | --------: |
| spaCy RoBERTa (2020)                                                           |           |      92.2 |
| spaCy CNN (2020)                                                               |      85.3 |      88.4 |
| spaCy CNN (2017)                                                               |      86.4 |           |
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
