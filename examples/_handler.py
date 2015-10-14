# encoding: utf8
from __future__ import unicode_literals, print_function

from math import sqrt
from numpy import dot
from numpy.linalg import norm


def handle_tweet(spacy, tweet_data, query):
    text = tweet_data.get('text', u'')
    # Twython returns either bytes or unicode, depending on tweet.
    # ಠ_ಠ #APIshaming
    try:
        match_tweet(spacy, text, query)
    except TypeError:
        match_tweet(spacy, text.decode('utf8'), query)


def match_tweet(spacy, text, query):
    def get_vector(word):
        return spacy.vocab[word].repvec

    tweet = spacy(text)
    tweet = [w.repvec for w in tweet if w.is_alpha and w.lower_ != query]
    if tweet:
        accept = map(get_vector, 'child classroom teach'.split())
        reject = map(get_vector, 'mouth hands giveaway'.split())
        
        y = sum(max(cos(w1, w2), 0) for w1 in tweet for w2 in accept)
        n = sum(max(cos(w1, w2), 0) for w1 in tweet for w2 in reject)
        
        if (y / (y + n)) >= 0.5 or True:
            print(text)


def cos(v1, v2):
    return dot(v1, v2) / (norm(v1) * norm(v2))
