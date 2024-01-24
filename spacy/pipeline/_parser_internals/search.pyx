# cython: experimental_cpp_class_def=True, cdivision=True, infer_types=True
cimport cython
from cymem.cymem cimport Pool
from libc.math cimport exp
from libc.string cimport memcpy, memset
from preshed.maps cimport PreshMap


cdef class Beam:
    def __init__(self, class_t nr_class, class_t width, weight_t min_density=0.0):
        assert nr_class != 0
        assert width != 0
        self.nr_class = nr_class
        self.width = width
        self.min_density = min_density
        self.size = 1
        self.t = 0
        self.mem = Pool()
        self.del_func = NULL
        self._parents = <_State*>self.mem.alloc(self.width, sizeof(_State))
        self._states = <_State*>self.mem.alloc(self.width, sizeof(_State))
        cdef int i
        self.histories = [[] for i in range(self.width)]
        self._parent_histories = [[] for i in range(self.width)]

        self.scores = <weight_t**>self.mem.alloc(self.width, sizeof(weight_t*))
        self.is_valid = <int**>self.mem.alloc(self.width, sizeof(weight_t*))
        self.costs = <weight_t**>self.mem.alloc(self.width, sizeof(weight_t*))
        for i in range(self.width):
            self.scores[i] = <weight_t*>self.mem.alloc(self.nr_class, sizeof(weight_t))
            self.is_valid[i] = <int*>self.mem.alloc(self.nr_class, sizeof(int))
            self.costs[i] = <weight_t*>self.mem.alloc(self.nr_class, sizeof(weight_t))

    def __len__(self):
        return self.size

    property score:
        def __get__(self):
            return self._states[0].score

    property min_score:
        def __get__(self):
            return self._states[self.size-1].score

    property loss:
        def __get__(self):
            return self._states[0].loss

    property probs:
        def __get__(self):
            return _softmax([self._states[i].score for i in range(self.size)])

    property scores:
        def __get__(self):
            return [self._states[i].score for i in range(self.size)]

    property histories:
        def __get__(self):
            return self.histories

    cdef int set_row(self, int i, const weight_t* scores, const int* is_valid,
                     const weight_t* costs) except -1:
        cdef int j
        for j in range(self.nr_class):
            self.scores[i][j] = scores[j]
            self.is_valid[i][j] = is_valid[j]
            self.costs[i][j] = costs[j]

    cdef int set_table(self, weight_t** scores, int** is_valid, weight_t** costs) except -1:
        cdef int i
        for i in range(self.width):
            memcpy(self.scores[i], scores[i], sizeof(weight_t) * self.nr_class)
            memcpy(self.is_valid[i], is_valid[i], sizeof(bint) * self.nr_class)
            memcpy(self.costs[i], costs[i], sizeof(int) * self.nr_class)

    cdef int initialize(self, init_func_t init_func, del_func_t del_func, int n, void* extra_args) except -1:
        for i in range(self.width):
            self._states[i].content = init_func(self.mem, n, extra_args)
            self._parents[i].content = init_func(self.mem, n, extra_args)
        self.del_func = del_func

    def __dealloc__(self):
        if self.del_func == NULL:
            return

        for i in range(self.width):
            self.del_func(self.mem, self._states[i].content, NULL)
            self.del_func(self.mem, self._parents[i].content, NULL)

    @cython.cdivision(True)
    cdef int advance(self, trans_func_t transition_func, hash_func_t hash_func,
                     void* extra_args) except -1:
        cdef weight_t** scores = self.scores
        cdef int** is_valid = self.is_valid
        cdef weight_t** costs = self.costs

        cdef Queue* q = new Queue()
        self._fill(q, scores, is_valid)
        # For a beam of width k, we only ever need 2k state objects. How?
        # Each transition takes a parent and a class and produces a new state.
        # So, we don't need the whole history --- just the parent. So at
        # each step, we take a parent, and apply one or more extensions to
        # it.
        self._parents, self._states = self._states, self._parents
        self._parent_histories, self.histories = self.histories, self._parent_histories
        cdef weight_t score
        cdef int p_i
        cdef int i = 0
        cdef class_t clas
        cdef _State* parent
        cdef _State* state
        cdef hash_t key
        cdef PreshMap seen_states = PreshMap(self.width)
        cdef uint64_t is_seen
        cdef uint64_t one = 1
        while i < self.width and not q.empty():
            data = q.top()
            p_i = data.second / self.nr_class
            clas = data.second % self.nr_class
            score = data.first
            q.pop()
            parent = &self._parents[p_i]
            # Indicates terminal state reached; i.e. state is done
            if parent.is_done:
                # Now parent will not be changed, so we don't have to copy.
                # Once finished, should also be unbranching.
                self._states[i], parent[0] = parent[0], self._states[i]
                parent.i = self._states[i].i
                parent.t = self._states[i].t
                parent.is_done = self._states[i].t
                self._states[i].score = score
                self.histories[i] = list(self._parent_histories[p_i])
                i += 1
            else:
                state = &self._states[i]
                # The supplied transition function should adjust the destination
                # state to be the result of applying the class to the source state
                transition_func(state.content, parent.content, clas, extra_args)
                key = hash_func(state.content, extra_args) if hash_func is not NULL else 0
                is_seen = <uint64_t>seen_states.get(key)
                if key == 0 or key == 1 or not is_seen:
                    if key != 0 and key != 1:
                        seen_states.set(key, <void*>one)
                    state.score = score
                    state.loss = parent.loss + costs[p_i][clas]
                    self.histories[i] = list(self._parent_histories[p_i])
                    self.histories[i].append(clas)
                    i += 1
        del q
        self.size = i
        assert self.size >= 1
        for i in range(self.width):
            memset(self.scores[i], 0, sizeof(weight_t) * self.nr_class)
            memset(self.costs[i], 0, sizeof(weight_t) * self.nr_class)
            memset(self.is_valid[i], 0, sizeof(int) * self.nr_class)
        self.t += 1

    cdef int check_done(self, finish_func_t finish_func, void* extra_args) except -1:
        cdef int i
        for i in range(self.size):
            if not self._states[i].is_done:
                self._states[i].is_done = finish_func(self._states[i].content, extra_args)
        for i in range(self.size):
            if not self._states[i].is_done:
                self.is_done = False
                break
        else:
            self.is_done = True

    @cython.cdivision(True)
    cdef int _fill(self, Queue* q, weight_t** scores, int** is_valid) except -1:
        """Populate the queue from a k * n matrix of scores, where k is the
        beam-width, and n is the number of classes.
        """
        cdef Entry entry
        cdef _State* s
        cdef int i, j, move_id
        assert self.size >= 1
        cdef vector[Entry] entries
        for i in range(self.size):
            s = &self._states[i]
            move_id = i * self.nr_class
            if s.is_done:
                # Update score by path average, following TACL '13 paper.
                if self.histories[i]:
                    entry.first = s.score + (s.score / self.t)
                else:
                    entry.first = s.score
                entry.second = move_id
                entries.push_back(entry)
            else:
                for j in range(self.nr_class):
                    if is_valid[i][j]:
                        entry.first = s.score + scores[i][j]
                        entry.second = move_id + j
                        entries.push_back(entry)
        cdef double max_, Z, cutoff
        if self.min_density == 0.0:
            for i in range(entries.size()):
                q.push(entries[i])
        elif not entries.empty():
            max_ = entries[0].first
            Z = 0.
            cutoff = 0.
            # Softmax into probabilities, so we can prune
            for i in range(entries.size()):
                if entries[i].first > max_:
                    max_ = entries[i].first
            for i in range(entries.size()):
                Z += exp(entries[i].first-max_)
            cutoff = (1. / Z) * self.min_density
            for i in range(entries.size()):
                prob = exp(entries[i].first-max_) / Z
                if prob >= cutoff:
                    q.push(entries[i])


cdef class MaxViolation:
    def __init__(self):
        self.p_score = 0.0
        self.g_score = 0.0
        self.Z = 0.0
        self.gZ = 0.0
        self.delta = -1
        self.cost = 0
        self.p_hist = []
        self.g_hist = []
        self.p_probs = []
        self.g_probs = []

    cpdef int check(self, Beam pred, Beam gold) except -1:
        cdef _State* p = &pred._states[0]
        cdef _State* g = &gold._states[0]
        cdef weight_t d = p.score - g.score
        if p.loss >= 1 and (self.cost == 0 or d > self.delta):
            self.cost = p.loss
            self.delta = d
            self.p_hist = list(pred.histories[0])
            self.g_hist = list(gold.histories[0])
            self.p_score = p.score
            self.g_score = g.score
            self.Z = 1e-10
            self.gZ = 1e-10
            for i in range(pred.size):
                if pred._states[i].loss > 0:
                    self.Z += exp(pred._states[i].score)
            for i in range(gold.size):
                if gold._states[i].loss == 0:
                    prob = exp(gold._states[i].score)
                    self.Z += prob
                    self.gZ += prob

    cpdef int check_crf(self, Beam pred, Beam gold) except -1:
        d = pred.score - gold.score
        seen_golds = set([tuple(gold.histories[i]) for i in range(gold.size)])
        if pred.loss > 0 and (self.cost == 0 or d > self.delta):
            p_hist = []
            p_scores = []
            g_hist = []
            g_scores = []
            for i in range(pred.size):
                if pred._states[i].loss > 0:
                    p_scores.append(pred._states[i].score)
                    p_hist.append(list(pred.histories[i]))
                # This can happen from non-monotonic actions
                # If we find a better gold analysis this way, be sure to keep it.
                elif pred._states[i].loss <= 0 \
                        and tuple(pred.histories[i]) not in seen_golds:
                    g_scores.append(pred._states[i].score)
                    g_hist.append(list(pred.histories[i]))
            for i in range(gold.size):
                if gold._states[i].loss == 0:
                    g_scores.append(gold._states[i].score)
                    g_hist.append(list(gold.histories[i]))

            all_probs = _softmax(p_scores + g_scores)
            p_probs = all_probs[:len(p_scores)]
            g_probs_all = all_probs[len(p_scores):]
            g_probs = _softmax(g_scores)

            self.cost = pred.loss
            self.delta = d
            self.p_hist = p_hist
            self.g_hist = g_hist
            # TODO: These variables are misnamed! These are the gradients of the loss.
            self.p_probs = p_probs
            # Intuition here:
            # The gradient of the loss is:
            # P(model) - P(truth)
            # Normally, P(truth) is 1 for the gold
            # But, if we want to do the "partial credit" scheme, we want
            # to create a distribution over the gold, proportional to the scores
            # awarded.
            self.g_probs = [x-y for x, y in zip(g_probs_all, g_probs)]


def _softmax(nums):
    if not nums:
        return []
    max_ = max(nums)
    nums = [(exp(n-max_) if n is not None else None) for n in nums]
    Z = sum(n for n in nums if n is not None)
    return [(n/Z if n is not None else None) for n in nums]
