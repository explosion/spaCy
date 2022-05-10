from typing import List

from libc.stdint cimport int8_t
cimport numpy as np
from thinc.api import Model

from spacy.pipeline._parser_internals.stateclass import StateClass
from spacy.pipeline._parser_internals.transition_system cimport TransitionSystem
from spacy.typedefs cimport weight_t, hash_t
from spacy.pipeline._parser_internals._state cimport StateC


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
