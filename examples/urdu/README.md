# Urdu (`ur`) community training example

This is a **training project**, not a model release. It lives in the spaCy
repository so Urdu experiments can reuse `spacy.blank("ur")`, the CLI, and the
standard config system.

There is **no official Explosion Urdu pipeline**. The public catalogue still
lists Urdu language data only (`spacy download` has nothing named `ur_*`). A
package produced here should use a community name such as `ur_community_ner_sm`
and must not be described as an official model.

## Blank pipeline vs trained pipeline

`spacy.blank("ur")` loads the Urdu tokenizer, punctuation rules, `like_num`,
and stop-word flags. It does **not** predict POS, lemmas, dependencies, or
entities.

```python
import spacy

nlp = spacy.blank("ur")
doc = nlp("کیا آپ 18 یا اٹھارہ سال کے ہیں؟")
print([(t.text, t.like_num, t.is_stop) for t in doc])
```

A trained pipeline is a statistical model saved with `spacy train` / `spacy
package`. Load it from a path or installed package name, not with
`spacy.blank`.

```python
import spacy

nlp = spacy.load("training/ner-smoke/model-best")  # only after smoke training
print([(ent.text, ent.label_) for ent in nlp("عمران خان اسلام آباد گئے").ents])
```

Whitespace tokenization plus these rules is **not** a complete Urdu word
segmenter. Missing spaces, compounds, and clitics stay ambiguous. Do not treat
transformer subwords as gold word boundaries.

Input text is not normalized. `ی`/`ے`, `ہ`/`ھ`, hamza forms, diacritics,
tatweel, and joiners are preserved. `token.is_stop` never deletes tokens.

## What this project provides

| Piece | Status |
| --- | --- |
| NER converter (JSONL → `.spacy`) | Implemented and tested |
| CoNLL-U converter wrapper | Implemented and tested |
| Document-level split + dedupe | Implemented and tested |
| CPU NER config (`tok2vec + ner`) | Generated with `spacy init config --lang ur` |
| CPU syntax config (`tok2vec + morphologizer + parser + trainable_lemmatizer`) | Generated the same way |
| XLM-R NER config | Written for `spacy-transformers`; factory validated only if that extra is installed |
| CPU overfit diagnostic | Training-set learnability check; not held-out evaluation |
| Miniature fixtures | Converter/smoke/overfit only |
| Licensed full corpora | **Not bundled** |
| Trained weights | **Not bundled** |

Syntax training on [UD Urdu-UDTB](https://universaldependencies.org/treebanks/ur_udtb/index.html)
is a **CC BY-NC-SA 4.0** research track. It has no NER labels. Forms such as
`بات_چیت` are kept with underscores; that is reconstructed treebank surface,
not raw-text offsets.

## Commands

From this directory, with spaCy 3.8.x installed:

```bash
python -m pytest tests -q
python -m spacy project run smoke
python -m spacy project run overfit
python -m spacy project run prepare-syntax-fixtures
```

Real training (only after you add a licensed corpus under `assets/` and convert
it to `corpus/`):

```bash
python scripts/split.py assets/ner.jsonl corpus/splits --seed 0
python scripts/convert_ner.py corpus/splits/train.jsonl corpus/ner_train.spacy
python scripts/convert_ner.py corpus/splits/dev.jsonl corpus/ner_dev.spacy
python -m spacy project run debug-ner
python -m spacy project run train-ner
```

Transformer experiment (optional extras in `requirements-optional.txt`; GPU
recommended). This checkout's `init config` templates use
`spacy-transformers`, not `spacy-curated-transformers`:

```bash
python -m pip install spacy-transformers torch transformers
python -m spacy project run train-ner-trf
```

`FacebookAI/xlm-roberta-base` (MIT, includes Urdu, revision
`e73636d4f797dec63c3081bb6ed5c7b0bb3f2089`) is a comparison encoder, not a
claim that it is the best Urdu model. Window/stride is 128/96 with
`discard_oversize = false` so long documents are windowed rather than dropped.
This checkout's transformer templates use `spacy-transformers`; keep that
package optional and out of core spaCy.

U+060C `،` is a list/clause comma, not a thousands separator. ASCII `,` / `.`
and Arabic `٬` / `٫` remain numeric grouping/decimal characters for `like_num`,
matching `str.isdigit` for ASCII, Arabic-Indic, and Eastern Arabic-Indic
digits.

## Evaluation honesty

- NER: exact-span P/R/F and per-label scores from `spacy evaluate`.
- Syntax: POS/morph accuracy, UAS/LAS, lemma accuracy on **reference
  tokenization**.
- Raw-text end-to-end tokenization/sentence scores need a raw-text gold set;
  UD CoNLL-U conversion is not that set.
- Fixture smoke scores are not Urdu model quality.
- `project run overfit` memorizes `fixtures/ner_overfit.jsonl` with dropout 0.
  Report that ents_f as a learnability check, never as generalization.
- Official `split` fields are preserved. Cross-split duplicates are written to
  `contaminated.jsonl` instead of reshuffling a benchmark.
- Throughput, latency, memory, and model size should be measured with
  `nlp.pipe` on a real held-out sample, not the three-sentence fixture.

## Packaging

```bash
python -m spacy package training/ner/model-best packages --name ur_community_ner_sm --version 0.0.0
```

Install that wheel in a clean environment and `spacy.load("ur_community_ner_sm")`.
It will not appear in `spacy download`. Fill a model card with data licenses,
label inventory, metrics, and hardware **after** a real training run.
