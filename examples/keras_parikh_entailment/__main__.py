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

try:
    import cPickle as pickle
except ImportError:
    import pickle


def train(train_loc, dev_loc, shape, settings):
    train_texts1, train_texts2, train_labels = read_snli(train_loc)
    dev_texts1, dev_texts2, dev_labels = read_snli(dev_loc)

    print("Loading spaCy")
    nlp = spacy.load('en')
    assert nlp.path is not None
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
    if not (nlp.path / 'similarity').exists():
        (nlp.path / 'similarity').mkdir()
    print("Saving to", nlp.path / 'similarity')
    weights = model.get_weights()
    with (nlp.path / 'similarity' / 'model').open('wb') as file_:
        pickle.dump(weights[1:], file_)
    with (nlp.path / 'similarity' / 'config.json').open('wb') as file_:
        file_.write(model.to_json())


def evaluate(model_dir, dev_loc):
    dev_texts1, dev_texts2, dev_labels = read_snli(dev_loc)
    nlp = spacy.load('en',
            create_pipeline=create_similarity_pipeline)
    total = 0.
    correct = 0.
    for text1, text2, label in zip(dev_texts1, dev_texts2, dev_labels):
        doc1 = nlp(text1)
        doc2 = nlp(text2)
        sim = doc1.similarity(doc2)
        if sim.argmax() == label.argmax():
            correct += 1
        total += 1
    return correct, total


def demo():
    nlp = spacy.load('en',
            create_pipeline=create_similarity_pipeline)
    doc1 = nlp(u'What were the best crime fiction books in 2016?')
    doc2 = nlp(
        u'What should I read that was published last year? I like crime stories.')
    print(doc1)
    print(doc2)
    print("Similarity", doc1.similarity(doc2))


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
def main(mode, train_loc, dev_loc,
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
        train(train_loc, dev_loc, shape, settings)
    elif mode == 'evaluate':
        correct, total = evaluate(dev_loc)
        print(correct, '/', total, correct / total)
    else:
        demo()

if __name__ == '__main__':
    plac.call(main)
