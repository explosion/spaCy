from libc.stdint cimport int8_t


cdef struct SizesC:
    int states
    int classes
    int hiddens
    int pieces
    int feats
    int embed_width
    int tokens


cdef struct WeightsC:
    const float* feat_weights
    const float* feat_bias
    const float* hidden_bias
    const float* hidden_weights
    const int8_t* seen_mask


cdef struct ActivationsC:
    int* token_ids
    float* unmaxed
    float* hiddens
    int* is_valid
    int _curr_size
    int _max_size
