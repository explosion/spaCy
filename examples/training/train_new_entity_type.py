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
* Training the Named Entity Recognizer: https://spacy.io/docs/usage/train-ner
* Saving and loading models: https://spacy.io/docs/usage/saving-loading

Developed for: spaCy 1.7.6
Last tested for: spaCy 1.7.6
"""
from __future__ import unicode_literals, print_function

import random
from pathlib import Path
import random

import spacy
from spacy.gold import GoldParse
from spacy.tagger import Tagger


def train_ner(nlp, train_data, output_dir):
    # Add new words to vocab
    for raw_text, _ in train_data:
        doc = nlp.make_doc(raw_text)
        for word in doc:
            _ = nlp.vocab[word.orth]
    random.seed(0)
    # You may need to change the learning rate. It's generally difficult to
    # guess what rate you should set, especially when you have limited data.
    nlp.entity.model.learn_rate = 0.001
    for itn in range(1000):
        random.shuffle(train_data)
        loss = 0.
        for raw_text, entity_offsets in train_data:
            doc = nlp.make_doc(raw_text)
            gold = GoldParse(doc, entities=entity_offsets)
            # By default, the GoldParse class assumes that the entities
            # described by offset are complete, and all other words should
            # have the tag 'O'. You can tell it to make no assumptions
            # about the tag of a word by giving it the tag '-'.
            # However, this allows a trivial solution to the current
            # learning problem: if words are either 'any tag' or 'ANIMAL',
            # the model can learn that all words can be tagged 'ANIMAL'.
            #for i in range(len(gold.ner)):
                #if not gold.ner[i].endswith('ANIMAL'):
                #    gold.ner[i] = '-'
            nlp.tagger(doc)
            # As of 1.9, spaCy's parser now lets you supply a dropout probability
            # This might help the model generalize better from only a few
            # examples.
            loss += nlp.entity.update(doc, gold, drop=0.9)
        if loss == 0:
            break
    # This step averages the model's weights. This may or may not be good for
    # your situation --- it's empirical.
    nlp.end_training()
    if output_dir:
        if not output_dir.exists():
            output_dir.mkdir()
        nlp.save_to_directory(output_dir)


def main(model_name, output_directory=None):
    print("Loading initial model", model_name)
    nlp = spacy.load(model_name)
    if output_directory is not None:
        output_directory = Path(output_directory)

    train_data = [
        (
            "Horses are too tall and they pretend to care about your feelings",
            [(0, 6, 'ANIMAL')],
        ),
        (
            "horses are too tall and they pretend to care about your feelings",
            [(0, 6, 'ANIMAL')]
        ),
        (
            "horses pretend to care about your feelings",
            [(0, 6, 'ANIMAL')]
        ),
        (
            "they pretend to care about your feelings, those horses",
            [(48, 54, 'ANIMAL')]
        ),
        (
            "horses?",
            [(0, 6, 'ANIMAL')]
        )

    ]
    nlp.entity.add_label('ANIMAL')
    train_ner(nlp, train_data, output_directory)

    # Test that the entity is recognized
    doc = nlp('Do you like horses?')
    print("Ents in 'Do you like horses?':")
    for ent in doc.ents:
        print(ent.label_, ent.text)
    if output_directory:
        print("Loading from", output_directory)
        nlp2 = spacy.load('en', path=output_directory)
        nlp2.entity.add_label('ANIMAL')
        doc2 = nlp2('Do you like horses?')
        for ent in doc2.ents:
            print(ent.label_, ent.text)


if __name__ == '__main__':
    import plac
    plac.call(main)
