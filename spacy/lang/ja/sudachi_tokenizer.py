# encoding: utf8
from __future__ import unicode_literals, print_function

from importlib import import_module
import json
from pathlib import Path
import re
import sys

from ...symbols import POS
from ...tokens import Doc
from ...vocab import Vocab
from ...util import DummyTokenizer

from .tag_map import TAG_MAP


def try_import_sudachipy_dictionary():
    try:
        from sudachipy import dictionary
        return dictionary
    except ImportError:
        raise ImportError(
            "Japanese support requires SudachiPy distributed with ja language model"
        )


# see https://spacy.io/usage/processing-pipelines#component-example1
def separate_sentences(doc):
    for i, token in enumerate(doc[:-2]):
        if token.tag_:
            if token.tag_ == "補助記号-句点":
                next_token = doc[i+1]
                if next_token.tag_ != token.tag_:
                    next_token.sent_start = True


def morph_tag(tag_array):
    return "-".join([
        p for p in tag_array if p != '*'
    ])


class SudachiTokenizer(DummyTokenizer):
    def __init__(self, nlp=None):
        self.nlp = nlp
        self.vocab = nlp.vocab if nlp is not None else Vocab()
        dictionary = try_import_sudachipy_dictionary()

        dict_ = dictionary.Dictionary()
        self.tokenizer = dict_.create()

    def __call__(self, text):
        result = self.tokenizer.tokenize(text=text)
        morph_spaces = []
        last_morph = None
        for m in result:
            if m.surface():
                if m.part_of_speech()[0] == '空白':
                    if last_morph:
                        morph_spaces.append((last_morph, True))
                        last_morph = None
                    else:
                        morph_spaces.append((m, False))
                elif last_morph:
                    morph_spaces.append((last_morph, False))
                    last_morph = m
                else:
                    last_morph = m
        if last_morph:
            morph_spaces.append((last_morph, False))

        words = [m.surface() for m, spaces in morph_spaces]
        spaces = [space for m, space in morph_spaces]
        doc = Doc(self.nlp.vocab if self.nlp else Vocab(), words=words, spaces=spaces)
        next_tag = morph_tag(morph_spaces[0][0].part_of_speech()[0:4]) if len(doc) else ''
        for token, (morph, spaces) in zip(doc, morph_spaces):
            tag = next_tag
            next_tag = morph_tag(morph_spaces[token.i + 1][0].part_of_speech()[0:4]) if token.i < len(doc) - 1 else ''
            token.tag_ = tag
            token.pos = TAG_MAP[tag][POS]
            # TODO separate lexical rules to resource files
            if morph.normalized_form() == '為る' and tag == '動詞-非自立可能':
                token.pos_ = 'AUX'
            elif tag == '名詞-普通名詞-サ変可能':
                if next_tag == '動詞-非自立可能':
                    token.pos_ = 'VERB'
            elif tag == '名詞-普通名詞-サ変形状詞可能':
                if next_tag == '動詞-非自立可能':
                    token.pos_ = 'VERB'
                elif next_tag == '助動詞' or next_tag.find('形状詞') >= 0:
                    token.pos_ = 'ADJ'
            token._.inf = ','.join(morph.part_of_speech()[4:])
            token.lemma_ = morph.normalized_form()  # work around: lemma_ must be set after tag_
        if self.use_sentence_separator:
            separate_sentences(doc)
        return doc

    # add dummy methods for to_bytes, from_bytes, to_disk and from_disk to
    # allow serialization (see #1557)
    def to_bytes(self, **exclude):
        return b''

    def from_bytes(self, bytes_data, **exclude):
        return self

    def to_disk(self, path, **exclude):
        return None

    def from_disk(self, path, **exclude):
        return self


SUDACHI_PATTERN = re.compile(
    r"^([^\t]*)\t"
    r"([^\t,]+,[^\t,]+,[^\t,]+,[^\t,]+),"
    r"([^\t,]+,[^\t,]+)\t"
    r"([^\t]*)\t"
    r"([^\t]*)\t"
    r"([^\t]*)\t"
    r"([^\t]+)"
    r"(\t\(OOV\))?$"
)


def read_sudachi_a(path, file, yield_document=False):
    return read_sudachi(path, file, yield_document, 'A')


def read_sudachi_b(path, file, yield_document=False):
    return read_sudachi(path, file, yield_document, 'B')


def read_sudachi_c(path, file, yield_document=False):
    return read_sudachi(path, file, yield_document, 'C')


def read_sudachi(path, file, yield_document=False, mode='B'):
    sentences = []
    sentence = []
    line = None
    state = 'EOS'
    for line_index, line in enumerate(file):
        if line_index == 0 and not line.startswith('#'):
            print('Skip file: %s' % path, file=sys.stderr)
            line = None
            break
        line = line.rstrip()
        if line.startswith('#'):
            continue
        elif line == 'EOS':
            if yield_document:
                sentences.append(sentence)
            else:
                yield sentence
            sentence = []
            state = 'EOS'
            continue
        elif line.startswith('@'):
            assert state != 'EOS', 'Bad state {}: {} #{}: {}'.format(state, path, line_index + 1, line)
            if line[1] != mode:
                continue
            if state == 'MORPH':
                sentence.pop()
                state = 'MODE'
            line = line[3:]
        else:
            state = 'MORPH'

        m = SUDACHI_PATTERN.match(line)
        surface = None
        if m:
            surface = m.group(1)
            if not surface:  # bug of sudachi java version
                surface = m.group(4)
        if surface:
            sentence.append(surface)
        else:
            print('Bad format in %s line #%d' % (path, line_index + 1), file=sys.stderr)
            print(line, file=sys.stderr)

    if line is not None and (line != 'EOS' or line.startswith('#\td')):
        print('File not ends with EOS or #d - %s' % path, file=sys.stderr)

    if yield_document:
        yield sentences
