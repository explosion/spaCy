## Examples of textcat training data

spacy JSON training files were generated from JSONL with:

```
python textcatjsonl_to_trainjson.py -m en file.jsonl .
```

`cooking.json` is an example with mutually-exclusive classes with two labels:

* `baking`
* `not_baking`

`jigsaw-toxic-comment.json` is an example with multiple labels per instance:

* `insult`
* `obscene`
* `severe_toxic`
* `toxic`

### Data Sources

* `cooking.jsonl`: https://cooking.stackexchange.com. The meta IDs link to the
  original question as `https://cooking.stackexchange.com/questions/ID`, e.g.,
  `https://cooking.stackexchange.com/questions/2` for the first instance.
* `jigsaw-toxic-comment.jsonl`: [Jigsaw Toxic Comments Classification
  Challenge](https://www.kaggle.com/c/jigsaw-toxic-comment-classification-challenge)

### Data Licenses

* `cooking.jsonl`: CC BY-SA 4.0 ([`CC_BY-SA-4.0.txt`](CC_BY-SA-4.0.txt))
* `jigsaw-toxic-comment.jsonl`:
    * text: CC BY-SA 3.0 ([`CC_BY-SA-3.0.txt`](CC_BY-SA-3.0.txt))
    * annotation: CC0 ([`CC0.txt`](CC0.txt))
