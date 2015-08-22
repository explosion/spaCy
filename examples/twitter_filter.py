# encoding: utf8
from __future__ import unicode_literals, print_function
import plac
import codecs
import pathlib
import random

import twython
import spacy.en

import _handler


class Connection(twython.TwythonStreamer):
    def __init__(self, keys_dir, nlp, query):
        keys_dir = pathlib.Path(keys_dir)
        read = lambda fn: (keys_dir / (fn + '.txt')).open().read().strip()
        api_key = map(read, ['key', 'secret', 'token', 'token_secret'])
        twython.TwythonStreamer.__init__(self, *api_key)
        self.nlp = nlp
        self.query = query

    def on_success(self, data):
        _handler.handle_tweet(self.nlp, data, self.query)
        if random.random() >= 0.1:
            reload(_handler)


def main(keys_dir, term):
    nlp = spacy.en.English()
    twitter = Connection(keys_dir, nlp, term)
    twitter.statuses.filter(track=term, language='en')


if __name__ == '__main__':
    plac.call(main)
