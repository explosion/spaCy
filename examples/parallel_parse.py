from __future__ import print_function, unicode_literals, division
import io
import bz2
import logging
from toolz import partition
from os import path
import re

import spacy.en
from spacy.tokens import Doc

from joblib import Parallel, delayed
import plac
import ujson


def parallelize(func, iterator, n_jobs, extra, backend='multiprocessing'):
    extra = tuple(extra)
    return Parallel(n_jobs=n_jobs, backend=backend)(delayed(func)(*(item + extra))
                    for item in iterator)


def iter_comments(loc):
    with bz2.BZ2File(loc) as file_:
        for i, line in enumerate(file_):
            yield ujson.loads(line)['body']


pre_format_re = re.compile(r'^[\`\*\~]')
post_format_re = re.compile(r'[\`\*\~]$')
url_re = re.compile(r'\[([^]]+)\]\(%%URL\)')
link_re = re.compile(r'\[([^]]+)\]\(https?://[^\)]+\)')
def strip_meta(text):
    text = link_re.sub(r'\1', text)
    text = text.replace('&gt;', '>').replace('&lt;', '<')
    text = pre_format_re.sub('', text)
    text = post_format_re.sub('', text)
    return text.strip()


def save_parses(batch_id, input_, out_dir, n_threads, batch_size):
    out_loc = path.join(out_dir, '%d.bin' % batch_id)
    if path.exists(out_loc):
        return None
    print('Batch', batch_id)
    nlp = spacy.en.English()
    nlp.matcher = None
    with open(out_loc, 'wb') as file_:
        texts = (strip_meta(text) for text in input_)
        texts = (text for text in texts if text.strip())
        for doc in nlp.pipe(texts, batch_size=batch_size, n_threads=n_threads):
            file_.write(doc.to_bytes())

@plac.annotations(
    in_loc=("Location of input file"),
    out_dir=("Location of input file"),
    n_process=("Number of processes", "option", "p", int),
    n_thread=("Number of threads per process", "option", "t", int),
    batch_size=("Number of texts to accumulate in a buffer", "option", "b", int)
)
def main(in_loc, out_dir, n_process=1, n_thread=4, batch_size=100):
    if not path.exists(out_dir):
        path.join(out_dir)
    if n_process >= 2:
        texts = partition(200000, iter_comments(in_loc))
        parallelize(save_parses, enumerate(texts), n_process, [out_dir, n_thread, batch_size],
                   backend='multiprocessing')
    else:
        save_parses(0, iter_comments(in_loc), out_dir, n_thread, batch_size)



if __name__ == '__main__':
    plac.call(main)
