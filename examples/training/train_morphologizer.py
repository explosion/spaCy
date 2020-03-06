#!/usr/bin/env python
# coding: utf8
"""
A simple example for training a morphologizer. For more details, see
the documentation:
* Training: https://spacy.io/usage/training

Compatible with: spaCy v3.0.0+
Last tested with: v3.0.0
"""
from __future__ import unicode_literals, print_function

import plac
import random
from pathlib import Path
import spacy
from spacy.util import minibatch, compounding
from spacy.morphology import Morphology


# Usually you'll read this in, of course. Data formats vary. Ensure your
# strings are unicode and that the number of tags assigned matches spaCy's
# tokenization. If not, you can always add a 'words' key to the annotations
# that specifies the gold-standard tokenization, e.g.:
# ("Eatblueham", {'words': ['Eat', 'blue', 'ham'], 'tags': ['V', 'J', 'N']})
TRAIN_DATA = [
    (
        "I like green eggs",
        {
            "morphs": [
                "PronType=Prs|Person=1",
                "VerbForm=Fin",
                "Degree=Pos",
                "Number=Plur",
            ],
            "pos": ["PRON", "VERB", "ADJ", "NOUN"],
        },
    ),
    (
        "Eat blue ham",
        {
            "morphs": ["VerbForm=Inf", "Degree=Pos", "Number=Sing"],
            "pos": ["VERB", "ADJ", "NOUN"],
        },
    ),
    (
        "She was blue",
        {
            "morphs": ["PronType=Prs|Person=3", "VerbForm=Fin", "Degree=Pos"],
            "pos": ["PRON", "VERB", "ADJ"],
        },
    ),
    (
        "He was blue today",
        {
            "morphs": ["PronType=Prs|Person=3", "VerbForm=Fin", "Degree=Pos", ""],
            "pos": ["PRON", "VERB", "ADJ", "ADV"],
        },
    ),
]

# The POS tags are optional, set `without_pos_tags = True` to omit them for
# this example:
without_pos_tags = True
if without_pos_tags:
    for i in range(len(TRAIN_DATA)):
        del TRAIN_DATA[i][1]["pos"]


@plac.annotations(
    lang=("ISO Code of language to use", "option", "l", str),
    output_dir=("Optional output directory", "option", "o", Path),
    n_iter=("Number of training iterations", "option", "n", int),
)
def main(lang="en", output_dir=None, n_iter=25):
    """Create a new model, set up the pipeline and train the tagger. In order to
    train the tagger with a custom tag map, we're creating a new Language
    instance with a custom vocab.
    """
    nlp = spacy.blank(lang)
    # add the tagger to the pipeline
    # nlp.create_pipe works for built-ins that are registered with spaCy
    morphologizer = nlp.create_pipe("morphologizer")
    nlp.add_pipe(morphologizer)

    # add labels
    for _, annotations in TRAIN_DATA:
        morph_labels = annotations.get("morphs")
        pos_labels = annotations.get("pos", [""] * len(annotations.get("morphs")))
        assert len(morph_labels) == len(pos_labels)
        for morph, pos in zip(morph_labels, pos_labels):
            morph_dict = Morphology.feats_to_dict(morph)
            if pos:
                morph_dict["POS"] = pos
            morph = Morphology.dict_to_feats(morph_dict)
            morphologizer.add_label(morph)

    optimizer = nlp.begin_training()
    for i in range(n_iter):
        random.shuffle(TRAIN_DATA)
        losses = {}
        # batch up the examples using spaCy's minibatch
        batches = minibatch(TRAIN_DATA, size=compounding(4.0, 32.0, 1.001))
        for batch in batches:
            nlp.update(batch, sgd=optimizer, losses=losses)
        print("Losses", losses)

    # test the trained model
    test_text = "I like blue eggs"
    doc = nlp(test_text)
    print("Morphs", [(t.text, t.morph) for t in doc])

    # save model to output directory
    if output_dir is not None:
        output_dir = Path(output_dir)
        if not output_dir.exists():
            output_dir.mkdir()
        nlp.to_disk(output_dir)
        print("Saved model to", output_dir)

        # test the save model
        print("Loading from", output_dir)
        nlp2 = spacy.load(output_dir)
        doc = nlp2(test_text)
        print("Morphs", [(t.text, t.morph) for t in doc])


if __name__ == "__main__":
    plac.call(main)

# Expected output:
# Morphs [('I', POS=PRON|Person=1|PronType=Prs), ('like', POS=VERB|VerbForm=Fin), ('blue', Degree=Pos|POS=ADJ), ('eggs', Number=Plur|POS=NOUN)]
