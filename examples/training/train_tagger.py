"""A quick example for training a part-of-speech tagger, without worrying
about the tokenization, or other language-specific customizations."""

from __future__ import unicode_literals
from __future__ import print_function

import plac
from pathlib import Path

from spacy.vocab import Vocab
from spacy.tagger import Tagger
from spacy.tokens import Doc
from spacy.gold import GoldParse

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
        ["N", "V", "J", "N"]
    ),
    (
        ["Eat", "blue", "ham"],
        ["V", "J", "N"]
    )
]


def ensure_dir(path):
    if not path.exists():
        path.mkdir()


def main(output_dir=None):
    if output_dir is not None:
        output_dir = Path(output_dir)
        ensure_dir(output_dir)
        ensure_dir(output_dir / "pos")
        ensure_dir(output_dir / "vocab")

    vocab = Vocab(tag_map=TAG_MAP)
    # The default_templates argument is where features are specified. See
    # spacy/tagger.pyx for the defaults.
    tagger = Tagger(vocab)
    for i in range(25):
        for words, tags in DATA:
            doc = Doc(vocab, words=words)
            gold = GoldParse(doc, tags=tags)
            tagger.update(doc, gold)
        random.shuffle(DATA)
    tagger.model.end_training()
    doc = Doc(vocab, orths_and_spaces=zip(["I", "like", "blue", "eggs"], [True] * 4))
    tagger(doc)
    for word in doc:
        print(word.text, word.tag_, word.pos_)
    if output_dir is not None:
        tagger.model.dump(str(output_dir / 'pos' / 'model'))
        with (output_dir / 'vocab' / 'strings.json').open('w') as file_:
            tagger.vocab.strings.dump(file_)


if __name__ == '__main__':
    plac.call(main)
    # I V VERB
    # like V VERB
    # blue N NOUN
    # eggs N NOUN
