---
title: Annotation Specifications
teaser: Schemes used for labels, tags and training data
menu:
  - ['Text Processing', 'text-processing']
  - ['POS Tagging', 'pos-tagging']
  - ['Dependencies', 'dependency-parsing']
  - ['Named Entities', 'named-entities']
  - ['Models & Training', 'training']
---

## Text processing {#text-processing}

> #### Example
>
> ```python
> from spacy.lang.en import English
> nlp = English()
> tokens = nlp(u"Some\\nspaces  and\\ttab characters")
> tokens_text = [t.text for t in tokens]
> assert tokens_text == ["Some", "\\n", "spaces", " ", "and", "\\t", "tab", "characters"]
> ```

Tokenization standards are based on the
[OntoNotes 5](https://catalog.ldc.upenn.edu/LDC2013T19) corpus. The tokenizer
differs from most by including **tokens for significant whitespace**. Any
sequence of whitespace characters beyond a single space (`' '`) is included as a
token. The whitespace tokens are useful for much the same reason punctuation is
– it's often an important delimiter in the text. By preserving it in the token
output, we are able to maintain a simple alignment between the tokens and the
original string, and we ensure that **no information is lost** during
processing.

### Lemmatization {#lemmatization}

> #### Examples
>
> In English, this means:
>
> - **Adjectives**: happier, happiest → happy
> - **Adverbs**: worse, worst → badly
> - **Nouns**: dogs, children → dog, child
> - **Verbs**: writes, writing, wrote, written → write

A lemma is the uninflected form of a word. The English lemmatization data is
taken from [WordNet](https://wordnet.princeton.edu). Lookup tables are taken
from [Lexiconista](http://www.lexiconista.com/datasets/lemmatization/). spaCy
also adds a **special case for pronouns**: all pronouns are lemmatized to the
special token `-PRON-`.

<Infobox title="About spaCy's custom pronoun lemma" variant="warning">

Unlike verbs and common nouns, there's no clear base form of a personal pronoun.
Should the lemma of "me" be "I", or should we normalize person as well, giving
"it" — or maybe "he"? spaCy's solution is to introduce a novel symbol, `-PRON-`,
which is used as the lemma for all personal pronouns.

</Infobox>

### Sentence boundary detection {#sentence-boundary}

Sentence boundaries are calculated from the syntactic parse tree, so features
such as punctuation and capitalization play an important but non-decisive role
in determining the sentence boundaries. Usually this means that the sentence
boundaries will at least coincide with clause boundaries, even given poorly
punctuated text.

## Part-of-speech tagging {#pos-tagging}

> #### Tip: Understanding tags
>
> You can also use `spacy.explain` to get the description for the string
> representation of a tag. For example, `spacy.explain("RB")` will return
> "adverb".

This section lists the fine-grained and coarse-grained part-of-speech tags
assigned by spaCy's [models](/models). The individual mapping is specific to the
training corpus and can be defined in the respective language data's
[`tag_map.py`](/usage/adding-languages#tag-map).

<Accordion title="Universal Part-of-speech Tags" id="pos-universal">

spaCy also maps all language-specific part-of-speech tags to a small, fixed set
of word type tags following the
[Universal Dependencies scheme](http://universaldependencies.org/u/pos/). The
universal tags don't code for any morphological features and only cover the word
type. They're available as the [`Token.pos`](/api/token#attributes) and
[`Token.pos_`](/api/token#attributes) attributes.

| POS     | Description               | Examples                                      |
| ------- | ------------------------- | --------------------------------------------- |
| `ADJ`   | adjective                 | big, old, green, incomprehensible, first      |
| `ADP`   | adposition                | in, to, during                                |
| `ADV`   | adverb                    | very, tomorrow, down, where, there            |
| `AUX`   | auxiliary                 | is, has (done), will (do), should (do)        |
| `CONJ`  | conjunction               | and, or, but                                  |
| `CCONJ` | coordinating conjunction  | and, or, but                                  |
| `DET`   | determiner                | a, an, the                                    |
| `INTJ`  | interjection              | psst, ouch, bravo, hello                      |
| `NOUN`  | noun                      | girl, cat, tree, air, beauty                  |
| `NUM`   | numeral                   | 1, 2017, one, seventy-seven, IV, MMXIV        |
| `PART`  | particle                  | 's, not,                                      |
| `PRON`  | pronoun                   | I, you, he, she, myself, themselves, somebody |
| `PROPN` | proper noun               | Mary, John, London, NATO, HBO                 |
| `PUNCT` | punctuation               | ., (, ), ?                                    |
| `SCONJ` | subordinating conjunction | if, while, that                               |
| `SYM`   | symbol                    | \$, %, §, ©, +, −, ×, ÷, =, :), 😝            |
| `VERB`  | verb                      | run, runs, running, eat, ate, eating          |
| `X`     | other                     | sfpksdpsxmsa                                  |
| `SPACE` | space                     |

</Accordion>

<Accordion title="English" id="pos-en">

The English part-of-speech tagger uses the
[OntoNotes 5](https://catalog.ldc.upenn.edu/LDC2013T19) version of the Penn
Treebank tag set. We also map the tags to the simpler Google Universal POS tag
set.

| Tag                                 |  POS    | Morphology                                     | Description                               |
| ----------------------------------- | ------- | ---------------------------------------------- | ----------------------------------------- |
| `-LRB-`                             | `PUNCT` | `PunctType=brck PunctSide=ini`                 | left round bracket                        |
| `-RRB-`                             | `PUNCT` | `PunctType=brck PunctSide=fin`                 | right round bracket                       |
| `,`                                 | `PUNCT` | `PunctType=comm`                               | punctuation mark, comma                   |
| `:`                                 | `PUNCT` |                                                | punctuation mark, colon or ellipsis       |
| `.`                                 | `PUNCT` | `PunctType=peri`                               | punctuation mark, sentence closer         |
| `''`                                | `PUNCT` | `PunctType=quot PunctSide=fin`                 | closing quotation mark                    |
| `""`                                | `PUNCT` | `PunctType=quot PunctSide=fin`                 | closing quotation mark                    |
| <InlineCode>&#96;&#96;</InlineCode> | `PUNCT` | `PunctType=quot PunctSide=ini`                 | opening quotation mark                    |
| `#`                                 | `SYM`   | `SymType=numbersign`                           | symbol, number sign                       |
| `$`                                 | `SYM`   | `SymType=currency`                             | symbol, currency                          |
| `ADD`                               | `X`     |                                                | email                                     |
| `AFX`                               | `ADJ`   | `Hyph=yes`                                     | affix                                     |
| `BES`                               | `VERB`  |                                                | auxiliary "be"                            |
| `CC`                                | `CONJ`  | `ConjType=coor`                                | conjunction, coordinating                 |
| `CD`                                | `NUM`   | `NumType=card`                                 | cardinal number                           |
| `DT`                                | `DET`   |                                                | determiner                                |
| `EX`                                | `ADV`   | `AdvType=ex`                                   | existential there                         |
| `FW`                                | `X`     | `Foreign=yes`                                  | foreign word                              |
| `GW`                                | `X`     |                                                | additional word in multi-word expression  |
| `HVS`                               | `VERB`  |                                                | forms of "have"                           |
| `HYPH`                              | `PUNCT` | `PunctType=dash`                               | punctuation mark, hyphen                  |
| `IN`                                | `ADP`   |                                                | conjunction, subordinating or preposition |
| `JJ`                                | `ADJ`   | `Degree=pos`                                   | adjective                                 |
| `JJR`                               | `ADJ`   | `Degree=comp`                                  | adjective, comparative                    |
| `JJS`                               | `ADJ`   | `Degree=sup`                                   | adjective, superlative                    |
| `LS`                                | `PUNCT` | `NumType=ord`                                  | list item marker                          |
| `MD`                                | `VERB`  | `VerbType=mod`                                 | verb, modal auxiliary                     |
| `NFP`                               | `PUNCT` |                                                | superfluous punctuation                   |
| `NIL`                               |         |                                                | missing tag                               |
| `NN`                                | `NOUN`  | `Number=sing`                                  | noun, singular or mass                    |
| `NNP`                               | `PROPN` | `NounType=prop Number=sign`                    | noun, proper singular                     |
| `NNPS`                              | `PROPN` | `NounType=prop Number=plur`                    | noun, proper plural                       |
| `NNS`                               | `NOUN`  | `Number=plur`                                  | noun, plural                              |
| `PDT`                               | `ADJ`   | `AdjType=pdt PronType=prn`                     | predeterminer                             |
| `POS`                               | `PART`  | `Poss=yes`                                     | possessive ending                         |
| `PRP`                               | `PRON`  | `PronType=prs`                                 | pronoun, personal                         |
| `PRP$`                              | `ADJ`   | `PronType=prs Poss=yes`                        | pronoun, possessive                       |
| `RB`                                | `ADV`   | `Degree=pos`                                   | adverb                                    |
| `RBR`                               | `ADV`   | `Degree=comp`                                  | adverb, comparative                       |
| `RBS`                               | `ADV`   | `Degree=sup`                                   | adverb, superlative                       |
| `RP`                                | `PART`  |                                                | adverb, particle                          |
| `_SP`                               | `SPACE` |                                                | space                                     |
| `SYM`                               | `SYM`   |                                                | symbol                                    |
| `TO`                                | `PART`  | `PartType=inf VerbForm=inf`                    | infinitival "to"                          |
| `UH`                                | `INTJ`  |                                                | interjection                              |
| `VB`                                | `VERB`  | `VerbForm=inf`                                 | verb, base form                           |
| `VBD`                               | `VERB`  | `VerbForm=fin Tense=past`                      | verb, past tense                          |
| `VBG`                               | `VERB`  | `VerbForm=part Tense=pres Aspect=prog`         | verb, gerund or present participle        |
| `VBN`                               | `VERB`  | `VerbForm=part Tense=past Aspect=perf`         | verb, past participle                     |
| `VBP`                               | `VERB`  | `VerbForm=fin Tense=pres`                      | verb, non-3rd person singular present     |
| `VBZ`                               | `VERB`  | `VerbForm=fin Tense=pres Number=sing Person=3` | verb, 3rd person singular present         |
| `WDT`                               | `ADJ`   | `PronType=int|rel`                             | wh-determiner                             |
| `WP`                                | `NOUN`  | `PronType=int|rel`                             | wh-pronoun, personal                      |
| `WP$`                               | `ADJ`   | `Poss=yes PronType=int|rel`                    | wh-pronoun, possessive                    |
| `WRB`                               | `ADV`   | `PronType=int|rel`                             | wh-adverb                                 |
| `XX`                                | `X`     |                                                | unknown                                   |

</Accordion>

<Accordion title="German" id="pos-de">

The German part-of-speech tagger uses the
[TIGER Treebank](http://www.ims.uni-stuttgart.de/forschung/ressourcen/korpora/TIGERCorpus/annotation/index.html)
annotation scheme. We also map the tags to the simpler Google Universal POS tag
set.

| Tag       |  POS    | Morphology                                  | Description                                       |
| --------- | ------- | ------------------------------------------- | ------------------------------------------------- |
| `$(`      | `PUNCT` | `PunctType=brck`                            | other sentence-internal punctuation mark          |
| `$,`      | `PUNCT` | `PunctType=comm`                            | comma                                             |
| `$.`      | `PUNCT` | `PunctType=peri`                            | sentence-final punctuation mark                   |
| `ADJA`    | `ADJ`   |                                             | adjective, attributive                            |
| `ADJD`    | `ADJ`   | `Variant=short`                             | adjective, adverbial or predicative               |
| `ADV`     | `ADV`   |                                             | adverb                                            |
| `APPO`    | `ADP`   | `AdpType=post`                              | postposition                                      |
| `APPR`    | `ADP`   | `AdpType=prep`                              | preposition; circumposition left                  |
| `APPRART` | `ADP`   | `AdpType=prep PronType=art`                 | preposition with article                          |
| `APZR`    | `ADP`   | `AdpType=circ`                              | circumposition right                              |
| `ART`     | `DET`   | `PronType=art`                              | definite or indefinite article                    |
| `CARD`    | `NUM`   | `NumType=card`                              | cardinal number                                   |
| `FM`      | `X`     | `Foreign=yes`                               | foreign language material                         |
| `ITJ`     | `INTJ`  |                                             | interjection                                      |
| `KOKOM`   | `CONJ`  | `ConjType=comp`                             | comparative conjunction                           |
| `KON`     | `CONJ`  |                                             | coordinate conjunction                            |
| `KOUI`    | `SCONJ` |                                             | subordinate conjunction with "zu" and infinitive  |
| `KOUS`    | `SCONJ` |                                             | subordinate conjunction with sentence             |
| `NE`      | `PROPN` |                                             | proper noun                                       |
| `NNE`     | `PROPN` |                                             | proper noun                                       |
| `NN`      | `NOUN`  |                                             | noun, singular or mass                            |
| `PAV`     | `ADV`   | `PronType=dem`                              | pronominal adverb                                 |
| `PROAV`   | `ADV`   | `PronType=dem`                              | pronominal adverb                                 |
| `PDAT`    | `DET`   | `PronType=dem`                              | attributive demonstrative pronoun                 |
| `PDS`     | `PRON`  | `PronType=dem`                              | substituting demonstrative pronoun                |
| `PIAT`    | `DET`   | `PronType=ind\|neg\|tot`                    | attributive indefinite pronoun without determiner |
| `PIDAT`   | `DET`   | `AdjType=pdt PronType=ind\|neg\|tot`        | attributive indefinite pronoun with determiner    |
| `PIS`     | `PRON`  | `PronType=ind\|neg\|tot`                    | substituting indefinite pronoun                   |
| `PPER`    | `PRON`  | `PronType=prs`                              | non-reflexive personal pronoun                    |
| `PPOSAT`  | `DET`   | `Poss=yes PronType=prs`                     | attributive possessive pronoun                    |
| `PPOSS`   | `PRON`  | `PronType=rel`                              | substituting possessive pronoun                   |
| `PRELAT`  | `DET`   | `PronType=rel`                              | attributive relative pronoun                      |
| `PRELS`   | `PRON`  | `PronType=rel`                              | substituting relative pronoun                     |
| `PRF`     | `PRON`  | `PronType=prs Reflex=yes`                   | reflexive personal pronoun                        |
| `PTKA`    | `PART`  |                                             | particle with adjective or adverb                 |
| `PTKANT`  | `PART`  | `PartType=res`                              | answer particle                                   |
| `PTKNEG`  | `PART`  | `Negative=yes`                              | negative particle                                 |
| `PTKVZ`   | `PART`  | `PartType=vbp`                              | separable verbal particle                         |
| `PTKZU`   | `PART`  | `PartType=inf" | "zu" before infinitive     |
| `PWAT`    | `DET`   | `PronType=int`                              | attributive interrogative pronoun                 |
| `PWAV`    | `ADV`   | `PronType=int`                              | adverbial interrogative or relative pronoun       |
| `PWS`     | `PRON`  | `PronType=int`                              | substituting interrogative pronoun                |
| `TRUNC`   | `X`     | `Hyph=yes`                                  | word remnant                                      |
| `VAFIN`   | `AUX`   | `Mood=ind VerbForm=fin`                     | finite verb, auxiliary                            |
| `VAIMP`   | `AUX`   | `Mood=imp VerbForm=fin`                     | imperative, auxiliary                             |
| `VAINF`   | `AUX`   | `VerbForm=inf`                              | infinitive, auxiliary                             |
| `VAPP`    | `AUX`   | `Aspect=perf VerbForm=fin`                  | perfect participle, auxiliary                     |
| `VMFIN`   | `VERB`  | `Mood=ind VerbForm=fin VerbType=mod`        | finite verb, modal                                |
| `VMINF`   | `VERB`  | `VerbForm=fin VerbType=mod`                 | infinitive, modal                                 |
| `VMPP`    | `VERB`  | `Aspect=perf VerbForm=part VerbType=mod`    | perfect participle, modal                         |
| `VVFIN`   | `VERB`  | `Mood=ind VerbForm=fin`                     | finite verb, full                                 |
| `VVIMP`   | `VERB`  | `Mood=imp VerbForm=fin`                     | imperative, full                                  |
| `VVINF`   | `VERB`  | `VerbForm=inf`                              | infinitive, full                                  |
| `VVIZU`   | `VERB`  | `VerbForm=inf" | infinitive with "zu", full |
| `VVPP`    | `VERB`  | `Aspect=perf VerbForm=part`                 | perfect participle, full                          |
| `XY`      | `X`     |                                             | non-word containing non-letter                    |
| `SP`      | `SPACE` |                                             | space                                             |

</Accordion>

---

<Infobox title="Annotation schemes for other models">

For the label schemes used by the other models, see the respective `tag_map.py`
in [`spacy/lang`](https://github.com/explosion/spaCy/tree/master/spacy/lang).

</Infobox>

## Syntactic Dependency Parsing {#dependency-parsing}

> #### Tip: Understanding labels
>
> You can also use `spacy.explain` to get the description for the string
> representation of a label. For example, `spacy.explain("prt")` will return
> "particle".

This section lists the syntactic dependency labels assigned by spaCy's
[models](/models). The individual labels are language-specific and depend on the
training corpus.

<Accordion title="Universal Dependency Labels" id="dependency-parsing-universal">

The [Universal Dependencies scheme](http://universaldependencies.org/u/dep/) is
used in all languages trained on Universal Dependency Corpora.

| Label        | Description                                  |
| ------------ | -------------------------------------------- |
| `acl`        | clausal modifier of noun (adjectival clause) |
| `advcl`      | adverbial clause modifier                    |
| `advmod`     | adverbial modifier                           |
| `amod`       | adjectival modifier                          |
| `appos`      | appositional modifier                        |
| `aux`        | auxiliary                                    |
| `case`       | case marking                                 |
| `cc`         | coordinating conjunction                     |
| `ccomp`      | clausal complement                           |
| `clf`        | classifier                                   |
| `compound`   | compound                                     |
| `conj`       | conjunct                                     |
| `cop`        | copula                                       |
| `csubj`      | clausal subject                              |
| `dep`        | unspecified dependency                       |
| `det`        | determiner                                   |
| `discourse`  | discourse element                            |
| `dislocated` | dislocated elements                          |
| `expl`       | expletive                                    |
| `fixed`      | fixed multiword expression                   |
| `flat`       | flat multiword expression                    |
| `goeswith`   | goes with                                    |
| `iobj`       | indirect object                              |
| `list`       | list                                         |
| `mark`       | marker                                       |
| `nmod`       | nominal modifier                             |
| `nsubj`      | nominal subject                              |
| `nummod`     | numeric modifier                             |
| `obj`        | object                                       |
| `obl`        | oblique nominal                              |
| `orphan`     | orphan                                       |
| `parataxis`  | parataxis                                    |
| `punct`      | punctuation                                  |
| `reparandum` | overridden disfluency                        |
| `root`       | root                                         |
| `vocative`   | vocative                                     |
| `xcomp`      | open clausal complement                      |

</Accordion>

<Accordion title="English" id="dependency-parsing-english">

The English dependency labels use the
[CLEAR Style](https://github.com/clir/clearnlp-guidelines/blob/master/md/specifications/dependency_labels.md)
by [ClearNLP](http://www.clearnlp.com).

| Label       | Description                                  |
| ----------- | -------------------------------------------- |
| `acl`       | clausal modifier of noun (adjectival clause) |
| `acomp`     | adjectival complement                        |
| `advcl`     | adverbial clause modifier                    |
| `advmod`    | adverbial modifier                           |
| `agent`     | agent                                        |
| `amod`      | adjectival modifier                          |
| `appos`     | appositional modifier                        |
| `attr`      | attribute                                    |
| `aux`       | auxiliary                                    |
| `auxpass`   | auxiliary (passive)                          |
| `case`      | case marking                                 |
| `cc`        | coordinating conjunction                     |
| `ccomp`     | clausal complement                           |
| `compound`  | compound                                     |
| `conj`      | conjunct                                     |
| `cop`       | copula                                       |
| `csubj`     | clausal subject                              |
| `csubjpass` | clausal subject (passive)                    |
| `dative`    | dative                                       |
| `dep`       | unclassified dependent                       |
| `det`       | determiner                                   |
| `dobj`      | direct object                                |
| `expl`      | expletive                                    |
| `intj`      | interjection                                 |
| `mark`      | marker                                       |
| `meta`      | meta modifier                                |
| `neg`       | negation modifier                            |
| `nn`        | noun compound modifier                       |
| `nounmod`   | modifier of nominal                          |
| `npmod`     | noun phrase as adverbial modifier            |
| `nsubj`     | nominal subject                              |
| `nsubjpass` | nominal subject (passive)                    |
| `nummod`    | numeric modifier                             |
| `oprd`      | object predicate                             |
| `obj`       | object                                       |
| `obl`       | oblique nominal                              |
| `parataxis` | parataxis                                    |
| `pcomp`     | complement of preposition                    |
| `pobj`      | object of preposition                        |
| `poss`      | possession modifier                          |
| `preconj`   | pre-correlative conjunction                  |
| `prep`      | prepositional modifier                       |
| `prt`       | particle                                     |
| `punct`     | punctuation                                  |
| `quantmod`  | modifier of quantifier                       |
| `relcl`     | relative clause modifier                     |
| `root`      | root                                         |
| `xcomp`     | open clausal complement                      |

</Accordion>

<Accordion title="German" id="dependency-parsing-german">

The German dependency labels use the
[TIGER Treebank](http://www.ims.uni-stuttgart.de/forschung/ressourcen/korpora/TIGERCorpus/annotation/index.html)
annotation scheme.

| Label  | Description                     |
| ------ | ------------------------------- |
| `ac`   | adpositional case marker        |
| `adc`  | adjective component             |
| `ag`   | genitive attribute              |
| `ams`  | measure argument of adjective   |
| `app`  | apposition                      |
| `avc`  | adverbial phrase component      |
| `cc`   | comparative complement          |
| `cd`   | coordinating conjunction        |
| `cj`   | conjunct                        |
| `cm`   | comparative conjunction         |
| `cp`   | complementizer                  |
| `cvc`  | collocational verb construction |
| `da`   | dative                          |
| `dh`   | discourse-level head            |
| `dm`   | discourse marker                |
| `ep`   | expletive es                    |
| `hd`   | head                            |
| `ju`   | junctor                         |
| `mnr`  | postnominal modifier            |
| `mo`   | modifier                        |
| `ng`   | negation                        |
| `nk`   | noun kernel element             |
| `nmc`  | numerical component             |
| `oa`   | accusative object               |
| `oa`   | second accusative object        |
| `oc`   | clausal object                  |
| `og`   | genitive object                 |
| `op`   | prepositional object            |
| `par`  | parenthetical element           |
| `pd`   | predicate                       |
| `pg`   | phrasal genitive                |
| `ph`   | placeholder                     |
| `pm`   | morphological particle          |
| `pnc`  | proper noun component           |
| `rc`   | relative clause                 |
| `re`   | repeated element                |
| `rs`   | reported speech                 |
| `sb`   | subject                         |
| `sp`   | "subject or predicate           |
| `svp`  | separable verb prefix           |
| `uc`   | unit component                  |
| `vo`   | vocative                        |
| `ROOT` | root                            |

</Accordion>

## Named Entity Recognition {#named-entities}

> #### Tip: Understanding entity types
>
> You can also use `spacy.explain` to get the description for the string
> representation of an entity label. For example, `spacy.explain("LANGUAGE")`
> will return "any named language".

Models trained on the [OntoNotes 5](https://catalog.ldc.upenn.edu/LDC2013T19)
corpus support the following entity types:

| Type          | Description                                          |
| ------------- | ---------------------------------------------------- |
| `PERSON`      | People, including fictional.                         |
| `NORP`        | Nationalities or religious or political groups.      |
| `FAC`         | Buildings, airports, highways, bridges, etc.         |
| `ORG`         | Companies, agencies, institutions, etc.              |
| `GPE`         | Countries, cities, states.                           |
| `LOC`         | Non-GPE locations, mountain ranges, bodies of water. |
| `PRODUCT`     | Objects, vehicles, foods, etc. (Not services.)       |
| `EVENT`       | Named hurricanes, battles, wars, sports events, etc. |
| `WORK_OF_ART` | Titles of books, songs, etc.                         |
| `LAW`         | Named documents made into laws.                      |
| `LANGUAGE`    | Any named language.                                  |
| `DATE`        | Absolute or relative dates or periods.               |
| `TIME`        | Times smaller than a day.                            |
| `PERCENT`     | Percentage, including "%".                           |
| `MONEY`       | Monetary values, including unit.                     |
| `QUANTITY`    | Measurements, as of weight or distance.              |
| `ORDINAL`     | "first", "second", etc.                              |
| `CARDINAL`    | Numerals that do not fall under another type.        |

### Wikipedia scheme {#ner-wikipedia-scheme}

Models trained on Wikipedia corpus
([Nothman et al., 2013](http://www.sciencedirect.com/science/article/pii/S0004370212000276))
use a less fine-grained NER annotation scheme and recognise the following
entities:

| Type   | Description                                                                                                                               |
| ------ | ----------------------------------------------------------------------------------------------------------------------------------------- |
| `PER`  | Named person or family.                                                                                                                   |
| `LOC`  | Name of politically or geographically defined location (cities, provinces, countries, international regions, bodies of water, mountains). |
| `ORG`  | Named corporate, governmental, or other organizational entity.                                                                            |
| `MISC` | Miscellaneous entities, e.g. events, nationalities, products or works of art.                                                             |

### IOB Scheme {#iob}

| Tag   | ID  | Description                           |
| ----- | --- | ------------------------------------- |
| `"I"` | `1` | Token is inside an entity.            |
| `"O"` | `2` | Token is outside an entity.           |
| `"B"` | `3` | Token begins an entity.               |
| `""`  | `0` | No entity tag is set (missing value). |

### BILUO Scheme {#biluo}

| Tag         | Description                              |
| ----------- | ---------------------------------------- |
| **`B`**EGIN | The first token of a multi-token entity. |
| **`I`**N    | An inner token of a multi-token entity.  |
| **`L`**AST  | The final token of a multi-token entity. |
| **`U`**NIT  | A single-token entity.                   |
| **`O`**UT   | A non-entity token.                      |

> #### Why BILUO, not IOB?
>
> There are several coding schemes for encoding entity annotations as token
> tags. These coding schemes are equally expressive, but not necessarily equally
> learnable. [Ratinov and Roth](http://www.aclweb.org/anthology/W09-1119) showed
> that the minimal **Begin**, **In**, **Out** scheme was more difficult to learn
> than the **BILUO** scheme that we use, which explicitly marks boundary tokens.

spaCy translates the character offsets into this scheme, in order to decide the
cost of each action given the current state of the entity recogniser. The costs
are then used to calculate the gradient of the loss, to train the model. The
exact algorithm is a pastiche of well-known methods, and is not currently
described in any single publication. The model is a greedy transition-based
parser guided by a linear model whose weights are learned using the averaged
perceptron loss, via the
[dynamic oracle](http://www.aclweb.org/anthology/C12-1059) imitation learning
strategy. The transition system is equivalent to the BILOU tagging scheme.

## Models and training data {#training}

### JSON input format for training {#json-input}

spaCy takes training data in JSON format. The built-in
[`convert`](/api/cli#convert) command helps you convert the `.conllu` format
used by the
[Universal Dependencies corpora](https://github.com/UniversalDependencies) to
spaCy's training format.

> #### Annotating entities
>
> Named entities are provided in the [BILUO](#biluo) notation. Tokens outside an
> entity are set to `"O"` and tokens that are part of an entity are set to the
> entity label, prefixed by the BILUO marker. For example `"B-ORG"` describes
> the first token of a multi-token `ORG` entity and `"U-PERSON"` a single token
> representing a `PERSON` entity. The
> [`biluo_tags_from_offsets`](/api/goldparse#biluo_tags_from_offsets) function
> can help you convert entity offsets to the right format.

```python
### Example structure
[{
    "id": int,                      # ID of the document within the corpus
    "paragraphs": [{                # list of paragraphs in the corpus
        "raw": string,              # raw text of the paragraph
        "sentences": [{             # list of sentences in the paragraph
            "tokens": [{            # list of tokens in the sentence
                "id": int,          # index of the token in the document
                "dep": string,      # dependency label
                "head": int,        # offset of token head relative to token index
                "tag": string,      # part-of-speech tag
                "orth": string,     # verbatim text of the token
                "ner": string       # BILUO label, e.g. "O" or "B-ORG"
            }],
            "brackets": [{          # phrase structure (NOT USED by current models)
                "first": int,       # index of first token
                "last": int,        # index of last token
                "label": string     # phrase label
            }]
        }]
    }]
}]
```

Here's an example of dependencies, part-of-speech tags and names entities, taken
from the English Wall Street Journal portion of the Penn Treebank:

```json
https://github.com/explosion/spaCy/tree/master/examples/training/training-data.json
```

### Lexical data for vocabulary {#vocab-jsonl new="2"}

To populate a model's vocabulary, you can use the
[`spacy init-model`](/api/cli#init-model) command and load in a
[newline-delimited JSON](http://jsonlines.org/) (JSONL) file containing one
lexical entry per line via the `--jsonl-loc` option. The first line defines the
language and vocabulary settings. All other lines are expected to be JSON
objects describing an individual lexeme. The lexical attributes will be then set
as attributes on spaCy's [`Lexeme`](/api/lexeme#attributes) object. The `vocab`
command outputs a ready-to-use spaCy model with a `Vocab` containing the lexical
data.

```python
### First line
{"lang": "en", "settings": {"oov_prob": -20.502029418945312}}
```

```python
### Entry structure
{
    "orth": string,
    "id": int,
    "lower": string,
    "norm": string,
    "shape": string
    "prefix": string,
    "suffix": string,
    "length": int,
    "cluster": string,
    "prob": float,
    "is_alpha": bool,
    "is_ascii": bool,
    "is_digit": bool,
    "is_lower": bool,
    "is_punct": bool,
    "is_space": bool,
    "is_title": bool,
    "is_upper": bool,
    "like_url": bool,
    "like_num": bool,
    "like_email": bool,
    "is_stop": bool,
    "is_oov": bool,
    "is_quote": bool,
    "is_left_punct": bool,
    "is_right_punct": bool
}
```

Here's an example of the 20 most frequent lexemes in the English training data:

```json
https://github.com/explosion/spaCy/tree/master/examples/training/vocab-data.jsonl
```
