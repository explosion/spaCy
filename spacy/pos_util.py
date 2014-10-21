from __future__ import unicode_literals
from . import util
from . import tokens
from .en import EN

from .pos import Tagger


def realign_tagged(token_rules, tagged_line, sep='/'):
    words, pos = zip(*[token.rsplit(sep, 1) for token in tagged_line.split()])
    positions = util.detokenize(token_rules, words)
    aligned = []
    for group in positions:
        w_group = [words[i] for i in group]
        p_group = [pos[i] for i in group]
        aligned.append('<SEP>'.join(w_group) + sep + '_'.join(p_group))
    return ' '.join(aligned)


def read_tagged(detoken_rules, file_, sep='/'):
    sentences = []
    for line in file_:
        line = realign_tagged(detoken_rules, line, sep=sep)
        tokens, tags = _parse_line(line, sep)
        assert len(tokens) == len(tags)
        sentences.append((tokens, tags))
    return sentences


def _parse_line(line, sep):
    words = []
    tags = []
    for token_str in line.split():
        word, pos = token_str.rsplit(sep, 1)
        word = word.replace('<SEP>', '')
        subtokens = EN.tokenize(word)
        subtags = pos.split('_')
        while len(subtags) < len(subtokens):
            subtags.append('NULL')
        assert len(subtags) == len(subtokens), [t.string for t in subtokens]
        words.append(word)
        tags.extend([Tagger.encode_pos(pos) for pos in subtags])
    return EN.tokenize(' '.join(words)), tags


def get_tagdict(train_sents):
    tagdict = {}
    for tokens, tags in train_sents:
        for i, tag in enumerate(tags):
            if tag == 'NULL':
                continue
            word = tokens.string(i)
            tagdict.setdefault(word, {}).setdefault(tag, 0)
            tagdict[word][tag] += 1
    return tagdict
