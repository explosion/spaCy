'''
This example shows training of the POS tagger without the Language class,
showing the APIs of the atomic components.

This example was adapted from the gist here:

https://gist.github.com/kamac/a7bc139f62488839a8118214a4d932f2

Issue discussing the gist:

https://github.com/explosion/spaCy/issues/1179

The example was written for spaCy 1.8.2.
'''
from __future__ import unicode_literals
from __future__ import print_function

import plac
import codecs
import spacy.symbols as symbols
import spacy
from pathlib import Path

from spacy.vocab import Vocab
from spacy.tagger import Tagger
from spacy.tokens import Doc
from spacy.gold import GoldParse
from spacy.language import Language
from spacy import orth
from spacy import attrs

import random

TAG_MAP = {
    'ADJ': {symbols.POS: symbols.ADJ},
    'ADP': {symbols.POS: symbols.ADP},
    'PUNCT': {symbols.POS: symbols.PUNCT},
    'ADV': {symbols.POS: symbols.ADV},
    'AUX': {symbols.POS: symbols.AUX},
    'SYM': {symbols.POS: symbols.SYM},
    'INTJ': {symbols.POS: symbols.INTJ},
    'CCONJ': {symbols.POS: symbols.CCONJ},
    'X': {symbols.POS: symbols.X},
    'NOUN': {symbols.POS: symbols.NOUN},
    'DET': {symbols.POS: symbols.DET},
    'PROPN': {symbols.POS: symbols.PROPN},
    'NUM': {symbols.POS: symbols.NUM},
    'VERB': {symbols.POS: symbols.VERB},
    'PART': {symbols.POS: symbols.PART},
  	'PRON': {symbols.POS: symbols.PRON},
    'SCONJ': {symbols.POS: symbols.SCONJ},
}

LEX_ATTR_GETTERS = {
    attrs.LOWER: lambda string: string.lower(),
    attrs.NORM: lambda string: string,
    attrs.SHAPE: orth.word_shape,
    attrs.PREFIX: lambda string: string[0],
    attrs.SUFFIX: lambda string: string[-3:],
    attrs.CLUSTER: lambda string: 0,
    attrs.IS_ALPHA: orth.is_alpha,
    attrs.IS_ASCII: orth.is_ascii,
    attrs.IS_DIGIT: lambda string: string.isdigit(),
    attrs.IS_LOWER: orth.is_lower,
    attrs.IS_PUNCT: orth.is_punct,
    attrs.IS_SPACE: lambda string: string.isspace(),
    attrs.IS_TITLE: orth.is_title,
    attrs.IS_UPPER: orth.is_upper,
    attrs.IS_BRACKET: orth.is_bracket,
    attrs.IS_QUOTE: orth.is_quote,
    attrs.IS_LEFT_PUNCT: orth.is_left_punct,
    attrs.IS_RIGHT_PUNCT: orth.is_right_punct,
    attrs.LIKE_URL: orth.like_url,
    attrs.LIKE_NUM: orth.like_number,
    attrs.LIKE_EMAIL: orth.like_email,
    attrs.IS_STOP: lambda string: False,
    attrs.IS_OOV: lambda string: True
}


def read_ud_data(path):
    data = []
    last_number = -1
    sentence_words = []
    sentence_tags = []
    with codecs.open(path, encoding="utf-8") as f:
        while True:
            line = f.readline()
            if not line:
                break

            if line[0].isdigit():
                d = line.split()
                if not "-" in d[0]:
                    number = int(line[0])
                    if number < last_number:
                        data.append((sentence_words, sentence_tags),)
                        sentence_words = []
                        sentence_tags = []
                    sentence_words.append(d[2])
                    sentence_tags.append(d[3])
                    last_number = number
    if len(sentence_words) > 0:
        data.append((sentence_words, sentence_tags,))
    return data

def ensure_dir(path):
    if not path.exists():
        path.mkdir()


def main(train_loc, dev_loc, output_dir=None):
    if output_dir is not None:
        output_dir = Path(output_dir)
        ensure_dir(output_dir)
        ensure_dir(output_dir / "pos")
        ensure_dir(output_dir / "vocab")

    train_data = read_ud_data(train_loc)
    vocab = Vocab(tag_map=TAG_MAP, lex_attr_getters=LEX_ATTR_GETTERS)
    # Populate vocab
    for words, _ in train_data:
        for word in words:
            _ = vocab[word]
    
    model = spacy.tagger.TaggerModel(spacy.tagger.Tagger.feature_templates)
    tagger = Tagger(vocab, model)
    print(tagger.tag_names)
    for i in range(30):
        print("training model (iteration " + str(i) + ")...")
        score = 0.
        num_samples = 0.
        for words, tags in train_data:
            doc = Doc(vocab, words=words)
            gold = GoldParse(doc, tags=tags)
            cost = tagger.update(doc, gold)
            for i, word in enumerate(doc):
                num_samples += 1
                if word.tag_ == tags[i]:
                    score += 1
        print('Train acc', score/num_samples) 
        random.shuffle(train_data)
    tagger.model.end_training()

    score = 0.0
    test_data = read_ud_data(dev_loc)
    num_samples = 0
    for words, tags in test_data:
        doc = Doc(vocab, words)
        tagger(doc)
        for i, word in enumerate(doc):
            num_samples += 1
            if word.tag_ == tags[i]:
                score += 1
    print("score: " + str(score / num_samples * 100.0))
    
    if output_dir is not None:
        tagger.model.dump(str(output_dir / 'pos' / 'model'))
        with (output_dir / 'vocab' / 'strings.json').open('w') as file_:
            tagger.vocab.strings.dump(file_)


if __name__ == '__main__':
    plac.call(main)
