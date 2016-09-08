# cython: infer_types=True
# cython: profile=True
from libc.stdint cimport uint64_t
from libc.string cimport memcpy, memset
from libc.math cimport sqrt

from cymem.cymem cimport Pool, Address
from murmurhash.mrmr cimport hash64

from thinc.typedefs cimport weight_t, class_t, feat_t, atom_t, hash_t, idx_t
from thinc.linear.avgtron cimport AveragedPerceptron
from thinc.linalg cimport VecVec
from thinc.structs cimport NeuralNetC, SparseArrayC, ExampleC
from thinc.structs cimport FeatureC
from thinc.extra.eg cimport Example
from thinc.neural.forward cimport softmax

from preshed.maps cimport map_get
from preshed.maps cimport MapStruct

from ..structs cimport TokenC
from ._state cimport StateC
from ._parse_features cimport fill_context
from ._parse_features cimport CONTEXT_SIZE
from ._parse_features cimport fill_context
from ._parse_features import ner as ner_templates
from ._parse_features cimport *
from .transition_system cimport TransitionSystem
from ..tokens.doc cimport Doc


cdef class ParserPerceptron(AveragedPerceptron):
    @property
    def widths(self):
        return (self.extracter.nr_templ,)

    def update(self, Example eg, loss='regression'):
        self.time += 1
        best = eg.best
        guess = eg.guess
        assert best >= 0, best
        assert guess >= 0, guess
        d_losses = {}
        if loss == 'regression':
            # Does regression on negative cost. Sort of cute?
            # Clip to guess and best, to keep gradient sparse.
            d_losses[guess] = -2 * (-eg.c.costs[guess] - eg.c.scores[guess])
            d_losses[best] = -2 * (-eg.c.costs[best] - eg.c.scores[best])
            #for i in range(eg.c.nr_class):
            #    if eg.c.is_valid[i] \
            #    and eg.c.scores[i] >= eg.c.scores[best]:
            #        d_losses[i] = -2 * (-eg.c.costs[i] - eg.c.scores[i])
        elif loss == 'nll':
            # Clip to guess and best, to keep gradient sparse.
            if eg.c.scores[guess] == 0.0:
                d_losses[guess] = 1.0
                d_losses[best] = -1.0
            else:
                softmax(eg.c.scores, eg.c.nr_class)
                for i in range(eg.c.nr_class):
                    if eg.c.is_valid[i] \
                    and eg.c.scores[i] >= eg.c.scores[best]:
                        d_losses[i] = eg.c.scores[i] - (eg.c.costs[i] <= 0)
        elif loss == 'hinge':
            for i in range(eg.c.nr_class):
                if eg.c.is_valid[i] \
                and eg.c.costs[i] > 0 \
                and eg.c.scores[i] > (eg.c.scores[best]-1):
                    margin = eg.c.scores[i] - (eg.c.scores[best] - 1)
                    d_losses[i] = margin
                    d_losses[best] = min(-margin, d_losses.get(best, 0.0))
        elif loss == 'perceptron':
            if guess != best:
                d_losses = {best: -1.0, guess: 1.0}
        step = 0.0
        i = 0
        for clas, d_loss in sorted(d_losses.items()):
            for feat in eg.c.features[:eg.c.nr_feat]:
                self.update_weight(feat.key, clas, feat.value * d_loss)
                i += 1
        #self.total_L1 += self.l1_penalty *  self.learn_rate
        return sum(map(abs, d_losses.values()))

    cdef int set_featuresC(self, FeatureC* feats, const void* _state) nogil: 
        cdef atom_t[CONTEXT_SIZE] context
        memset(context, 0, sizeof(context))
        state = <const StateC*>_state
        fill_context(context, state)
        return self.extracter.set_features(feats, context)

    def _update_from_history(self, TransitionSystem moves, Doc doc, history, weight_t grad):
        cdef Pool mem = Pool()
        features = <FeatureC*>mem.alloc(self.nr_feat, sizeof(FeatureC))
        
        cdef StateClass stcls = StateClass.init(doc.c, doc.length)
        moves.initialize_state(stcls.c)

        cdef class_t clas
        self.time += 1
        for clas in history:
            nr_feat = self.set_featuresC(features, stcls.c)
            for feat in features[:nr_feat]:
                self.update_weight(feat.key, clas, feat.value * grad)
            moves.c[clas].do(stcls.c, moves.c[clas].label)
 

cdef class ParserNeuralNet(NeuralNet):
    def __init__(self, shape, **kwargs):
        if kwargs.get('feat_set', 'parser') == 'parser':
            vector_widths = [4] * 76
            slots =  [0, 1, 2, 3] # S0
            slots += [4, 5, 6, 7] # S1
            slots += [8, 9, 10, 11] # S2
            slots += [12, 13, 14, 15] # S3+
            slots += [16, 17, 18, 19] # B0
            slots += [20, 21, 22, 23] # B1
            slots += [24, 25, 26, 27] # B2
            slots += [28, 29, 30, 31] # B3+
            slots += [32, 33, 34, 35] * 2 # S0l, S0r
            slots += [36, 37, 38, 39] * 2 # B0l, B0r
            slots += [40, 41, 42, 43] * 2 # S1l, S1r
            slots += [44, 45, 46, 47] * 2 # S2l, S2r
            slots += [48, 49, 50, 51, 52, 53, 54, 55]
            slots += [53, 54, 55, 56]
            self.extracter = None
        else:
            templates = ner_templates
            vector_widths = [4] * len(templates)
            slots = list(range(templates))
            self.extracter = ConjunctionExtracter(templates)
 
        input_length = sum(vector_widths[slot] for slot in slots)
        widths = [input_length] + shape
        NeuralNet.__init__(self, widths, embed=(vector_widths, slots), **kwargs)

    @property
    def nr_feat(self):
        if self.extracter is None:
            return 2000
        else:
            return self.extracter.nr_feat

    cdef int set_featuresC(self, FeatureC* feats, const void* _state) nogil: 
        cdef atom_t[CONTEXT_SIZE] context
        state = <const StateC*>_state
        if self.extracter is not None:
            fill_context(context, state)
            return self.extracter.set_features(feats, context)
        memset(feats, 0, 2000 * sizeof(FeatureC))
        start = feats

        feats = _add_token(feats, 0, state.S_(0), 1.0)
        feats = _add_token(feats, 4, state.S_(1), 1.0)
        feats = _add_token(feats, 8, state.S_(2), 1.0)
        # Rest of the stack, with exponential decay
        for i in range(3, state.stack_depth()):
            feats = _add_token(feats, 12, state.S_(i), 1.0 * 0.5**(i-2))
        feats = _add_token(feats, 16, state.B_(0), 1.0)
        feats = _add_token(feats, 20, state.B_(1), 1.0)
        feats = _add_token(feats, 24, state.B_(2), 1.0)
        # Rest of the buffer, with exponential decay
        for i in range(3, min(8, state.buffer_length())):
            feats = _add_token(feats, 28, state.B_(i), 1.0 * 0.5**(i-2))
        feats = _add_subtree(feats, 32, state, state.S(0))
        feats = _add_subtree(feats, 40, state, state.B(0))
        feats = _add_subtree(feats, 48, state, state.S(1))
        feats = _add_subtree(feats, 56, state, state.S(2))
        feats = _add_pos_bigram(feats, 64, state.S_(0), state.B_(0))
        feats = _add_pos_bigram(feats, 65, state.S_(1), state.S_(0))
        feats = _add_pos_bigram(feats, 66, state.S_(1), state.B_(0))
        feats = _add_pos_bigram(feats, 67, state.S_(0), state.B_(1))
        feats = _add_pos_bigram(feats, 68, state.S_(0), state.R_(state.S(0), 1))
        feats = _add_pos_bigram(feats, 69, state.S_(0), state.R_(state.S(0), 2))
        feats = _add_pos_bigram(feats, 70, state.S_(0), state.L_(state.S(0), 1))
        feats = _add_pos_bigram(feats, 71, state.S_(0), state.L_(state.S(0), 2))
        feats = _add_pos_trigram(feats, 72, state.S_(1), state.S_(0), state.B_(0))
        feats = _add_pos_trigram(feats, 73, state.S_(0), state.B_(0), state.B_(1))
        feats = _add_pos_trigram(feats, 74, state.S_(0), state.R_(state.S(0), 1),
                                 state.R_(state.S(0), 2))
        feats = _add_pos_trigram(feats, 75, state.S_(0), state.L_(state.S(0), 1),
                                 state.L_(state.S(0), 2))
        return feats - start

    #cdef void _set_delta_lossC(self, weight_t* delta_loss,
    #        const weight_t* cost, const weight_t* scores) nogil:
    #    for i in range(self.c.widths[self.c.nr_layer-1]):
    #        delta_loss[i] = cost[i]

    #cdef void _softmaxC(self, weight_t* out) nogil:
    #    pass
    
    cdef void dropoutC(self, FeatureC* feats, weight_t drop_prob,
            int nr_feat) nogil:
        pass
    
    def _update_from_history(self, TransitionSystem moves, Doc doc, history, weight_t grad):
        cdef Pool mem = Pool()
        features = <FeatureC*>mem.alloc(self.nr_feat, sizeof(FeatureC))
        is_valid = <int*>mem.alloc(moves.n_moves, sizeof(int))
        costs = <weight_t*>mem.alloc(moves.n_moves, sizeof(weight_t))
 
        stcls = StateClass.init(doc.c, doc.length)
        moves.initialize_state(stcls.c)
        cdef uint64_t[2] key
        key[0] = hash64(doc.c, sizeof(TokenC) * doc.length, 0)
        key[1] = 0
        cdef uint64_t clas
        for clas in history:
            memset(costs, 0, moves.n_moves * sizeof(costs[0]))
            for i in range(moves.n_moves):
                is_valid[i] = 1
            nr_feat = self.set_featuresC(features, stcls.c)
            moves.set_valid(is_valid, stcls.c)
            # Update with a sparse gradient: everything's 0, except our class.
            # Remember, this is a component of the global update. It's not our
            # "job" here to think about the other beam candidates. We just want
            # to work on this sequence. However, other beam candidates will
            # have gradients that refer to the same state.
            # We therefore have a key that indicates the current sequence, so that
            # the model can merge updates that refer to the same state together,
            # by summing their gradients.
            costs[clas] = grad
            self.updateC(features,
                nr_feat, costs, is_valid, False, key[0])
            moves.c[clas].do(stcls.c, moves.c[clas].label)
            # Build a hash of the state sequence.
            # Position 0 represents the previous sequence, position 1 the new class.
            # So we want to do:
            # key.prev = hash((key.prev, key.new))
            # key.new = clas
            key[1] = clas
            key[0] = hash64(key, sizeof(key), 0)


cdef inline FeatureC* _add_token(FeatureC* feats,
        int slot, const TokenC* token, weight_t value) nogil:
    # Word
    feats.i = slot
    feats.key = token.lex.norm
    feats.value = value
    feats += 1
    # POS tag
    feats.i = slot+1
    feats.key = token.tag
    feats.value = value
    feats += 1
    # Dependency label 
    feats.i = slot+2
    feats.key = token.dep
    feats.value = value
    feats += 1
    # Word, label, tag
    feats.i = slot+3
    cdef uint64_t key[3]
    key[0] = token.lex.cluster
    key[1] = token.tag
    key[2] = token.dep
    feats.key = hash64(key, sizeof(key), 0)
    feats.value = value
    feats += 1
    return feats


cdef inline FeatureC* _add_characters(FeatureC* feats,
        int slot, uint64_t* chars, int length, weight_t value) with gil:
    nr_start_chars = 4
    nr_end_chars = 4
    for i in range(min(nr_start_chars, length)):
        feats.i = slot
        feats.key = chars[i]
        feats.value = value
        feats += 1
        slot += 1
    for _ in range(length, nr_start_chars):
        feats.i = slot
        feats.key = 0
        feats.value = 0
        feats += 1
        slot += 1
    for i in range(min(nr_end_chars, length)):
        feats.i = slot
        feats.key = chars[(length-nr_end_chars)+i]
        feats.value = value
        feats += 1
        slot += 1
    for _ in range(length, nr_start_chars):
        feats.i = slot
        feats.key = 0
        feats.value = 0
        feats += 1
        slot += 1
    return feats
 

cdef inline FeatureC* _add_subtree(FeatureC* feats, int slot, const StateC* state, int t) nogil:
    value = 1.0
    for i in range(state.n_R(t)):
        feats = _add_token(feats, slot, state.R_(t, i+1), value)
        value *= 0.5
    slot += 4
    value = 1.0
    for i in range(state.n_L(t)):
        feats = _add_token(feats, slot, state.L_(t, i+1), value)
        value *= 0.5
    return feats


cdef inline FeatureC* _add_pos_bigram(FeatureC* feat, int slot,
        const TokenC* t1, const TokenC* t2) nogil:
    cdef uint64_t[2] key
    key[0] = t1.tag
    key[1] = t2.tag
    feat.i = slot
    feat.key = hash64(key, sizeof(key), slot)
    feat.value = 1.0
    return feat+1
 

cdef inline FeatureC* _add_pos_trigram(FeatureC* feat, int slot,
        const TokenC* t1, const TokenC* t2, const TokenC* t3) nogil:
    cdef uint64_t[3] key
    key[0] = t1.tag
    key[1] = t2.tag
    key[2] = t3.tag
    feat.i = slot
    feat.key = hash64(key, sizeof(key), slot)
    feat.value = 1.0
    return feat+1
