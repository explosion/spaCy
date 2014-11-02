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
        if not line.strip():
            continue
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
        tags.extend([Tagger.encode_pos(ptb_to_univ(pos)) for pos in subtags])
    tokens = EN.tokenize(' '.join(words)), tags
    return tokens


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


def ptb_to_univ(tag):
    mapping = dict(tuple(line.split()) for line in """
NULL    NULL
HYPH   .
ADD X
NFP .
AFX X
XX  X
BES VERB
HVS VERB
GW  X
!	.
#	.
$	.
''	.
(	.
)	.
,	.
-LRB-	.
-RRB-	.
.	.
:	.
?	.
CC	CONJ
CD	NUM
CD|RB	X
DT	DET
EX	DET
FW	X
IN	ADP
IN|RP	ADP
JJ	ADJ
JJR	ADJ
JJRJR	ADJ
JJS	ADJ
JJ|RB	ADJ
JJ|VBG	ADJ
LS	X
MD	VERB
NN	NOUN
NNP	NOUN
NNPS	NOUN
NNS	NOUN
NN|NNS	NOUN
NN|SYM	NOUN
NN|VBG	NOUN
NP	NOUN
PDT	DET
POS	PRT
PRP	PRON
PRP$	PRON
PRP|VBP	PRON
PRT	PRT
RB	ADV
RBR	ADV
RBS	ADV
RB|RP	ADV
RB|VBG	ADV
RN	X
RP	PRT
SYM	X
TO	PRT
UH	X
VB	VERB
VBD	VERB
VBD|VBN	VERB
VBG	VERB
VBG|NN	VERB
VBN	VERB
VBP	VERB
VBP|TO	VERB
VBZ	VERB
VP	VERB
WDT	DET
WH	X
WP	PRON
WP$	PRON
WRB	ADV
!	PRT
#	X
$	NUM
&	CONJ
,	.
@	X
A	ADJ
D	DET
E	X
G	X
L	PRT
M	PRT
N	NOUN
O	PRON
P	ADP
R	ADV
S	NOUN
T	PRT
U	X
V	VERB
X	PRT
Y	PRT
Z	NOUN
^	NOUN
~	X
``	.""".strip().split('\n'))
    return mapping[tag]

