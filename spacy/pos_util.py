from __future__ import unicode_literals
from . import util
from . import tokens
from .en import EN

from .pos import Tagger


def read_gold(file_, tag_list):
    paras = file_.read().strip().split('\n\n')
    golds = []
    tag_ids = dict((tag, i) for i, tag in enumerate(tag_list))
    for para in paras:
        if not para.strip():
            continue
        lines = para.strip().split('\n')
        raw = lines.pop(0)
        gold_toks = lines.pop(0)
        tokens = EN.tokenize(raw)
        tags = []
        conll_toks = []
        for line in lines:
            pieces = line.split()
            conll_toks.append((int(pieces[0]), len(pieces[1]), pieces[3]))
        for i, token in enumerate(tokens):
            if not conll_toks:
                tags.append('NULL')
            elif token.idx == conll_toks[0][0]:
                tags.append(conll_toks[0][2])
                conll_toks.pop(0)
            elif token.idx < conll_toks[0]:
                tags.append('NULL')
            else:
                conll_toks.pop(0)
        assert len(tags) == len(tokens)
        tags = [_encode_pos(t, tag_ids, tag_list) for t in tags]
        golds.append((tokens, tags))
    return golds

def _encode_pos(tag, tag_ids, tag_list):
    if tag not in tag_ids:
        tag_ids[tag] = len(tag_list)
        tag_list.append(tag)
    return tag_ids[tag]


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

