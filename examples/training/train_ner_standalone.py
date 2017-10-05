#!/usr/bin/env python
'''Example of training a named entity recognition system from scratch using spaCy

This example is written to be self-contained and reasonably transparent.
To achieve that, it duplicates some of spaCy's internal functionality.

Specifically, in this example, we don't use spaCy's built-in Language class to
wire together the Vocab, Tokenizer and EntityRecognizer. Instead, we write
our own simle Pipeline class, so that it's easier to see how the pieces
interact.

Input data:
https://www.lt.informatik.tu-darmstadt.de/fileadmin/user_upload/Group_LangTech/data/GermEval2014_complete_data.zip

Developed for: spaCy 1.7.1
Last tested for: spaCy 2.0.0a13
'''
from __future__ import unicode_literals, print_function
import plac
from pathlib import Path
import random
import json
import tqdm

from thinc.neural.optimizers import Adam
from thinc.neural.ops import NumpyOps

from spacy.vocab import Vocab
from spacy.pipeline import TokenVectorEncoder, NeuralEntityRecognizer
from spacy.tokenizer import Tokenizer
from spacy.tokens import Doc
from spacy.attrs import *
from spacy.gold import GoldParse
from spacy.gold import iob_to_biluo
from spacy.gold import minibatch
from spacy.scorer import Scorer
import spacy.util


try:
    unicode
except NameError:
    unicode = str


spacy.util.set_env_log(True)


def init_vocab():
    return Vocab(
        lex_attr_getters={
            LOWER: lambda string: string.lower(),
            NORM: lambda string: string.lower(),
            PREFIX: lambda string: string[0],
            SUFFIX: lambda string: string[-3:],
        })


class Pipeline(object):
    def __init__(self, vocab=None, tokenizer=None, entity=None):
        if vocab is None:
            vocab = init_vocab()
        if tokenizer is None:
            tokenizer = Tokenizer(vocab, {}, None, None, None)
        if entity is None:
            entity = NeuralEntityRecognizer(vocab)
        self.vocab = vocab
        self.tokenizer = tokenizer
        self.entity = entity
        self.pipeline = [self.entity]

    def begin_training(self):
        for model in self.pipeline:
            model.begin_training([])
        optimizer = Adam(NumpyOps(), 0.001)
        return optimizer

    def __call__(self, input_):
        doc = self.make_doc(input_)
        for process in self.pipeline:
            process(doc)
        return doc

    def make_doc(self, input_):
        if isinstance(input_, bytes):
            input_ = input_.decode('utf8')
        if isinstance(input_, unicode):
            return self.tokenizer(input_)
        else:
            return Doc(self.vocab, words=input_)

    def make_gold(self, input_, annotations):
        doc = self.make_doc(input_)
        gold = GoldParse(doc, entities=annotations)
        return gold

    def update(self, inputs, annots, sgd, losses=None, drop=0.):
        if losses is None:
            losses = {}
        docs = [self.make_doc(input_) for input_ in inputs]
        golds = [self.make_gold(input_, annot) for input_, annot in
                 zip(inputs, annots)]

        self.entity.update(docs, golds, drop=drop,
                           sgd=sgd, losses=losses)
        return losses

    def evaluate(self, examples):
        scorer = Scorer()
        for input_, annot in examples:
            gold = self.make_gold(input_, annot)
            doc = self(input_)
            scorer.score(doc, gold)
        return scorer.scores

    def to_disk(self, path):
        path = Path(path)
        if not path.exists():
            path.mkdir()
        elif not path.is_dir():
            raise IOError("Can't save pipeline to %s\nNot a directory" % path)
        self.vocab.to_disk(path / 'vocab')
        self.entity.to_disk(path / 'ner')

    def from_disk(self, path):
        path = Path(path)
        if not path.exists():
            raise IOError("Cannot load pipeline from %s\nDoes not exist" % path)
        if not path.is_dir():
            raise IOError("Cannot load pipeline from %s\nNot a directory" % path)
        self.vocab = self.vocab.from_disk(path / 'vocab')
        self.entity = self.entity.from_disk(path / 'ner')


def train(nlp, train_examples, dev_examples, nr_epoch=5):
    sgd = nlp.begin_training()
    print("Iter", "Loss", "P", "R", "F")
    for i in range(nr_epoch):
        random.shuffle(train_examples)
        losses = {}
        for batch in minibatch(tqdm.tqdm(train_examples, leave=False), size=8):
            inputs, annots = zip(*batch)
            nlp.update(list(inputs), list(annots), sgd, losses=losses)
        scores = nlp.evaluate(dev_examples)
        report_scores(i, losses['ner'], scores)
    scores = nlp.evaluate(dev_examples)
    report_scores(channels, i+1, loss, scores)


def report_scores(i, loss, scores):
    precision = '%.2f' % scores['ents_p']
    recall = '%.2f' % scores['ents_r']
    f_measure = '%.2f' % scores['ents_f']
    print('%d %s %s %s' % (int(loss), precision, recall, f_measure))


def read_examples(path):
    path = Path(path)
    with path.open() as file_:
        sents = file_.read().strip().split('\n\n')
        for sent in sents:
            sent = sent.strip()
            if not sent:
                continue
            tokens = sent.split('\n')
            while tokens and tokens[0].startswith('#'):
                tokens.pop(0)
            words = []
            iob = []
            for token in tokens:
                if token.strip():
                    pieces = token.split('\t')
                    words.append(pieces[1])
                    iob.append(pieces[2])
            yield words, iob_to_biluo(iob)


def get_labels(examples):
    labels = set()
    for words, tags in examples:
        for tag in tags:
            if '-' in tag:
                labels.add(tag.split('-')[1])
    return sorted(labels)


@plac.annotations(
    model_dir=("Path to save the model", "positional", None, Path),
    train_loc=("Path to your training data", "positional", None, Path),
    dev_loc=("Path to your development data", "positional", None, Path),
)
def main(model_dir, train_loc, dev_loc, nr_epoch=30):
    print(model_dir, train_loc, dev_loc)
    train_examples = list(read_examples(train_loc))
    dev_examples = read_examples(dev_loc)
    nlp = Pipeline()
    for label in get_labels(train_examples):
        nlp.entity.add_label(label)
        print("Add label", label)

    train(nlp, train_examples, list(dev_examples), nr_epoch)

    nlp.to_disk(model_dir)


if __name__ == '__main__':
    plac.call(main)
