#!/usr/bin/env python
# coding: utf8
"""Example of multi-processing with Joblib. Here, we're exporting
part-of-speech-tagged, true-cased, (very roughly) sentence-separated text, with
each "sentence" on a newline, and spaces between tokens. Data is loaded from
the IMDB movie reviews dataset and will be loaded automatically via Thinc's
built-in dataset loader.

Compatible with: spaCy v2.0.0+
"""
from __future__ import print_function, unicode_literals
from toolz import partition_all
from pathlib import Path
from joblib import Parallel, delayed
import thinc.extra.datasets
import plac
import spacy


@plac.annotations(
    output_dir=("Output directory", "positional", None, Path),
    model=("Model name (needs tagger)", "positional", None, str),
    n_jobs=("Number of workers", "option", "n", int),
    batch_size=("Batch-size for each process", "option", "b", int),
    limit=("Limit of entries from the dataset", "option", "l", int))
def main(output_dir, model='en_core_web_sm', n_jobs=4, batch_size=1000,
         limit=10000):
    nlp = spacy.load(model)  # load spaCy model
    print("Loaded model '%s'" % model)
    if not output_dir.exists():
        output_dir.mkdir()
    # load and pre-process the IMBD dataset
    print("Loading IMDB data...")
    data, _ = thinc.extra.datasets.imdb()
    texts, _ = zip(*data[-limit:])
    print("Processing texts...")
    partitions = partition_all(batch_size, texts)
    executor = Parallel(n_jobs=n_jobs)
    do = delayed(transform_texts)
    tasks = (do(nlp, i, batch, output_dir)
             for i, batch in enumerate(partitions))
    executor(tasks)


def transform_texts(nlp, batch_id, texts, output_dir):
    print(nlp.pipe_names)
    out_path = Path(output_dir) / ('%d.txt' % batch_id)
    if out_path.exists():  # return None in case same batch is called again
        return None
    print('Processing batch', batch_id)
    with out_path.open('w', encoding='utf8') as f:
        for doc in nlp.pipe(texts):
            f.write(' '.join(represent_word(w) for w in doc if not w.is_space))
            f.write('\n')
    print('Saved {} texts to {}.txt'.format(len(texts), batch_id))


def represent_word(word):
    text = word.text
    # True-case, i.e. try to normalize sentence-initial capitals.
    # Only do this if the lower-cased form is more probable.
    if text.istitle() and is_sent_begin(word) \
       and word.prob < word.doc.vocab[text.lower()].prob:
        text = text.lower()
    return text + '|' + word.tag_


def is_sent_begin(word):
    if word.i == 0:
        return True
    elif word.i >= 2 and word.nbor(-1).text in ('.', '!', '?', '...'):
        return True
    else:
        return False


if __name__ == '__main__':
    plac.call(main)
