'''Train a multi-label convolutional neural network text classifier,
using the spacy.pipeline.TextCategorizer component. The model is then added
to spacy.pipeline, and predictions are available at `doc.cats`.
'''
from __future__ import unicode_literals
import plac
import random
import tqdm

from thinc.neural.optimizers import Adam
from thinc.neural.ops import NumpyOps
import thinc.extra.datasets

import spacy.lang.en
from spacy.gold import GoldParse, minibatch
from spacy.util import compounding
from spacy.pipeline import TextCategorizer

# TODO: Remove this once we're not supporting models trained with thinc <6.9.0
import thinc.neural._classes.layernorm
thinc.neural._classes.layernorm.set_compat_six_eight(False)


def train_textcat(tokenizer, textcat,
                  train_texts, train_cats, dev_texts, dev_cats,
                  n_iter=20):
    '''
    Train the TextCategorizer without associated pipeline.
    '''
    textcat.begin_training()
    optimizer = Adam(NumpyOps(), 0.001)
    train_docs = [tokenizer(text) for text in train_texts]
    train_gold = [GoldParse(doc, cats=cats) for doc, cats in
                  zip(train_docs, train_cats)]
    train_data = list(zip(train_docs, train_gold))
    batch_sizes = compounding(4., 128., 1.001)
    for i in range(n_iter):
        losses = {}
        # Progress bar and minibatching
        batches = minibatch(tqdm.tqdm(train_data, leave=False), size=batch_sizes)
        for batch in batches:
            docs, golds = zip(*batch)
            textcat.update(docs, golds, sgd=optimizer, drop=0.2,
                losses=losses)
        with textcat.model.use_params(optimizer.averages):
            scores = evaluate(tokenizer, textcat, dev_texts, dev_cats)
        yield losses['textcat'], scores


def evaluate(tokenizer, textcat, texts, cats):
    docs = (tokenizer(text) for text in texts)
    tp = 1e-8 # True positives
    fp = 1e-8 # False positives
    fn = 1e-8 # False negatives
    tn = 1e-8 # True negatives
    for i, doc in enumerate(textcat.pipe(docs)):
        gold = cats[i]
        for label, score in doc.cats.items():
            if label not in gold:
                continue
            if score >= 0.5 and gold[label] >= 0.5:
                tp += 1.
            elif score >= 0.5 and gold[label] < 0.5:
                fp += 1.
            elif score < 0.5 and gold[label] < 0.5:
                tn += 1
            elif score < 0.5 and gold[label] >= 0.5:
                fn += 1
    precis = tp / (tp + fp)
    recall = tp / (tp + fn)
    fscore = 2 * (precis * recall) / (precis + recall)
    return {'textcat_p': precis, 'textcat_r': recall, 'textcat_f': fscore}


def load_data(limit=0):
    # Partition off part of the train data --- avoid running experiments
    # against test.
    train_data, _ = thinc.extra.datasets.imdb()

    random.shuffle(train_data)
    train_data = train_data[-limit:]

    texts, labels = zip(*train_data)
    cats = [{'POSITIVE': bool(y)} for y in labels]

    split = int(len(train_data) * 0.8)

    train_texts = texts[:split]
    train_cats = cats[:split]
    dev_texts = texts[split:]
    dev_cats = cats[split:]
    return (train_texts, train_cats), (dev_texts, dev_cats)


def main(model_loc=None):
    nlp = spacy.lang.en.English()
    tokenizer = nlp.tokenizer
    textcat = TextCategorizer(tokenizer.vocab, labels=['POSITIVE'])

    print("Load IMDB data")
    (train_texts, train_cats), (dev_texts, dev_cats) = load_data(limit=2000)

    print("Itn.\tLoss\tP\tR\tF")
    progress = '{i:d} {loss:.3f} {textcat_p:.3f} {textcat_r:.3f} {textcat_f:.3f}'

    for i, (loss, scores) in enumerate(train_textcat(tokenizer, textcat,
                                       train_texts, train_cats,
                                       dev_texts, dev_cats, n_iter=20)):
        print(progress.format(i=i, loss=loss, **scores))
    # How to save, load and use
    nlp.pipeline.append(textcat)
    if model_loc is not None:
        nlp.to_disk(model_loc)

        nlp = spacy.load(model_loc)
        doc = nlp(u'This movie sucked!')
        print(doc.cats)


if __name__ == '__main__':
    plac.call(main)
