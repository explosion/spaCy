from libc.string cimport memset, memcpy
from ..typedefs cimport weight_t, hash_t
from ..pipeline._parser_internals._state cimport StateC


cdef struct SizesC:
    int states
    int classes
    int hiddens
    int pieces
    int feats
    int embed_width


cdef struct WeightsC:
    const float* feat_weights
    const float* feat_bias
    const float* hidden_bias
    const float* hidden_weights
    const float* seen_classes


cdef struct ActivationsC:
    int* token_ids
    float* unmaxed
    float* scores
    float* hiddens
    int* is_valid
    int _curr_size
    int _max_size


cdef WeightsC get_c_weights(model) except *

cdef SizesC get_c_sizes(model, int batch_size) except *

cdef ActivationsC alloc_activations(SizesC n) nogil

cdef void free_activations(const ActivationsC* A) nogil

cdef void predict_states(ActivationsC* A, StateC** states,
        const WeightsC* W, SizesC n) nogil
 
cdef int arg_max_if_valid(const weight_t* scores, const int* is_valid, int n) nogil

cdef void cpu_log_loss(float* d_scores,
        const float* costs, const int* is_valid, const float* scores, int O) nogil
 
