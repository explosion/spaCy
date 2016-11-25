from __future__ import unicode_literals, print_function

import numpy
import io
import json
import random
import re
import os
from os import path

from libc.string cimport memset

import ujson as json

from .syntax import nonproj


def tags_to_entities(tags):
    entities = []
    start = None
    for i, tag in enumerate(tags):
        if tag is None:
            continue
        if tag.startswith('O'):
            # TODO: We shouldn't be getting these malformed inputs. Fix this.
            if start is not None:
                start = None
            continue
        elif tag == '-':
            continue
        elif tag.startswith('I'):
            assert start is not None, tags[:i]
            continue
        if tag.startswith('U'):
            entities.append((tag[2:], i, i))
        elif tag.startswith('B'):
            start = i
        elif tag.startswith('L'):
            entities.append((tag[2:], start, i))
            start = None
        else:
            raise Exception(tag)
    return entities


def merge_sents(sents):
    m_deps = [[], [], [], [], [], []]
    m_brackets = []
    i = 0
    for (ids, words, tags, heads, labels, ner), brackets in sents:
        m_deps[0].extend(id_ + i for id_ in ids)
        m_deps[1].extend(words)
        m_deps[2].extend(tags)
        m_deps[3].extend(head + i for head in heads)
        m_deps[4].extend(labels)
        m_deps[5].extend(ner)
        m_brackets.extend((b['first'] + i, b['last'] + i, b['label']) for b in brackets)
        i += len(ids)
    return [(m_deps, m_brackets)]


def align(cand_words, gold_words):
    cost, edit_path = _min_edit_path(cand_words, gold_words)
    alignment = []
    i_of_gold = 0
    for move in edit_path:
        if move == 'M':
            alignment.append(i_of_gold)
            i_of_gold += 1
        elif move == 'S':
            alignment.append(None)
            i_of_gold += 1
        elif move == 'D':
            alignment.append(None)
        elif move == 'I':
            i_of_gold += 1
        else:
            raise Exception(move)
    return alignment


punct_re = re.compile(r'\W')
def _min_edit_path(cand_words, gold_words):
    cdef:
        Pool mem
        int i, j, n_cand, n_gold
        int* curr_costs
        int* prev_costs

    # TODO: Fix this --- just do it properly, make the full edit matrix and
    # then walk back over it...
    # Preprocess inputs
    cand_words = [punct_re.sub('', w) for w in cand_words] 
    gold_words = [punct_re.sub('', w) for w in gold_words] 
    
    if cand_words == gold_words:
        return 0, ''.join(['M' for _ in gold_words])
    mem = Pool()
    n_cand = len(cand_words)
    n_gold = len(gold_words)
    # Levenshtein distance, except we need the history, and we may want different
    # costs.
    # Mark operations with a string, and score the history using _edit_cost.
    previous_row = []
    prev_costs = <int*>mem.alloc(n_gold + 1, sizeof(int))
    curr_costs = <int*>mem.alloc(n_gold + 1, sizeof(int))
    for i in range(n_gold + 1):
        cell = ''
        for j in range(i):
            cell += 'I'
        previous_row.append('I' * i)
        prev_costs[i] = i
    for i, cand in enumerate(cand_words):
        current_row = ['D' * (i + 1)]
        curr_costs[0] = i+1
        for j, gold in enumerate(gold_words):
            if gold.lower() == cand.lower():
                s_cost = prev_costs[j]
                i_cost = curr_costs[j] + 1
                d_cost = prev_costs[j + 1] + 1
            else:
                s_cost = prev_costs[j] + 1
                i_cost = curr_costs[j] + 1
                d_cost = prev_costs[j + 1] + (1 if cand else 0)

            if s_cost <= i_cost and s_cost <= d_cost:
                best_cost = s_cost
                best_hist = previous_row[j] + ('M' if gold == cand else 'S')
            elif i_cost <= s_cost and i_cost <= d_cost:
                best_cost = i_cost
                best_hist = current_row[j] + 'I'
            else:
                best_cost = d_cost
                best_hist = previous_row[j + 1] + 'D'
            
            current_row.append(best_hist)
            curr_costs[j+1] = best_cost
        previous_row = current_row
        for j in range(len(gold_words) + 1):
            prev_costs[j] = curr_costs[j]
            curr_costs[j] = 0

    return prev_costs[n_gold], previous_row[-1]


def read_json_file(loc, docs_filter=None):
    if path.isdir(loc):
        for filename in os.listdir(loc):
            yield from read_json_file(path.join(loc, filename))
    else:
        with io.open(loc, 'r', encoding='utf8') as file_:
            docs = json.load(file_)
        for doc in docs:
            if docs_filter is not None and not docs_filter(doc):
                continue
            paragraphs = []
            for paragraph in doc['paragraphs']:
                sents = []
                for sent in paragraph['sentences']:
                    words = []
                    ids = []
                    tags = []
                    heads = []
                    labels = []
                    ner = []
                    for i, token in enumerate(sent['tokens']):
                        words.append(token['orth'])
                        ids.append(i)
                        tags.append(token.get('tag','-'))
                        heads.append(token.get('head',0) + i)
                        labels.append(token.get('dep',''))
                        # Ensure ROOT label is case-insensitive
                        if labels[-1].lower() == 'root':
                            labels[-1] = 'ROOT'
                        ner.append(token.get('ner', '-'))
                    sents.append((
                        (ids, words, tags, heads, labels, ner),
                        sent.get('brackets', [])))
                if sents:
                    yield (paragraph.get('raw', None), sents)


def _iob_to_biluo(tags):
    out = []
    curr_label = None
    tags = list(tags)
    while tags:
        out.extend(_consume_os(tags))
        out.extend(_consume_ent(tags))
    return out


def _consume_os(tags):
    while tags and tags[0] == 'O':
        yield tags.pop(0)


def _consume_ent(tags):
    if not tags:
        return []
    target = tags.pop(0).replace('B', 'I')
    length = 1
    while tags and tags[0] == target:
        length += 1
        tags.pop(0)
    label = target[2:]
    if length == 1:
        return ['U-' + label]
    else:
        start = 'B-' + label
        end = 'L-' + label
        middle = ['I-%s' % label for _ in range(1, length - 1)]
        return [start] + middle + [end]


cdef class GoldParse:
    """Collection for training annotations."""
    @classmethod
    def from_annot_tuples(cls, doc, annot_tuples, make_projective=False):
        _, words, tags, heads, deps, entities = annot_tuples
        return cls(doc, words=words, tags=tags, heads=heads, deps=deps, entities=entities,
                   make_projective=make_projective)

    def __init__(self, doc, annot_tuples=None, words=None, tags=None, heads=None,
                 deps=None, entities=None, make_projective=False):
        """Create a GoldParse.

        Arguments:
            doc (Doc):
                The document the annotations refer to.
            words:
                A sequence of unicode word strings.
            tags:
                A sequence of strings, representing tag annotations.
            heads:
                A sequence of integers, representing syntactic head offsets.
            deps:
                A sequence of strings, representing the syntactic relation types.
            entities:
                A sequence of named entity annotations, either as BILUO tag strings,
                or as (start_char, end_char, label) tuples, representing the entity
                positions.
        Returns (GoldParse): The newly constructed object.
        """
        if words is None:
            words = [token.text for token in doc]
        if tags is None:
            tags = [None for _ in doc]
        if heads is None:
            heads = [token.i for token in doc]
        if deps is None:
            deps = [None for _ in doc]
        if entities is None:
            entities = ['-' for _ in doc]
        elif len(entities) == 0:
            entities = ['O' for _ in doc]
        elif not isinstance(entities[0], basestring):
            # Assume we have entities specified by character offset.
            entities = biluo_tags_from_offsets(doc, entities)

        self.mem = Pool()
        self.loss = 0
        self.length = len(doc)

        # These are filled by the tagger/parser/entity recogniser
        self.c.tags = <int*>self.mem.alloc(len(doc), sizeof(int))
        self.c.heads = <int*>self.mem.alloc(len(doc), sizeof(int))
        self.c.labels = <int*>self.mem.alloc(len(doc), sizeof(int))
        self.c.ner = <Transition*>self.mem.alloc(len(doc), sizeof(Transition))

        self.words = [None] * len(doc)
        self.tags = [None] * len(doc)
        self.heads = [None] * len(doc)
        self.labels = [''] * len(doc)
        self.ner = ['-'] * len(doc)

        self.cand_to_gold = align([t.orth_ for t in doc], words)
        self.gold_to_cand = align(words, [t.orth_ for t in doc])

        annot_tuples = (range(len(words)), words, tags, heads, deps, entities)
        self.orig_annot = list(zip(*annot_tuples))

        for i, gold_i in enumerate(self.cand_to_gold):
            if doc[i].text.isspace():
                self.words[i] = doc[i].text
                self.tags[i] = 'SP'
                self.heads[i] = None
                self.labels[i] = None
                self.ner[i] = 'O'
            if gold_i is None:
                pass
            else:
                self.words[i] = words[gold_i]
                self.tags[i] = tags[gold_i]
                self.heads[i] = self.gold_to_cand[heads[gold_i]]
                self.labels[i] = deps[gold_i]
                self.ner[i] = entities[gold_i]

        cycle = nonproj.contains_cycle(self.heads)
        if cycle != None:
            raise Exception("Cycle found: %s" % cycle)

        if make_projective:
            proj_heads,_ = nonproj.PseudoProjectivity.projectivize(self.heads, self.labels)
            self.heads = proj_heads

    def __len__(self):
        """Get the number of gold-standard tokens.
        
        Returns (int): The number of gold-standard tokens.
        """
        return self.length

    @property
    def is_projective(self):
        """Whether the provided syntactic annotations form a projective dependency
        tree."""
        return not nonproj.is_nonproj_tree(self.heads)


def biluo_tags_from_offsets(doc, entities):
    '''Encode labelled spans into per-token tags, using the Begin/In/Last/Unit/Out
    scheme (biluo).

    Arguments:
        doc (Doc):
            The document that the entity offsets refer to. The output tags will
            refer to the token boundaries within the document.

        entities (sequence):
            A sequence of (start, end, label) triples. start and end should be
            character-offset integers denoting the slice into the original string.
    
    Returns:
        tags (list):
            A list of unicode strings, describing the tags. Each tag string will
            be of the form either "", "O" or "{action}-{label}", where action is one
            of "B", "I", "L", "U". The string "-" is used where the entity
            offsets don't align with the tokenization in the Doc object. The
            training algorithm will view these as missing values. "O" denotes
            a non-entity token. "B" denotes the beginning of a multi-token entity,
            "I" the inside of an entity of three or more tokens, and "L" the end
            of an entity of two or more tokens. "U" denotes a single-token entity.

    Example:
        text = 'I like London.'
        entities = [(len('I like '), len('I like London'), 'LOC')]
        doc = nlp.tokenizer(text)

        tags = biluo_tags_from_offsets(doc, entities)
        
        assert tags == ['O', 'O', 'U-LOC', 'O']
    '''
    starts = {token.idx: token.i for token in doc}
    ends = {token.idx+len(token): token.i for token in doc}
    biluo = ['-' for _ in doc]
    # Handle entity cases
    for start_char, end_char, label in entities:
        start_token = starts.get(start_char)
        end_token = ends.get(end_char)
        # Only interested if the tokenization is correct
        if start_token is not None and end_token is not None:
            if start_token == end_token:
                biluo[start_token] = 'U-%s' % label
            else:
                biluo[start_token] = 'B-%s' % label
                for i in range(start_token+1, end_token):
                    biluo[i] = 'I-%s' % label
                biluo[end_token] = 'L-%s' % label
    # Now distinguish the O cases from ones where we miss the tokenization
    entity_chars = set()
    for start_char, end_char, label in entities:
        for i in range(start_char, end_char):
            entity_chars.add(i)
    for token in doc:
        for i in range(token.idx, token.idx+len(token)):
            if i in entity_chars:
                break
        else:
            biluo[token.i] = 'O'
    return biluo


def is_punct_label(label):
    return label == 'P' or label.lower() == 'punct'
