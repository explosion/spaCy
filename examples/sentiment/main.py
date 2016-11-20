from __future__ import unicode_literals
from __future__ import print_function

import plac
from pathlib import Path
import random

import spacy.en
import model


try:
    import cPickle as pickle
except ImportError:
    import pickle


def read_data(nlp, data_dir):
    for subdir, label in (('pos', 1), ('neg', 0)):
        for filename in (data_dir / subdir).iterdir():
            text = filename.open().read()
            doc = nlp(text)
            yield doc, label


def partition(examples, split_size):
    examples = list(examples)
    random.shuffle(examples)
    n_docs = len(examples)
    split = int(n_docs * split_size)
    return examples[:split], examples[split:]


class Dataset(object):
    def __init__(self, nlp, data_dir, batch_size=24):
        self.batch_size = batch_size
        self.train, self.dev = partition(read_data(nlp, Path(data_dir)), 0.8)
        print("Read %d train docs" % len(self.train))
        print("Pos. Train: ", sum(eg[1] == 1 for eg in self.train))
        print("Read %d dev docs" % len(self.dev))
        print("Neg. Dev: ", sum(eg[1] == 1 for eg in self.dev))

    def batches(self, data):
        for i in range(0, len(data), self.batch_size):
            yield data[i : i + self.batch_size]


def model_writer(out_dir, name):
    def save_model(epoch, params):
        out_path = out_dir / name.format(epoch=epoch)
        pickle.dump(params, out_path.open('wb'))    
    return save_model


@plac.annotations(
    data_dir=("Data directory", "positional", None, Path),
    vocab_size=("Number of words to fine-tune", "option", "w", int),
    n_iter=("Number of iterations (epochs)", "option", "i", int),
    vector_len=("Size of embedding vectors", "option", "e", int),
    hidden_len=("Size of hidden layers", "option", "H", int),
    depth=("Depth", "option", "d", int),
    drop_rate=("Drop-out rate", "option", "r", float),
    rho=("Regularization penalty", "option", "p", float),
    batch_size=("Batch size", "option", "b", int),
    out_dir=("Model directory", "positional", None, Path)
)
def main(data_dir, out_dir, n_iter=10, vector_len=300, vocab_size=20000,
         hidden_len=300, depth=3, drop_rate=0.3, rho=1e-4, batch_size=24):
    print("Loading")
    nlp = spacy.en.English(parser=False)
    dataset = Dataset(nlp, data_dir / 'train', batch_size)
    print("Training")
    network = model.train(dataset, vector_len, hidden_len, 2, vocab_size, depth,
                          drop_rate, rho, n_iter,
                          model_writer(out_dir, 'model_{epoch}.pickle'))
    score = model.Scorer()
    print("Evaluating")
    for doc, label in read_data(nlp, data_dir / 'test'):
        word_ids, embeddings = model.get_words(doc, 0.0, vocab_size)
        guess = network.forward(word_ids, embeddings)
        score += guess == label
    print(score)
    

if __name__ == '__main__':
    plac.call(main)
