from __future__ import unicode_literals
from ...vocab import Vocab
from ...pipeline import DependencyParser
from ...tokens import Doc
from ...gold import GoldParse
from ...syntax.nonproj import projectivize

annot_tuples = [
    (0, 'When', 'WRB', 11, 'advmod', 'O'),
    (1, 'Walter', 'NNP', 2, 'compound', 'B-PERSON'),
    (2, 'Rodgers', 'NNP', 11, 'nsubj', 'L-PERSON'),
    (3, ',', ',', 2, 'punct', 'O'),
    (4, 'our', 'PRP$', 6, 'poss', 'O'),
    (5, 'embedded', 'VBN', 6, 'amod', 'O'),
    (6, 'reporter', 'NN', 2, 'appos', 'O'),
    (7, 'with', 'IN', 6, 'prep', 'O'),
    (8, 'the', 'DT', 10, 'det', 'B-ORG'),
    (9, '3rd', 'NNP', 10, 'compound', 'I-ORG'),
    (10, 'Cavalry', 'NNP', 7, 'pobj', 'L-ORG'),
    (11, 'says', 'VBZ', 44, 'advcl', 'O'),
    (12, 'three', 'CD', 13, 'nummod', 'U-CARDINAL'),
    (13, 'battalions', 'NNS', 16, 'nsubj', 'O'),
    (14, 'of', 'IN', 13, 'prep', 'O'),
    (15, 'troops', 'NNS', 14, 'pobj', 'O'),
    (16, 'are', 'VBP', 11, 'ccomp', 'O'),
    (17, 'on', 'IN', 16, 'prep', 'O'),
    (18, 'the', 'DT', 19, 'det', 'O'),
    (19, 'ground', 'NN', 17, 'pobj', 'O'),
    (20, ',', ',', 17, 'punct', 'O'),
    (21, 'inside', 'IN', 17, 'prep', 'O'),
    (22, 'Baghdad', 'NNP', 21, 'pobj', 'U-GPE'),
    (23, 'itself', 'PRP', 22, 'appos', 'O'),
    (24, ',', ',', 16, 'punct', 'O'),
    (25, 'have', 'VBP', 26, 'aux', 'O'),
    (26, 'taken', 'VBN', 16, 'dep', 'O'),
    (27, 'up', 'RP', 26, 'prt', 'O'),
    (28, 'positions', 'NNS', 26, 'dobj', 'O'),
    (29, 'they', 'PRP', 31, 'nsubj', 'O'),
    (30, "'re", 'VBP', 31, 'aux', 'O'),
    (31, 'going', 'VBG', 26, 'parataxis', 'O'),
    (32, 'to', 'TO', 33, 'aux', 'O'),
    (33, 'spend', 'VB', 31, 'xcomp', 'O'),
    (34, 'the', 'DT', 35, 'det', 'B-TIME'), 
    (35, 'night', 'NN', 33, 'dobj', 'L-TIME'),
    (36, 'there', 'RB', 33, 'advmod', 'O'),
    (37, 'presumably', 'RB', 33, 'advmod', 'O'),
    (38, ',', ',', 44, 'punct', 'O'),
    (39, 'how', 'WRB', 40, 'advmod', 'O'),
    (40, 'many', 'JJ', 41, 'amod', 'O'),
    (41, 'soldiers', 'NNS', 44, 'pobj', 'O'),
    (42, 'are', 'VBP', 44, 'aux', 'O'),
    (43, 'we', 'PRP', 44, 'nsubj', 'O'),
    (44, 'talking', 'VBG', 44, 'ROOT', 'O'),
    (45, 'about', 'IN', 44, 'prep', 'O'),
    (46, 'right', 'RB', 47, 'advmod', 'O'),
    (47, 'now', 'RB', 44, 'advmod', 'O'),
    (48, '?', '.', 44, 'punct', 'O')]

def test_get_oracle_actions():
    doc = Doc(Vocab(), words=[t[1] for t in annot_tuples])
    parser = DependencyParser(doc.vocab)
    parser.moves.add_action(0, '')
    parser.moves.add_action(1, '')
    parser.moves.add_action(1, '')
    parser.moves.add_action(4, 'ROOT')
    for i, (id_, word, tag, head, dep, ent) in enumerate(annot_tuples):
        if head > i:
            parser.moves.add_action(2, dep)
        elif head < i:
            parser.moves.add_action(3, dep)
    ids, words, tags, heads, deps, ents = zip(*annot_tuples)
    heads, deps = projectivize(heads, deps)
    gold = GoldParse(doc, words=words, tags=tags, heads=heads, deps=deps)
    parser.moves.preprocess_gold(gold)
    actions = parser.moves.get_oracle_sequence(doc, gold)
