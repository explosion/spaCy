# cython: profile=True
# coding: utf8
from __future__ import unicode_literals, print_function

import re
import ujson
import random
import cytoolz
import itertools

from .syntax import nonproj
from .tokens import Doc
from .errors import Errors
from . import util
from .util import minibatch


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
            if start is None:
                raise ValueError(Errors.E067.format(tags=tags[:i+1]))
            continue
        if tag.startswith('U'):
            entities.append((tag[2:], i, i))
        elif tag.startswith('B'):
            start = i
        elif tag.startswith('L'):
            entities.append((tag[2:], start, i))
            start = None
        else:
            raise ValueError(Errors.E068.format(tag=tag))
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
        m_brackets.extend((b['first'] + i, b['last'] + i, b['label'])
                          for b in brackets)
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
    cand_words = [punct_re.sub('', w).lower() for w in cand_words]
    gold_words = [punct_re.sub('', w).lower() for w in gold_words]

    if cand_words == gold_words:
        return 0, ''.join(['M' for _ in gold_words])
    mem = Pool()
    n_cand = len(cand_words)
    n_gold = len(gold_words)
    # Levenshtein distance, except we need the history, and we may want
    # different costs. Mark operations with a string, and score the history
    # using _edit_cost.
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


class GoldCorpus(object):
    """An annotated corpus, using the JSON file format. Manages
    annotations for tagging, dependency parsing and NER."""
    def __init__(self, train_path, dev_path, gold_preproc=True, limit=None):
        """Create a GoldCorpus.

        train_path (unicode or Path): File or directory of training data.
        dev_path (unicode or Path): File or directory of development data.
        RETURNS (GoldCorpus): The newly created object.
        """
        self.train_path = util.ensure_path(train_path)
        self.dev_path = util.ensure_path(dev_path)
        self.limit = limit
        self.train_locs = self.walk_corpus(self.train_path)
        self.dev_locs = self.walk_corpus(self.dev_path)

    @property
    def train_tuples(self):
        i = 0
        for loc in self.train_locs:
            gold_tuples = read_json_file(loc)
            for item in gold_tuples:
                yield item
                i += len(item[1])
                if self.limit and i >= self.limit:
                    break

    @property
    def dev_tuples(self):
        i = 0
        for loc in self.dev_locs:
            gold_tuples = read_json_file(loc)
            for item in gold_tuples:
                yield item
                i += len(item[1])
                if self.limit and i >= self.limit:
                    break

    def count_train(self):
        n = 0
        i = 0
        for raw_text, paragraph_tuples in self.train_tuples:
            n += sum([len(s[0][1]) for s in paragraph_tuples])
            if self.limit and i >= self.limit:
                break
            i += len(paragraph_tuples)
        return n

    def train_docs(self, nlp, gold_preproc=False,
                   projectivize=False, max_length=None,
                   noise_level=0.0):
        train_tuples = self.train_tuples
        if projectivize:
            train_tuples = nonproj.preprocess_training_data(
                self.train_tuples, label_freq_cutoff=100)
        random.shuffle(train_tuples)
        gold_docs = self.iter_gold_docs(nlp, train_tuples, gold_preproc,
                                        max_length=max_length,
                                        noise_level=noise_level)
        yield from gold_docs

    def dev_docs(self, nlp, gold_preproc=False):
        gold_docs = self.iter_gold_docs(nlp, self.dev_tuples, gold_preproc)
        yield from gold_docs

    @classmethod
    def iter_gold_docs(cls, nlp, tuples, gold_preproc, max_length=None,
                       noise_level=0.0):
        for raw_text, paragraph_tuples in tuples:
            if gold_preproc:
                raw_text = None
            else:
                paragraph_tuples = merge_sents(paragraph_tuples)
            docs = cls._make_docs(nlp, raw_text, paragraph_tuples,
                                  gold_preproc, noise_level=noise_level)
            golds = cls._make_golds(docs, paragraph_tuples)
            for doc, gold in zip(docs, golds):
                if (not max_length) or len(doc) < max_length:
                    yield doc, gold

    @classmethod
    def _make_docs(cls, nlp, raw_text, paragraph_tuples, gold_preproc,
                   noise_level=0.0):
        if raw_text is not None:
            raw_text = add_noise(raw_text, noise_level)
            return [nlp.make_doc(raw_text)]
        else:
            return [Doc(nlp.vocab,
                        words=add_noise(sent_tuples[1], noise_level))
                    for (sent_tuples, brackets) in paragraph_tuples]

    @classmethod
    def _make_golds(cls, docs, paragraph_tuples):
        if len(docs) != len(paragraph_tuples):
            raise ValueError(Errors.E070.format(n_docs=len(docs),
                                                n_annots=len(paragraph_tuples)))
        if len(docs) == 1:
            return [GoldParse.from_annot_tuples(docs[0],
                                                paragraph_tuples[0][0])]
        else:
            return [GoldParse.from_annot_tuples(doc, sent_tuples)
                    for doc, (sent_tuples, brackets)
                    in zip(docs, paragraph_tuples)]

    @staticmethod
    def walk_corpus(path):
        if not path.is_dir():
            return [path]
        paths = [path]
        locs = []
        seen = set()
        for path in paths:
            if str(path) in seen:
                continue
            seen.add(str(path))
            if path.parts[-1].startswith('.'):
                continue
            elif path.is_dir():
                paths.extend(path.iterdir())
            elif path.parts[-1].endswith('.json'):
                locs.append(path)
        return locs


def add_noise(orig, noise_level):
    if random.random() >= noise_level:
        return orig
    elif type(orig) == list:
        corrupted = [_corrupt(word, noise_level) for word in orig]
        corrupted = [w for w in corrupted if w]
        return corrupted
    else:
        return ''.join(_corrupt(c, noise_level) for c in orig)


def _corrupt(c, noise_level):
    if random.random() >= noise_level:
        return c
    elif c == ' ':
        return '\n'
    elif c == '\n':
        return ' '
    elif c in ['.', "'", "!", "?"]:
        return ''
    else:
        return c.lower()


def read_json_file(loc, docs_filter=None, limit=None):
    loc = util.ensure_path(loc)
    if loc.is_dir():
        for filename in loc.iterdir():
            yield from read_json_file(loc / filename, limit=limit)
    else:
        with loc.open('r', encoding='utf8') as file_:
            docs = ujson.load(file_)
        if limit is not None:
            docs = docs[:limit]
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
                        tags.append(token.get('tag', '-'))
                        heads.append(token.get('head', 0) + i)
                        labels.append(token.get('dep', ''))
                        # Ensure ROOT label is case-insensitive
                        if labels[-1].lower() == 'root':
                            labels[-1] = 'ROOT'
                        ner.append(token.get('ner', '-'))
                    sents.append([
                        [ids, words, tags, heads, labels, ner],
                        sent.get('brackets', [])])
                if sents:
                    yield [paragraph.get('raw', None), sents]


def iob_to_biluo(tags):
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
    tag = tags.pop(0)
    target_in = 'I' + tag[1:]
    target_last = 'L' + tag[1:]
    length = 1
    while tags and tags[0] in {target_in, target_last}:
        length += 1
        tags.pop(0)
    label = tag[2:]
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
        return cls(doc, words=words, tags=tags, heads=heads, deps=deps,
                   entities=entities, make_projective=make_projective)

    def __init__(self, doc, annot_tuples=None, words=None, tags=None,
                 heads=None, deps=None, entities=None, make_projective=False,
                 cats=None):
        """Create a GoldParse.

        doc (Doc): The document the annotations refer to.
        words (iterable): A sequence of unicode word strings.
        tags (iterable): A sequence of strings, representing tag annotations.
        heads (iterable): A sequence of integers, representing syntactic
            head offsets.
        deps (iterable): A sequence of strings, representing the syntactic
            relation types.
        entities (iterable): A sequence of named entity annotations, either as
            BILUO tag strings, or as `(start_char, end_char, label)` tuples,
            representing the entity positions.
        cats (dict): Labels for text classification. Each key in the dictionary
            may be a string or an int, or a `(start_char, end_char, label)`
            tuple, indicating that the label is applied to only part of the
            document (usually a sentence). Unlike entity annotations, label
            annotations can overlap, i.e. a single word can be covered by
            multiple labelled spans. The TextCategorizer component expects
            true examples of a label to have the value 1.0, and negative
            examples of a label to have the value 0.0. Labels not in the
            dictionary are treated as missing - the gradient for those labels
            will be zero.
        RETURNS (GoldParse): The newly constructed object.
        """
        if words is None:
            words = [token.text for token in doc]
        if tags is None:
            tags = [None for _ in doc]
        if heads is None:
            heads = [None for token in doc]
        if deps is None:
            deps = [None for _ in doc]
        if entities is None:
            entities = [None for _ in doc]
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
        self.c.labels = <attr_t*>self.mem.alloc(len(doc), sizeof(attr_t))
        self.c.has_dep = <int*>self.mem.alloc(len(doc), sizeof(int))
        self.c.sent_start = <int*>self.mem.alloc(len(doc), sizeof(int))
        self.c.ner = <Transition*>self.mem.alloc(len(doc), sizeof(Transition))

        self.cats = {} if cats is None else dict(cats)
        self.words = [None] * len(doc)
        self.tags = [None] * len(doc)
        self.heads = [None] * len(doc)
        self.labels = [None] * len(doc)
        self.ner = [None] * len(doc)

        self.cand_to_gold = align([t.orth_ for t in doc], words)
        self.gold_to_cand = align(words, [t.orth_ for t in doc])

        annot_tuples = (range(len(words)), words, tags, heads, deps, entities)
        self.orig_annot = list(zip(*annot_tuples))

        for i, gold_i in enumerate(self.cand_to_gold):
            if doc[i].text.isspace():
                self.words[i] = doc[i].text
                self.tags[i] = '_SP'
                self.heads[i] = None
                self.labels[i] = None
                self.ner[i] = 'O'
            if gold_i is None:
                pass
            else:
                self.words[i] = words[gold_i]
                self.tags[i] = tags[gold_i]
                if heads[gold_i] is None:
                    self.heads[i] = None
                else:
                    self.heads[i] = self.gold_to_cand[heads[gold_i]]
                self.labels[i] = deps[gold_i]
                self.ner[i] = entities[gold_i]

        cycle = nonproj.contains_cycle(self.heads)
        if cycle is not None:
            raise ValueError(Errors.E069.format(cycle=cycle))

        if make_projective:
            proj_heads, _ = nonproj.projectivize(self.heads, self.labels)
            self.heads = proj_heads

    def __len__(self):
        """Get the number of gold-standard tokens.

        RETURNS (int): The number of gold-standard tokens.
        """
        return self.length

    @property
    def is_projective(self):
        """Whether the provided syntactic annotations form a projective
        dependency tree.
        """
        return not nonproj.is_nonproj_tree(self.heads)

    @property
    def sent_starts(self):
        return [self.c.sent_start[i] for i in range(self.length)]


def biluo_tags_from_offsets(doc, entities, missing='O'):
    """Encode labelled spans into per-token tags, using the
    Begin/In/Last/Unit/Out scheme (BILUO).

    doc (Doc): The document that the entity offsets refer to. The output tags
        will refer to the token boundaries within the document.
    entities (iterable): A sequence of `(start, end, label)` triples. `start`
        and `end` should be character-offset integers denoting the slice into
        the original string.
    RETURNS (list): A list of unicode strings, describing the tags. Each tag
        string will be of the form either "", "O" or "{action}-{label}", where
        action is one of "B", "I", "L", "U". The string "-" is used where the
        entity offsets don't align with the tokenization in the `Doc` object.
        The training algorithm will view these as missing values. "O" denotes a
        non-entity token. "B" denotes the beginning of a multi-token entity,
        "I" the inside of an entity of three or more tokens, and "L" the end
        of an entity of two or more tokens. "U" denotes a single-token entity.

    EXAMPLE:
        >>> text = 'I like London.'
        >>> entities = [(len('I like '), len('I like London'), 'LOC')]
        >>> doc = nlp.tokenizer(text)
        >>> tags = biluo_tags_from_offsets(doc, entities)
        >>> assert tags == ['O', 'O', 'U-LOC', 'O']
    """
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
            biluo[token.i] = missing
    return biluo


def offsets_from_biluo_tags(doc, tags):
    """Encode per-token tags following the BILUO scheme into entity offsets.

    doc (Doc): The document that the BILUO tags refer to.
    entities (iterable): A sequence of BILUO tags with each tag describing one
        token. Each tags string will be of the form of either "", "O" or
        "{action}-{label}", where action is one of "B", "I", "L", "U".
    RETURNS (list): A sequence of `(start, end, label)` triples. `start` and
        `end` will be character-offset integers denoting the slice into the
        original string.
    """
    token_offsets = tags_to_entities(tags)
    offsets = []
    for label, start_idx, end_idx in token_offsets:
        span = doc[start_idx : end_idx + 1]
        offsets.append((span.start_char, span.end_char, label))
    return offsets


def is_punct_label(label):
    return label == 'P' or label.lower() == 'punct'
