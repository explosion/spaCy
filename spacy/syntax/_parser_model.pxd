from libc.string cimport memset, memcpy
from libc.stdlib cimport calloc, free, realloc
from thinc.typedefs cimport weight_t, class_t, hash_t

from ._state cimport StateC


cdef struct SizesC:
    int states
    int classes
    int hiddens
    int pieces
    int feats
    int embed_width


cdef struct WeightsC:
    float* feat_weights
    float* feat_bias
    float* hidden_bias
    float* hidden_weights
    float* vectors


cdef struct ActivationsC:
    int* token_ids
    float* vectors
    float* unmaxed
    float* scores
    float* hiddens
    int* is_valid
    int _curr_size
    int _max_size


cdef WeightsC get_c_weights(model)

cdef void resize_activations(ActivationsC* A, SizesC n) nogil

cdef void predict_states(ActivationsC* A, StateC** states,
        const WeightsC* W, SizesC n) nogil
 
cdef int arg_max_if_valid(const weight_t* scores, const int* is_valid, int n) nogil

cdef void cpu_log_loss(float* d_scores,
        const float* costs, const int* is_valid, const float* scores, int O) nogil
 
