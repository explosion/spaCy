"""A quick example for training a part-of-speech tagger, without worrying
about the tokenization, or other language-specific customizations."""

from __future__ import unicode_literals
from __future__ import print_function

import plac
from os import path
import os

from spacy.vocab import Vocab
from spacy.tokenizer import Tokenizer
from spacy.tagger import Tagger
import random


# You need to define a mapping from your data's part-of-speech tag names to the
# Universal Part-of-Speech tag set, as spaCy includes an enum of these tags.
# See here for the Universal Tag Set:
# http://universaldependencies.github.io/docs/u/pos/index.html
# You may also specify morphological features for your tags, from the universal
# scheme.
TAG_MAP = {
        'N': {"pos": "NOUN"},
        'V': {"pos": "VERB"},
        'J': {"pos": "ADJ"}
    }

# Usually you'll read this in, of course. Data formats vary.
# Ensure your strings are unicode.
DATA = [
    (
        ["I", "like", "green", "eggs"],
        ["N", "V",    "J",     "N"]
    ),
    (
        ["Eat", "blue", "ham"],
        ["V",   "J",    "N"]
    )
]
    
def ensure_dir(*parts):
    path_ = path.join(*parts)
    if not path.exists(path_):
        os.mkdir(path_)
    return path_


def main(output_dir):
    ensure_dir(output_dir)
    ensure_dir(output_dir, "pos")
    ensure_dir(output_dir, "vocab")
    
    vocab = Vocab(tag_map=TAG_MAP)
    tokenizer = Tokenizer(vocab, {}, None, None, None)
    # The default_templates argument is where features are specified. See
    # spacy/tagger.pyx for the defaults.
    tagger = Tagger.blank(vocab, Tagger.default_templates())

    for i in range(5):
        for words, tags in DATA:
            tokens = tokenizer.tokens_from_list(words)
            tagger.train(tokens, tags)
        random.shuffle(DATA)
    tagger.model.end_training()
    tagger.model.dump(path.join(output_dir, 'pos', 'model'))
    with io.open(output_dir, 'vocab', 'strings.json') as file_:
        tagger.vocab.strings.dump(file_)


if __name__ == '__main__':
    plac.call(main)
