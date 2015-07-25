#!/usr/bin/env python

from __future__ import unicode_literals

import plac
import joblib
from os import path
import os
import bz2
import ujson
import codecs
from preshed.counter import PreshCounter
from joblib import Parallel, delayed

import spacy.en
from spacy.strings import StringStore
from spacy.en.attrs import ORTH


def iter_comments(loc):
    with bz2.BZ2File(loc) as file_:
        for line in file_:
            yield ujson.loads(line)


def null_props(string):
    return {
        'flags': 0,
        'length': len(string),
        'orth': string,
        'lower': string,
        'norm': string,
        'shape': string,
        'prefix': string,
        'suffix': string,
        'cluster': 0,
        'prob': -22,
        'sentiment': 0
    }


def count_freqs(input_loc, output_loc):
    print output_loc
    nlp = spacy.en.English(Parser=None, Tagger=None, Entity=None, load_vectors=False)
    nlp.vocab.lexeme_props_getter = null_props

    counts = PreshCounter()
    tokenizer = nlp.tokenizer
    for json_comment in iter_comments(input_loc):
        doc = tokenizer(json_comment['body'])
        doc.count_by(ORTH, counts=counts)

    with codecs.open(output_loc, 'w', 'utf8') as file_:
        for orth, freq in counts:
            string = nlp.vocab.strings[orth]
            file_.write('%d\t%s\n' % (freq, repr(string)))


def parallelize(func, iterator, n_jobs):
    Parallel(n_jobs=n_jobs)(delayed(func)(*item) for item in iterator)


def merge_counts(locs, out_loc):
    string_map = StringStore()
    counts = PreshCounter()
    for loc in locs:
        with codecs.open(loc, 'r', 'utf8') as file_:
            for line in file_:
                freq, word = line.strip().split('\t', 1)
                orth = string_map[word]
                counts.inc(orth, int(freq))
    with codecs.open(out_loc, 'w', 'utf8') as file_:
        for orth, count in counts:
            string = string_map[orth]
            file_.write('%d\t%s\n' % (count, string))


@plac.annotations(
    input_loc=("Location of input file list"),
    freqs_dir=("Directory for frequency files"),
    output_loc=("Location for output file"),
    n_jobs=("Number of workers", "option", "n", int),
    skip_existing=("Skip inputs where an output file exists", "flag", "s", bool),
)
def main(input_loc, freqs_dir, output_loc, n_jobs=2, skip_existing=False):
    tasks = []
    outputs = []
    for input_path in open(input_loc):
        input_path = input_path.strip()
        if not input_path:
            continue
        filename = input_path.split('/')[-1]
        output_path = path.join(freqs_dir, filename.replace('bz2', 'freq'))
        outputs.append(output_path)
        if not path.exists(output_path) or not skip_existing:
            tasks.append((input_path, output_path))

    if tasks:
        parallelize(count_freqs, tasks, n_jobs)

    print "Merge"
    merge_counts(outputs, output_loc)
                

if __name__ == '__main__':
    plac.call(main)
