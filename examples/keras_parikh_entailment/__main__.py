from __future__ import division, unicode_literals, print_function
import spacy

import plac
from pathlib import Path
import ujson as json
import numpy
from keras.utils.np_utils import to_categorical

from spacy_hook import get_embeddings, get_word_ids
from spacy_hook import create_similarity_pipeline

from keras_decomposable_attention import build_model


def train(model_dir, train_loc, dev_loc, shape, settings):
    train_texts1, train_texts2, train_labels = read_snli(train_loc)
    dev_texts1, dev_texts2, dev_labels = read_snli(dev_loc)
    
    print("Loading spaCy")
    nlp = spacy.load('en')
    print("Compiling network")
    model = build_model(get_embeddings(nlp.vocab), shape, settings)
    print("Processing texts...")
    Xs = []    
    for texts in (train_texts1, train_texts2, dev_texts1, dev_texts2):
        Xs.append(get_word_ids(list(nlp.pipe(texts, n_threads=20, batch_size=20000)),
                         max_length=shape[0],
                         rnn_encode=settings['gru_encode'],
                         tree_truncate=settings['tree_truncate']))
    train_X1, train_X2, dev_X1, dev_X2 = Xs
    print(settings)
    model.fit(
        [train_X1, train_X2],
        train_labels,
        validation_data=([dev_X1, dev_X2], dev_labels),
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
def read_snli(path):
    texts1 = []
    texts2 = []
    labels = []
    with path.open() as file_:
        for line in file_:
            eg = json.loads(line)
            label = eg['gold_label']
            if label == '-':
                continue
            texts1.append(eg['sentence1'])
            texts2.append(eg['sentence2'])
            labels.append(LABELS[label])
    return texts1, texts2, to_categorical(numpy.asarray(labels, dtype='int32'))


@plac.annotations(
    mode=("Mode to execute", "positional", None, str, ["train", "evaluate", "demo"]),
    model_dir=("Path to spaCy model directory", "positional", None, Path),
    train_loc=("Path to training data", "positional", None, Path),
    dev_loc=("Path to development data", "positional", None, Path),
    max_length=("Length to truncate sentences", "option", "L", int),
    nr_hidden=("Number of hidden units", "option", "H", int),
    dropout=("Dropout level", "option", "d", float),
    learn_rate=("Learning rate", "option", "e", float),
    batch_size=("Batch size for neural network training", "option", "b", int),
    nr_epoch=("Number of training epochs", "option", "i", int),
    tree_truncate=("Truncate sentences by tree distance", "flag", "T", bool),
    gru_encode=("Encode sentences with bidirectional GRU", "flag", "E", bool),
)
def main(mode, model_dir, train_loc, dev_loc,
        tree_truncate=False,
        gru_encode=False,
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
        'nr_epoch': nr_epoch,
        'tree_truncate': tree_truncate,
        'gru_encode': gru_encode
    }
    if mode == 'train':
        train(model_dir, train_loc, dev_loc, shape, settings)
    elif mode == 'evaluate':
        evaluate(model_dir, dev_loc)
    else:
        demo(model_dir)

if __name__ == '__main__':
    plac.call(main)
