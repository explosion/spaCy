from __future__ import unicode_literals, print_function
import json
import pathlib
import random

import spacy
from spacy.pipeline import EntityRecognizer
from spacy.gold import GoldParse
from spacy.tagger import Tagger

 
try:
    unicode
except:
    unicode = str


def train_ner(nlp, train_data, output_dir):
    # Add new words to vocab.
    for raw_text, _ in train_data:
        doc = nlp.make_doc(raw_text)
        for word in doc:
            _ = nlp.vocab[word.orth]

    for itn in range(20):
        random.shuffle(train_data)
        for raw_text, entity_offsets in train_data:
            gold = GoldParse(doc, entities=entity_offsets)
            doc = nlp.make_doc(raw_text)
            nlp.tagger(doc)
            loss = nlp.entity.update(doc, gold)
    nlp.save_to_directory(output_dir)
    #nlp.end_training(output_dir)


def main(model_name, output_directory=None):
    nlp = spacy.load(model_name)

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
        )
    ]
    nlp.entity.add_label('ANIMAL')
    if output_directory is not None:
        output_directory = pathlib.Path(output_directory)
    ner = train_ner(nlp, train_data, output_directory)

    doc = nlp('Do you like horses?')
    for ent in doc.ents:
        print(ent.label_, ent.text)
    nlp2 = spacy.load('en', path=output_directory)
    nlp2.entity.add_label('ANIMAL')
    doc2 = nlp2('Do you like horses?')
    for ent in doc2.ents:
        print(ent.label_, ent.text)


if __name__ == '__main__':
    import plac
    plac.call(main)
