from __future__ import division, unicode_literals, print_function
import spacy

import plac
from pathlib import Path

from spacy_hook import get_embeddings, get_word_ids
from spacy_hook import create_similarity_pipeline

from keras_decomposable_attention import build_model

def train(model_dir, train_loc, dev_loc, shape, settings):
    print("Loading spaCy")
    nlp = spacy.load('en', tagger=False, parser=False, entity=False, matcher=False)
    print("Compiling network")
    model = build_model(get_embeddings(nlp.vocab), shape, settings)
    print("Processing texts...")
    train_X = get_features(list(nlp.pipe(train_texts)))
    dev_X = get_features(list(nlp.pipe(dev_texts)))

    model.fit(
        train_X,
        train_labels,
        validation_data=(dev_X, dev_labels),
        nb_epoch=settings['nr_epoch'],
        batch_size=settings['batch_size'])


def evaluate(model_dir, dev_loc):
    nlp = spacy.load('en', path=model_dir,
            tagger=False, parser=False, entity=False, matcher=False,
            create_pipeline=create_similarity_pipeline)
    n = 0
    correct = 0
    for (text1, text2), label in zip(dev_texts, dev_labels):
        doc1 = nlp(text1)
        doc2 = nlp(text2)
        sim = doc1.similarity(doc2)
        if bool(sim >= 0.5) == label:
            correct += 1
        n += 1
    return correct, total


def demo(model_dir):
    nlp = spacy.load('en', path=model_dir,
            tagger=False, parser=False, entity=False, matcher=False,
            create_pipeline=create_similarity_pipeline)
    doc1 = nlp(u'Worst fries ever! Greasy and horrible...')
    doc2 = nlp(u'The milkshakes are good. The fries are bad.')
    print('doc1.similarity(doc2)', doc1.similarity(doc2))
    sent1a, sent1b = doc1.sents
    print('sent1a.similarity(sent1b)', sent1a.similarity(sent1b))
    print('sent1a.similarity(doc2)', sent1a.similarity(doc2))
    print('sent1b.similarity(doc2)', sent1b.similarity(doc2))


LABELS = {'entailment': 0, 'contradiction': 1, 'neutral': 2}
def read_snli(loc):
    with open(loc) as file_:
        for line in file_:
            eg = json.loads(line)
            label = eg['gold_label']
            if label == '-':
                continue
            text1 = eg['sentence1']
            text2 = eg['sentence2']
            yield text1, text2, LABELS[label]


@plac.annotations(
    mode=("Mode to execute", "positional", None, str, ["train", "evaluate", "demo"]),
    model_dir=("Path to spaCy model directory", "positional", None, Path),
    train_loc=("Path to training data", "positional", None, Path),
    dev_loc=("Path to development data", "positional", None, Path),
    max_length=("Length to truncate sentences", "option", "L", int),
    nr_hidden=("Number of hidden units", "option", "H", int),
    dropout=("Dropout level", "option", "d", float),
    learn_rate=("Learning rate", "option", "e", float),
    batch_size=("Batch size for neural network training", "option", "b", float),
    nr_epoch=("Number of training epochs", "option", "i", float)
)
def main(mode, model_dir, train_loc, dev_loc,
        max_length=100,
        nr_hidden=100,
        dropout=0.2,
        learn_rate=0.001,
        batch_size=100,
        nr_epoch=5):
    shape = (max_length, nr_hidden, 3)
    settings = {
        'lr': learn_rate,
        'dropout': dropout,
        'batch_size': batch_size,
        'nr_epoch': nr_epoch
    }
    if mode == 'train':
        train(model_dir, train_loc, dev_loc, shape, settings)
    elif mode == 'evaluate':
        evaluate(model_dir, dev_loc)
    else:
        demo(model_dir)


if __name__ == '__main__':
    plac.call(main)
