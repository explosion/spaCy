#!/usr/bin/env python
from __future__ import unicode_literals
from __future__ import print_function
import sys

import falcon
import json
from os import path
from collections import defaultdict
import pprint
import numpy

import spacy.en
from spacy.attrs import ORTH, SPACY, TAG, POS, ENT_IOB, ENT_TYPE
from spacy.parts_of_speech import NAMES as UNIV_POS_NAMES

try:
  unicode
except NameError:
  unicode = str


NLU = spacy.en.English()


def merge_entities(doc):
    ents = [(e[0].idx, e[len(e)-1].idx + len(e[len(e)-1]), e.label_, e.text)
            for e in doc.ents if len(e) >= 2]
    for start, end, label, lemma in ents:
        merged = doc.merge(start, end, label, text, label)
        assert merged != None


def merge_nps(doc):
    nps = [(np[0].idx, np[-1].idx + len(np[-1]), np.root.tag_, np.text)
            for np in doc.noun_chunks if len(np) >= 2]
    
    for start, end, ent_type, lemma in nps:
        doc.merge(start, end, u'NP', lemma, ent_type)


def merge_punct(tokens):
    # Merge punctuation onto its head
    collect = False
    start = None
    merges = []

    for word in tokens:
        if word.whitespace_:
            if collect:
                span = tokens[start:word.i+1]
                if len(span) >= 2:
                    merges.append((
                        span[0].idx,
                        span[-1].idx + len(span[-1]),
                        span.root.tag_,
                        span.root.lemma_,
                        span.root.ent_type_))
                collect = False
                start = None
        elif not collect:
            collect = True
            start = word.i
    if collect:
        span = tokens[start:len(tokens)]
        merges.append((span[0].idx, span[-1].idx + len(span[-1]),
                       span.root.tag_, span.root.lemma_, span.root.ent_type_))
    for merge in merges:
         tokens.merge(*merge)


def get_actions(parse_state, n_actions):
    actions = []
    queue = list(sorted(parse_state.queue))
    stack = list(sorted(parse_state.stack))
    stack = []
    actions.append({'label': 'shift', 'key': 'S', 'binding': 38,
                    'is_valid': NLU.parser.moves.is_valid(parse_state, 'S')})
    actions.append({'label': 'left', 'key': 'L', 'binding': 37,
                    'is_valid': NLU.parser.moves.is_valid(parse_state, 'L-det')})
    actions.append({'label': 'predict', 'key': '_', 'binding': 32,
                    'is_valid': bool(parse_state.queue or parse_state.stack)})
    actions.append({'label': 'right', 'key': 'R', 'binding': 39,
                    'is_valid': NLU.parser.moves.is_valid(parse_state, 'R-dobj')})
    actions.append({'label': 'undo', 'key': '-', 'binding': 8,
                    'is_valid': n_actions != 0})
    actions.append({'label': 'reduce', 'key': 'D', 'binding': 40,
                    'is_valid': NLU.parser.moves.is_valid(parse_state, 'D')})
    return actions


class Model(object):
    def to_json(self):
        return {name: _as_json(value) for name, value in self.__dict__.items()
                if not name.startswith('_')}

def _as_json(value):
    if hasattr(value, 'to_json'):
        return value.to_json()
    elif isinstance(value, list):
        return [_as_json(v) for v in value]
    elif isinstance(value, set):
        return {key: True for key in value}
    else:
        return value


def _parse_history(history):
    if history and history.endswith(','):
        history = history[:-1]
    history = history.strip().split(',') if history else tuple()
    new_hist = []
    history_length = len(history)
    for action in history:
        if action == '-':
            if new_hist:
                new_hist.pop()
        else:
            new_hist.append(action)
    return new_hist, history_length


def apply_edits(tokens, word_edits, tag_edits):
    new_words = []
    attrs = (POS, ENT_TYPE, ENT_IOB)
    new_analysis = numpy.zeros(shape=(len(tokens), len(attrs)), dtype=numpy.int32)
    for word in tokens:
        key = str(word.i)
        new_words.append(word_edits.get(key, word.orth_))
        tag = tag_edits.get(key, word.pos_)
        if tag in UNIV_POS_NAMES:
            new_analysis[word.i, 0] = UNIV_POS_NAMES[tag]
            # Set ent_type=0 and IOB="O"
            new_analysis[word.i, 1] = 0
            new_analysis[word.i, 2] = 2
        else:
            new_analysis[word.i, 0] = word.pos
            new_analysis[word.i, 1] = NLU.vocab.strings[tag]
            new_analysis[word.i, 2] = 3

    doc = NLU.tokenizer.tokens_from_list(new_words)
    doc.from_array(attrs, new_analysis)
    NLU.parser(doc)
    return doc


class Parse(Model):
    def __init__(self, doc, states, actions, **kwargs):
        word_edits = kwargs.get('words', {})
        tag_edits = kwargs.get('tags', {})
        if word_edits or tag_edits:
            doc = apply_edits(doc, word_edits, tag_edits)
        notes = kwargs.get('notes', {})
        self.actions = actions
        self.words = [Word(w, w.i in word_edits, w.i in tag_edits) for w in doc]
        self.states = states
        self.notes = notes
        for word in doc:
            print(word.orth_, word.head.orth_)

    @classmethod
    def from_text(cls, text, **kwargs):
        tokens = NLU(text)
        #merge_entities(tokens)
        merge_nps(tokens)
        #merge_punct(tokens)
        return cls(tokens, [State.from_doc(tokens)], [], **kwargs)

    @classmethod
    def from_history(cls, text, history, **kwargs):
        if not isinstance(text, unicode):
            text = text.decode('utf8')
        text = text.replace('-SLASH-', '/')
        history, history_length = _parse_history(history)

        tokens = NLU.tokenizer(text)
        NLU.tagger(tokens)
        NLU.matcher(tokens)

        with NLU.parser.step_through(tokens) as state:
            for action in history:
                state.transition(action)

        NLU.entity(tokens)
        actions = get_actions(state.stcls, len(history))
        return Parse(tokens, [State(state.heads, state.deps, state.stack, state.queue)],
                     actions, **kwargs)

    @classmethod
    def with_history(cls, text):
        tokens = NLU.tokenizer(text)
        NLU.tagger(tokens)
        NLU.matcher(tokens)

        with NLU.parser.step_through(tokens) as state:
            states = []
            while not state.is_final:
                action = state.predict()
                state.transition(action)
                states.append(State(state.heads, state.deps, state.stack, state.queue))
        actions = [
            {'label': 'prev', 'key': 'P', 'binding': 37, 'is_valid': True},
            {'label': 'next', 'key': 'N', 'binding': 39, 'is_valid': True}
        ]
        return Parse(state.doc, states, actions)


class Word(Model):
    def __init__(self, token, is_w_edit=False, is_t_edit=False):
        self.word = token.orth_
        self.tag = token.pos_
        self.tag = token.pos_ if not token.ent_type_ else token.ent_type_
        self.is_entity = token.ent_iob in (1, 3)
        self.is_w_edit = is_w_edit
        self.is_t_edit = is_t_edit
        self.prob = token.prob


class State(Model):
    def __init__(self, heads, deps, stack, queue):
        Model.__init__(self)

        queue = [w for w in queue if w >= 0]
        self.focus = min(queue) if queue else -1
        self.is_final = bool(not stack and not queue)
        self.stack = set(stack)
        self.arrows = self._get_arrows(heads, deps)

    @classmethod
    def from_doc(cls, doc):
        return cls([w.head.i for w in doc], [w.dep_ for w in doc], [], [])

    def _get_arrows(self, heads, deps):
        arcs = defaultdict(dict)
        for i, (head, dep) in enumerate(zip(heads, deps)):
            if i < head:
                arcs[head - i][i] = Arrow(i, head, dep)
            elif i > head:
                arcs[i - head][head] = Arrow(i, head, dep)
        output = []
        for level in range(1, len(heads)):
            level_arcs = []
            for i in range(len(heads) - level):
                level_arcs.append(arcs[level].get(i))
            output.append(level_arcs)
        while output and all(arc is None for arc in output[-1]):
            output.pop()
        return output


class Arrow(Model):
    def __init__(self, word, head, label):
        self.dir = 'left' if head > word else 'right'
        self.label = label


class Endpoint(object):
    def set_header(self, resp):
        resp.content_type = 'text/string'
        resp.append_header('Access-Control-Allow-Origin', "*")
        resp.status = falcon.HTTP_200

    def set_body(self, resp, parse):
        resp.body = json.dumps(parse.to_json(), indent=4)

    def on_get(self, req, resp, text):
        if not isinstance(text, unicode):
            text = text.decode('utf8')
        self.set_body(resp, self.get_parse(text))
        self.set_header(resp)

    def on_post(self, req, resp):
        try:
            body_bytes = req.stream.read()
            json_data = json.loads(body_bytes.decode('utf8'))
            text = json_data['text']
            if not isinstance(text, unicode):
                text = text.decode('utf8')
            self.set_body(resp, self.get_parse(text))
            self.set_header(resp)
        except:
            pass


class ParseEP(Endpoint):
    def get_parse(self, text, **kwargs):
        return Parse.from_text(text, **kwargs)


class StepsEP(Endpoint):
    def get_parse(self, text):
        print('Step=', repr(text))
        return Parse.with_history(text)


class ManualEP(Endpoint):
    def get_parse(self, text, **kwargs):
        print('Manual=', repr(text))
        if '/' in text:
            text, actions = text.rsplit('/', 1)
        else:
            actions = ''
        return Parse.from_history(text, actions, **kwargs)

    def on_get(self, req, resp, text, actions=''):
        if not isinstance(text, unicode):
            text = text.decode('utf8')
        self.set_body(resp, self.get_parse(text + '/' + actions))
        self.set_header(resp)

    def on_post(self, req, resp):
        self.set_header(resp)
        body_bytes = req.stream.read()
        json_data = json.loads(body_bytes.decode('utf8'))
        print(json_data)
        params = json_data.get('params', {})
        self.set_body(resp, self.get_parse(json_data['text'], **params))


app = falcon.API()

remote_man = ManualEP()
remote_parse = ParseEP()
remote_steps = StepsEP()

app.add_route('/api/displacy/parse/', remote_parse)
app.add_route('/api/displacy/parse/{text}/', remote_parse)

app.add_route('/api/displacy/steps/', remote_steps)
app.add_route('/api/displacy/steps/{text}/', remote_steps)

app.add_route('/api/displacy/manual/', remote_man)
app.add_route('/api/displacy/manual/{text}/', remote_man)
app.add_route('/api/displacy/manual/{text}/{actions}', remote_man)


if __name__ == '__main__':
    text, actions = open(sys.argv[1]).read().strip().split('\n')
    parse = Parse.from_text(text)
    pprint.pprint(parse.to_json())
