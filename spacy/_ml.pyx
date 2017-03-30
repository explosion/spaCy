# cython: infer_types=True
# cython: profile=True
# cython: cdivision=True

from libcpp.vector cimport vector
from libc.stdint cimport uint64_t, uint32_t, int32_t
from libc.string cimport memcpy, memset
cimport libcpp.algorithm
from libc.math cimport exp

from cymem.cymem cimport Pool
from thinc.linalg cimport Vec, VecVec
from murmurhash.mrmr cimport hash64
cimport numpy as np
import numpy
np.import_array()

from thinc.neural.optimizers import Adam
from thinc.neural.ops import NumpyOps


cdef class LinearModel:
    def __init__(self, int nr_class, templates,
            weight_t momentum=0.9, weight_t learn_rate=0.001, size=2**18):
        self.extracter = ConjunctionExtracter(templates)
        self.nr_weight = size
        self.nr_class = nr_class
        self.learn_rate = learn_rate
        self.momentum = momentum
        self.mem = Pool()
        self.time = 0
        self.W = <weight_t*>self.mem.alloc(self.nr_weight * self.nr_class,
                                           sizeof(weight_t))
        self.mom = <weight_t*>self.mem.alloc(self.nr_weight * self.nr_class,
                                           sizeof(weight_t))
        self.averages = <weight_t*>self.mem.alloc(self.nr_weight * self.nr_class,
                                           sizeof(weight_t))
        self.last_upd = <weight_t*>self.mem.alloc(self.nr_weight * self.nr_class,
                                           sizeof(weight_t))

    cdef void hinge_lossC(self, weight_t* d_scores,
            const weight_t* scores, const weight_t* costs) nogil:
        guess = 0
        best = -1
        for i in range(1, self.nr_class):
            if scores[i] > scores[guess]:
                guess = i
            if costs[i] == 0 and (best == -1 or scores[i] > scores[best]):
                best = i
        if best != -1 and scores[guess] >= scores[best]:
            d_scores[guess] = 1.
            d_scores[best] = -1.

    cdef void log_lossC(self, weight_t* d_scores,
            const weight_t* scores, const weight_t* costs) nogil:
        for i in range(self.nr_class):
            if costs[i] <= 0:
                break
        else:
            return
        cdef double Z = 1e-10
        cdef double gZ = 1e-10
        cdef double max_ = scores[0]
        cdef double g_max = -9000
        for i in range(self.nr_class):
            max_ = max(max_, scores[i])
            if costs[i] <= 0:
                g_max = max(g_max, scores[i])
        for i in range(self.nr_class):
            Z += exp(scores[i]-max_)
            if costs[i] <= 0:
                gZ += exp(scores[i]-g_max)
        for i in range(self.nr_class):
            score = exp(scores[i]-max_)
            if costs[i] >= 1:
                d_scores[i] = score / Z
            else:
                g_score = exp(scores[i]-g_max)
                d_scores[i] = (score / Z) - (g_score / gZ)

    cdef void regression_lossC(self, weight_t* d_scores,
            const weight_t* scores, const weight_t* costs) nogil:
        best = -1
        for i in range(self.nr_class):
            if costs[i] <= 0:
                if best == -1:
                    best = i
                elif scores[i] > scores[best]:
                    best = i
        if best == -1:
            return
        for i in range(self.nr_class):
            if scores[i] < scores[best]:
                d_scores[i] = 0
            elif costs[i] <= 0 and scores[i] == best:
                continue
            else:
                d_scores[i] = scores[i] - -costs[i]

    cdef void set_scoresC(self, weight_t* scores,
            const FeatureC* features, int nr_feat) nogil:
        cdef int nr_class = self.nr_class
        cdef uint64_t nr_weight = self.nr_weight * nr_class - nr_class
        cdef vector[uint64_t] indices
        # Collect all feature indices
        cdef uint32_t[2] hashed
        cdef FeatureC feat
        cdef uint64_t hash2
        for feat in features[:nr_feat]:
            if feat.value == 0:
                continue
            memcpy(hashed, &feat.key, sizeof(hashed))
            indices.push_back(hashed[0] % nr_weight)
            indices.push_back(hashed[1] % nr_weight)

        # Sort them, to improve memory access pattern
        libcpp.algorithm.sort(indices.begin(), indices.end())
        for idx in indices:
            W = &self.W[idx]
            for clas in range(nr_class):
                scores[clas] += W[clas]

    cdef void set_gradientC(self, const weight_t* d_scores, const FeatureC*
            features, int nr_feat) nogil:
        self.time += 1
        cdef int nr_class = self.nr_class
        cdef weight_t abs_grad = 0
        for i in range(nr_class):
            abs_grad += d_scores[i] if d_scores[i] > 0 else -d_scores[i]
        if abs_grad < 0.1:
            return
        cdef uint64_t nr_weight = self.nr_weight * nr_class - nr_class
        cdef vector[uint64_t] indices
        # Collect all feature indices
        indices.reserve(nr_feat * 2)
        cdef uint32_t[2] hashed
        cdef uint64_t hash2
        for feat in features[:nr_feat]:
            if feat.value == 0:
                continue
            memcpy(hashed, &feat.key, sizeof(hashed))
            indices.push_back(hashed[0] % nr_weight)
            indices.push_back(hashed[1] % nr_weight)

        # Sort them, to improve memory access pattern
        libcpp.algorithm.sort(indices.begin(), indices.end())
        for idx in indices:
            #avg = &self.averages[idx]
            #last_upd = &self.last_upd[idx]
            W = &self.W[idx]
            #mom = &self.mom[idx]
            for i in range(nr_class):
                if d_scores[i] == 0:
                    continue
                d = d_scores[i]
                W[i] -= self.learn_rate * d
                #unchanged = self.time - last_upd[i]
                #avg[i] += unchanged * W[i]
                #mom[i] *= self.momentum ** unchanged
                #mom[i] += self.learn_rate * d
                #W[i] -= mom[i]
                #last_upd[i] = self.time

    def finish_update(self, optimizer):
        pass

    @property
    def nr_active_feat(self):
        return self.nr_weight

    @property
    def nr_feat(self):
        return self.extracter.nr_templ

    def end_training(self, *args, **kwargs):
        # Average weights
        for i in range(self.nr_weight * self.nr_class):  
            unchanged = self.time - self.last_upd[i]
            self.averages[i] += self.W[i] * unchanged
            self.W[i], self.averages[i] = self.averages[i], self.W[i]
            self.W[i] /= self.time
            self.last_upd[i] = self.time

    def dump(self, *args, **kwargs):
        pass
