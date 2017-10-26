#!/usr/bin/env python
# coding: utf8
"""
Example of training an additional entity type

This script shows how to add a new entity type to an existing pre-trained NER
model. To keep the example short and simple, only four sentences are provided
as examples. In practice, you'll need many more — a few hundred would be a
good start. You will also likely need to mix in examples of other entity
types, which might be obtained by running the entity recognizer over unlabelled
sentences, and adding their annotations to the training set.

The actual training is performed by looping over the examples, and calling
`nlp.entity.update()`. The `update()` method steps through the words of the
input. At each word, it makes a prediction. It then consults the annotations
provided on the GoldParse instance, to see whether it was right. If it was
wrong, it adjusts its weights so that the correct action will score higher
next time.

After training your model, you can save it to a directory. We recommend
wrapping models as Python packages, for ease of deployment.

For more details, see the documentation:
* Training: https://alpha.spacy.io/usage/training
* NER: https://alpha.spacy.io/usage/linguistic-features#named-entities

Developed for: spaCy 2.0.0a18
Last updated for: spaCy 2.0.0a18
"""
from __future__ import unicode_literals, print_function

import random
from pathlib import Path

import spacy
from spacy.gold import GoldParse, minibatch
from spacy.pipeline import NeuralEntityRecognizer


# new entity label
LABEL = 'ANIMAL'

# training data
TRAIN_DATA = [
    ("Horses are too tall and they pretend to care about your feelings",
     [(0, 6, 'ANIMAL')]),

    ("Do they bite?", []),

    ("horses are too tall and they pretend to care about your feelings",
     [(0, 6, 'ANIMAL')]),

    ("horses pretend to care about your feelings", [(0, 6, 'ANIMAL')]),

    ("they pretend to care about your feelings, those horses",
     [(48, 54, 'ANIMAL')]),

    ("horses?", [(0, 6, 'ANIMAL')])
]


def main(model=None, new_model_name='animal', output_dir=None):
    """Set up the pipeline and entity recognizer, and train the new entity.

    model (unicode): Model name to start off with. If None, a blank English
        Language class is created.
    new_model_name (unicode): Name of new model to create. Will be added to the
        model meta and prefixed by the language code, e.g. 'en_animal'.
    output_dir (unicode / Path): Optional output directory. If None, no model
        will be saved.
    """
    if model is not None:
        nlp = spacy.load(model)  # load existing spaCy model
        print("Loaded model '%s'" % model)
    else:
        nlp = spacy.blank('en')  # create blank Language class
        print("Created blank 'en' model")

    # Add entity recognizer to model if it's not in the pipeline
    if 'ner' not in nlp.pipe_names:
        nlp.add_pipe(NeuralEntityRecognizer(nlp.vocab))

    ner = nlp.get_pipe('ner')  # get entity recognizer
    ner.add_label(LABEL)   # add new entity label to entity recognizer

    # get names of other pipes to disable them during training
    other_pipes = [pipe for pipe in nlp.pipe_names if pipe != 'ner']
    with nlp.disable_pipes(*other_pipes) as disabled:  # only train NER
        random.seed(0)
        optimizer = nlp.begin_training(lambda: [])
        for itn in range(50):
            losses = {}
            gold_parses = get_gold_parses(nlp.make_doc, TRAIN_DATA)
            for batch in minibatch(gold_parses, size=3):
                docs, golds = zip(*batch)
                nlp.update(docs, golds, losses=losses, sgd=optimizer,
                           drop=0.35)
            print(losses)

    # test the trained model
    test_text = 'Do you like horses?'
    doc = nlp(test_text)
    print("Entities in '%s'" % test_text)
    for ent in doc.ents:
        print(ent.label_, ent.text)

    # save model to output directory
    if output_dir is not None:
        output_dir = Path(output_dir)
        if not output_dir.exists():
            output_dir.mkdir()
        nlp.meta['name'] = new_model_name  # rename model
        nlp.to_disk(output_dir)
        print("Saved model to", output_dir)

        # test the saved model
        print("Loading from", output_dir)
        nlp2 = spacy.load(output_dir)
        doc2 = nlp2(test_text)
        for ent in doc2.ents:
            print(ent.label_, ent.text)


def get_gold_parses(tokenizer, train_data):
    """Shuffle and create GoldParse objects.

    tokenizer (Tokenizer): Tokenizer to processs the raw text.
    train_data (list): The training data.
    YIELDS (tuple): (doc, gold) tuples.
    """
    random.shuffle(train_data)
    for raw_text, entity_offsets in train_data:
        doc = tokenizer(raw_text)
        gold = GoldParse(doc, entities=entity_offsets)
        yield doc, gold


if __name__ == '__main__':
    import plac
    plac.call(main)
