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
Last tested for: spaCy 1.7.1
'''
from __future__ import unicode_literals, print_function
import plac
from pathlib import Path
import random
import json

import spacy.orth as orth_funcs
from spacy.vocab import Vocab
from spacy.pipeline import BeamEntityRecognizer
from spacy.pipeline import EntityRecognizer
from spacy.tokenizer import Tokenizer
from spacy.tokens import Doc
from spacy.attrs import *
from spacy.gold import GoldParse
from spacy.gold import _iob_to_biluo as iob_to_biluo
from spacy.scorer import Scorer

try:
    unicode
except NameError:
    unicode = str


def init_vocab():
    return Vocab(
        lex_attr_getters={
            LOWER: lambda string: string.lower(),
            SHAPE: orth_funcs.word_shape,
            PREFIX: lambda string: string[0],
            SUFFIX: lambda string: string[-3:],
            CLUSTER: lambda string: 0,
            IS_ALPHA: orth_funcs.is_alpha,
            IS_ASCII: orth_funcs.is_ascii,
            IS_DIGIT: lambda string: string.isdigit(),
            IS_LOWER: orth_funcs.is_lower,
            IS_PUNCT: orth_funcs.is_punct,
            IS_SPACE: lambda string: string.isspace(),
            IS_TITLE: orth_funcs.is_title,
            IS_UPPER: orth_funcs.is_upper,
            IS_STOP: lambda string: False,
            IS_OOV: lambda string: True
        })


def save_vocab(vocab, path):
    path = Path(path)
    if not path.exists():
        path.mkdir()
    elif not path.is_dir():
        raise IOError("Can't save vocab to %s\nNot a directory" % path)
    with (path / 'strings.json').open('w') as file_:
        vocab.strings.dump(file_)
    vocab.dump((path / 'lexemes.bin').as_posix())


def load_vocab(path):
    path = Path(path)
    if not path.exists():
        raise IOError("Cannot load vocab from %s\nDoes not exist" % path)
    if not path.is_dir():
        raise IOError("Cannot load vocab from %s\nNot a directory" % path)
    return Vocab.load(path)


def init_ner_model(vocab, features=None):
    if features is None:
        features = tuple(EntityRecognizer.feature_templates)
    return EntityRecognizer(vocab, features=features)


def save_ner_model(model, path):
    path = Path(path)
    if not path.exists():
        path.mkdir()
    if not path.is_dir():
        raise IOError("Can't save model to %s\nNot a directory" % path)
    model.model.dump((path / 'model').as_posix())
    with (path / 'config.json').open('w') as file_:
        data = json.dumps(model.cfg)
        if not isinstance(data, unicode):
            data = data.decode('utf8')
        file_.write(data)


def load_ner_model(vocab, path):
    return EntityRecognizer.load(path, vocab)


class Pipeline(object):
    @classmethod
    def load(cls, path):
        path = Path(path)
        if not path.exists():
            raise IOError("Cannot load pipeline from %s\nDoes not exist" % path)
        if not path.is_dir():
            raise IOError("Cannot load pipeline from %s\nNot a directory" % path)
        vocab = load_vocab(path)
        tokenizer = Tokenizer(vocab, {}, None, None, None)
        ner_model = load_ner_model(vocab, path / 'ner')
        return cls(vocab, tokenizer, ner_model)

    def __init__(self, vocab=None, tokenizer=None, entity=None):
        if vocab is None:
            vocab = init_vocab()
        if tokenizer is None:
            tokenizer = Tokenizer(vocab, {}, None, None, None)
        if entity is None:
            entity = init_ner_model(self.vocab)
        self.vocab = vocab
        self.tokenizer = tokenizer
        self.entity = entity
        self.pipeline = [self.entity]

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

    def update(self, input_, annot):
        doc = self.make_doc(input_)
        gold = self.make_gold(input_, annot)
        for ner in gold.ner:
            if ner not in (None, '-', 'O'):
                action, label = ner.split('-', 1)
                self.entity.add_label(label)
        return self.entity.update(doc, gold)

    def evaluate(self, examples):
        scorer = Scorer()
        for input_, annot in examples:
            gold = self.make_gold(input_, annot)
            doc = self(input_)
            scorer.score(doc, gold)
        return scorer.scores

    def average_weights(self):
        self.entity.model.end_training()

    def save(self, path):
        path = Path(path)
        if not path.exists():
            path.mkdir()
        elif not path.is_dir():
            raise IOError("Can't save pipeline to %s\nNot a directory" % path)
        save_vocab(self.vocab, path / 'vocab')
        save_ner_model(self.entity, path / 'ner')


def train(nlp, train_examples, dev_examples, ctx, nr_epoch=5):
    next_epoch = train_examples
    print("Iter", "Loss", "P", "R", "F")
    for i in range(nr_epoch):
        this_epoch = next_epoch
        next_epoch = []
        loss = 0
        for input_, annot in this_epoch:
            loss += nlp.update(input_, annot)
            if (i+1) < nr_epoch:
                next_epoch.append((input_, annot))
        random.shuffle(next_epoch)
        scores = nlp.evaluate(dev_examples)
        report_scores(i, loss, scores)
    nlp.average_weights()
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
            if not sent.strip():
                continue
            tokens = sent.split('\n')
            while tokens and tokens[0].startswith('#'):
                tokens.pop(0)
            words = []
            iob = []
            for token in tokens:
                if token.strip():
                    pieces = token.split()
                    words.append(pieces[1])
                    iob.append(pieces[2])
            yield words, iob_to_biluo(iob)


@plac.annotations(
    model_dir=("Path to save the model", "positional", None, Path),
    train_loc=("Path to your training data", "positional", None, Path),
    dev_loc=("Path to your development data", "positional", None, Path),
)
def main(model_dir=Path('/home/matt/repos/spaCy/spacy/data/de-1.0.0'),
        train_loc=None, dev_loc=None, nr_epoch=30):
    
    train_examples = read_examples(train_loc)
    dev_examples = read_examples(dev_loc)
    nlp = Pipeline.load(model_dir)

    train(nlp, train_examples, list(dev_examples), ctx, nr_epoch)

    nlp.save(model_dir)


if __name__ == '__main__':
    main()
