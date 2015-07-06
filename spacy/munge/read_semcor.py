from __future__ import unicode_literals
from __future__ import division
import plac
import re
from os import path
import os
import codecs

from spacy.en import English

lexnames_str = """
-1      NO_SENSE       -1
00      J_all 3
01      A_pert        3 
02      A_all 4
03      N_Tops       1  
04      N_act        1
05      N_animal     1
06      N_artifact   1
07      N_attribute  1
08      N_body       1
09      N_cognition  1
10      N_communication      1
11      N_event      1
12      N_feeling    1
13      N_food       1
14      N_group      1
15      N_location   1
16      N_motive     1
17      N_object     1
18      N_person     1
19      N_phenomenon 1
20      N_plant      1
21      N_possession 1
22      N_process    1
23      N_quantity   1
24      N_relation   1
25      N_shape      1
26      N_state      1
27      N_substance  1
28      N_time       1
29      V_body       2
30      V_change     2
31      V_cognition  2
32      V_communication      2
33      V_competition        2
34      V_consumption        2
35      V_contact    2
36      V_creation   2
37      V_emotion    2
38      V_motion     2
39      V_perception 2
40      V_possession 2
41      V_social     2
42      V_stative    2
43      V_weather    2
44      A_ppl 3
""".strip()

SUPERSENSES = tuple(line.split()[1] for line in lexnames_str.split('\n'))




def re_get(exp, string):
    obj = exp.search(string)
    if obj is None:
        return obj
    else:
        return obj.group()


lemma_re = re.compile(r'(?<=lemma=)[^ >]+')
cmd_re = re.compile(r'(?<=cmd=)[^ >]+')
pos_re = re.compile(r'(?<=pos=)[^ >]+')
ot_re = re.compile(r'(?<=ot=)[^ >]+')
wnsn_re = re.compile(r'(?<=wnsn=)[^ >]+')
lexsn_re = re.compile(r'(?<=lexsn=)[^ >]+')
supersense_re = re.compile(r'(?<=lexsn=\d:)\d\d')
orth_re = re.compile(r'(?<=>)[^<]+(?=<)')
class Token(object):
    def __init__(self, line):
        self.cmd = re_get(cmd_re, line)
        self.lemma = re_get(lemma_re, line)
        self.ot = re_get(ot_re, line)
        self.pos = re_get(pos_re, line)
        self.wnsn = re_get(wnsn_re, line)
        self.lexsn = re_get(lexsn_re, line)
        supersense = re_get(supersense_re, line)
        if supersense is None:
            self.supersense = SUPERSENSES[0]
        else:
            self.supersense = SUPERSENSES[int(supersense) + 1]
        self.orth = re_get(orth_re, line)

    def __str__(self):
        return (self.cmd, self.lemma, self.ot, self.pos,
                self.wnsn, self.lexsn, self.orth)

    def __repr__(self):
        return str(self)


def read_file(loc):
    paras = []
    sents = []
    sent = []
    filename = None
    pnum = None
    snum = None
    for line in codecs.open(loc, 'r', 'latin1'):
        line = line.strip()
        if not line:
            continue

        if line.startswith('contextfile'):
            continue

        if line.startswith('<context '):
            assert filename is None
            pieces = line.split()
            filename = pieces[1].replace('filename=', '')
            continue
        
        if line.startswith('<p '):
            assert pnum is None
            pnum = int(line.split('=')[1][:-1])
            continue
        
        if line.startswith('<s '):
            assert snum is None, line
            snum = int(line.split('=')[1][:-1])
            continue

        if line.startswith('<wf ') or line.startswith('<punc'):
            sent.append(Token(line))
            continue

        if line == '</s>':
            sents.append((snum, sent))
            sent = []
            snum = None
            continue

        if line == '</p>':
            paras.append((pnum, sents))
            sents = []
            pnum = None
            continue
    return paras


def read_semcor(semcor_dir):
    docs = []
    brown1 = path.join(semcor_dir, 'brown1', 'tagfiles')
    for filename in os.listdir(brown1):
        file_path = path.join(brown1, filename)
        docs.append((filename, read_file(file_path)))
    return docs


def test_token():
    string = '<wf cmd=done pos=NN lemma=sheriff wnsn=1 lexsn=1:18:00::>sheriff</wf>'
    token = Token(string)
    assert token.cmd == 'done'
    assert token.pos == 'NN'
    assert token.lemma == 'sheriff'
    assert token.wnsn == '1'
    assert token.lexsn == '1:18:00::'
    assert token.orth == 'sheriff'


def main(model_dir, semcor_dir):
    brown1 = path.join(semcor_dir, 'brown1', 'tagfiles')

    nlp = English(data_dir=model_dir)
    total_right = 0
    total_wrong = 0
    total_multi = 0
    for filename in os.listdir(brown1):
        file_path = path.join(brown1, filename)
        annotations = read_file(file_path)

        n_multi, n_right, n_wrong = eval_text(nlp, annotations)
        total_right += n_right
        total_wrong += n_wrong
        total_multi += n_multi
    print total_right, total_wrong
    print total_right / (total_right + total_wrong)
    print total_multi / (total_multi + total_right + total_wrong) 

if __name__ == '__main__':
    plac.call(main)
