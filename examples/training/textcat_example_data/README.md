## Examples of textcat training data

spacy JSON training files were generated from JSONL with:

```
python textcatjsonl_to_trainjson.py -m en file.jsonl .
```

`cooking.json` is an example with mutually-exclusive classes with two labels:
* `baking`
* `not_baking`

`jigsaw-toxic-comment.json` is an example with multiple labels per instances:
* `identity_hate`
* `insult`
* `obscene`
* `severe_toxic`
* `threat`
* `toxic`

Example data sources:

* `cooking.jsonl`: https://cooking.stackexchange.com
* `jigsaw-toxic-comment.jsonl`: [Jigsaw Toxic Comments Classification Challenge](https://www.kaggle.com/c/jigsaw-toxic-comment-classification-challenge)
