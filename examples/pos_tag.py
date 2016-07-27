'''Print part-of-speech tagged, true-cased, (very roughly) sentence-separated
text, with each "sentence" on a newline, and spaces between tokens. Supports
multi-processing.
'''
from __future__ import print_function, unicode_literals, division
import io
import bz2
import logging
from toolz import partition
from os import path

import spacy.en

from joblib import Parallel, delayed
import plac
import ujson


def parallelize(func, iterator, n_jobs, extra):
    extra = tuple(extra)
    return Parallel(n_jobs=n_jobs)(delayed(func)(*(item + extra)) for item in iterator)


def iter_texts_from_json_bz2(loc):
    '''
    Iterator of unicode strings, one per document (here, a comment).
    
    Expects a a path to a BZ2 file, which should be new-line delimited JSON. The
    document text should be in a string field titled 'body'.

    This is the data format of the Reddit comments corpus.
    '''
    with bz2.BZ2File(loc) as file_:
        for i, line in enumerate(file_):
            yield ujson.loads(line)['body']


def transform_texts(batch_id, input_, out_dir):
    out_loc = path.join(out_dir, '%d.txt' % batch_id)
    if path.exists(out_loc):
        return None
    print('Batch', batch_id)
    nlp = spacy.en.English(parser=False, entity=False)
    with io.open(out_loc, 'w', encoding='utf8') as file_:
        for text in input_:
            doc = nlp(text)
            file_.write(' '.join(represent_word(w) for w in doc if not w.is_space))
            file_.write('\n')


def represent_word(word):
    text = word.text
    # True-case, i.e. try to normalize sentence-initial capitals.
    # Only do this if the lower-cased form is more probable.
    if text.istitle() \
    and is_sent_begin(word) \
    and word.prob < word.doc.vocab[text.lower()].prob:
        text = text.lower()
    return text + '|' + word.tag_


def is_sent_begin(word):
    # It'd be nice to have some heuristics like these in the library, for these
    # times where we don't care so much about accuracy of SBD, and we don't want
    # to parse
    if word.i == 0:
        return True
    elif word.i >= 2 and word.nbor(-1).text in ('.', '!', '?', '...'):
        return True
    else:
        return False


@plac.annotations(
    in_loc=("Location of input file"),
    out_dir=("Location of input file"),
    n_workers=("Number of workers", "option", "n", int),
    batch_size=("Batch-size for each process", "option", "b", int)
)
def main(in_loc, out_dir, n_workers=4, batch_size=100000):
    if not path.exists(out_dir):
        path.join(out_dir)
    texts = partition(batch_size, iter_texts(in_loc))
    parallelize(transform_texts, enumerate(texts), n_workers, [out_dir])
 

if __name__ == '__main__':
    plac.call(main)

