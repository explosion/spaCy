from typing import List, Optional, Callable, Tuple
import numpy
from thinc.types import Ints2d
from thinc.api import Model, registry, get_current_ops
from ..symbols import NAMES as SYMBOLS_BY_INT

cimport numpy as np
from cymem.cymem cimport Pool
from libc.string cimport memset, strlen
from libc.stdint cimport uint64_t
from ..tokens.doc cimport Doc
from ..structs cimport TokenC
from ..typedefs cimport attr_t


@registry.layers("spacy.RichFeatureExtractor.v1")
def RichFeatureExtractor(
    *,
    case_sensitive: bool,
    pref_lengths: Optional[List[int]] = None,
    suff_lengths: Optional[List[int]] = None,
) -> Model[List[Doc], List[Ints2d]]:
    # Because the calling code guarantees that the integers in the list are each less than 256,
    # the integer list can be converted into *bytes*.
    return Model(
        "extract_character_combination_hashes",
        forward,
        attrs={
            "case_sensitive": case_sensitive,
            "p_lengths": bytes(pref_lengths) if pref_lengths is not None else bytes(),
            "s_lengths": bytes(suff_lengths) if suff_lengths is not None else bytes(),
        },
    )


def forward(
    model: Model[List[Doc], List[Ints2d]], docs, is_train: bool
) -> Tuple[List[Ints2d], Callable]:
    ops = model.ops
    case_sensitive: bool = model.attrs["case_sensitive"]
    p_lengths: bytes = model.attrs["p_lengths"]
    s_lengths: bytes = model.attrs["s_lengths"]
    features: List[Ints2d] = []
    for doc in docs:
        hashes = get_character_combination_hashes(
            doc=doc,
            case_sensitive=case_sensitive,
            p_lengths=p_lengths,
            s_lengths=s_lengths,
        )
        features.append(ops.asarray2i(hashes, dtype="uint64"))

    backprop: Callable[[List[Ints2d]], List] = lambda d_features: []
    return features, backprop


def get_character_combination_hashes(
    *,
    Doc doc,
    const bint case_sensitive, 
    const unsigned char* p_lengths,
    const unsigned char* s_lengths,
):
    """
    Returns a 2D NumPy array where the rows represent tokens and the columns represent hashes of various character combinations 
        derived from the raw text of each token.

    doc: the document
    case_sensitive: if *False*, hashes are generated based on the lower-case version of each token.
    p_lengths: an array of single-byte values specifying the lengths of prefixes to be hashed in ascending order. 
        For example, if *p_lengths==[2, 3]*, the prefixes hashed for "spaCy" would be "sp" and "spa".
    s_lengths: an array of single-byte values specifying the lengths of suffixes to be hashed in ascending order. 
        For example, if *s_lengths==[2, 3]* and *cs == True*, the suffixes hashed for "spaCy" would be "yC" and "yCa".

    Many of the buffers passed into and used by this method contain single-byte numerical values. This takes advantage of 
    the fact that we are hashing short affixes and searching for small groups of characters. The calling code is responsible
    for ensuring that lengths being passed in cannot exceed 63 and hence, with maximally four-byte 
    character widths, that individual values within buffers can never exceed the capacity of a single byte (255).

    Note that this method performs no data validation itself as it expects the calling code will already have done so, and
    that the behaviour of the code may be erratic if the supplied parameters do not conform to expectations.
    """
    
    # Work out lengths
    cdef int p_lengths_l = strlen(<char*> p_lengths)
    cdef int s_lengths_l = strlen(<char*> s_lengths)
    cdef int p_max_l = p_lengths[p_lengths_l - 1] if p_lengths_l > 0 else 0
    cdef int s_max_l = s_lengths[s_lengths_l - 1] if s_lengths_l > 0 else 0
    
    # Define / allocate buffers
    cdef Pool mem = Pool()
    cdef unsigned char* pref_l_buf = <unsigned char*> mem.alloc(p_max_l, sizeof(char))
    cdef unsigned char* suff_l_buf = <unsigned char*> mem.alloc(s_max_l, sizeof(char))
    cdef int doc_l = doc.length
    cdef np.ndarray[np.uint64_t, ndim=2] hashes = numpy.empty(
        (doc_l, p_lengths_l + s_lengths_l), dtype="uint64")
    cdef np.uint64_t* hashes_ptr = <np.uint64_t*> hashes.data
        
    # Define working variables
    cdef TokenC tok_c
    cdef int tok_i, tok_str_l
    cdef attr_t num_tok_attr
    cdef bytes tok_str_bytes
    cdef const unsigned char* tok_str
    
    for tok_i in range(doc_l):
        tok_c = <TokenC> doc.c[tok_i]
        num_tok_attr = tok_c.lex.orth if case_sensitive else tok_c.lex.lower
        if num_tok_attr < len(SYMBOLS_BY_INT): # hardly ever happens
            if num_tok_attr == 0:
                tok_str_bytes = b""
            else:
                tok_str_bytes = SYMBOLS_BY_INT[num_tok_attr].encode("UTF-8")
            tok_str = tok_str_bytes
            tok_str_l = len(tok_str_bytes)
        else:
            tok_str, tok_str_l = doc.vocab.strings.utf8_ptr(num_tok_attr)

        if p_max_l > 0:
            _set_prefix_lengths(tok_str, tok_str_l, p_max_l, pref_l_buf)
            hashes_ptr += _write_hashes(tok_str, p_lengths, pref_l_buf, 0, hashes_ptr)

        if s_max_l > 0:
            _set_suffix_lengths(tok_str, tok_str_l, s_max_l, suff_l_buf)
            hashes_ptr += _write_hashes(tok_str, s_lengths, suff_l_buf, tok_str_l - 1, hashes_ptr)
                
    return hashes

cdef void _set_prefix_lengths(
    const unsigned char* tok_str,
    const int tok_str_l,
    const int p_max_l, 
    unsigned char* pref_l_buf,
) nogil:
    """ Populate *pref_l_buf*, which has length *p_max_l*, with the byte lengths of each of the substrings terminated by the first *p_max_l* 
        characters within *tok_str*. Lengths that are greater than the character length of the whole word are populated with the byte length 
        of the whole word.

        tok_str: a UTF-8 representation of a string.
        tok_str_l: the length of *tok_str*.
        p_max_l: the number of characters to process at the beginning of the word.
        pref_l_buf: a buffer of length *p_max_l* in which to store the lengths. The code calling *get_character_combination_hashes()* is 
        responsible for ensuring that *p_max_l* cannot exceed 63 and hence, with maximally four-byte character widths, that individual values 
        within the buffer can never exceed the capacity of a single byte (255).
    """
    cdef int tok_str_idx = 1, pref_l_buf_idx = 0

    while pref_l_buf_idx < p_max_l:
        if (tok_str_idx >= tok_str_l 
            or 
            ((tok_str[tok_str_idx] & 0xc0) != 0x80)  # not a continuation character
        ):
            pref_l_buf[pref_l_buf_idx] = tok_str_idx
            pref_l_buf_idx += 1
        if tok_str_idx >= tok_str_l:
            break
        tok_str_idx += 1

    if pref_l_buf_idx < p_max_l:
        memset(pref_l_buf + pref_l_buf_idx, pref_l_buf[pref_l_buf_idx - 1], p_max_l - pref_l_buf_idx)


cdef void _set_suffix_lengths(
    const unsigned char* tok_str,
    const int tok_str_l,
    const int s_max_l,
    unsigned char* suff_l_buf,
) nogil:
    """ Populate *suff_l_buf*, which has length *s_max_l*, with the byte lengths of each of the substrings started by the last *s_max_l* 
        characters within *tok_str*. Lengths that are greater than the character length of the whole word are populated with the byte length 
        of the whole word.

        tok_str: a UTF-8 representation of a string.
        tok_str_l: the length of *tok_str*.
        s_max_l: the number of characters to process at the end of the word.
        suff_l_buf: a buffer of length *s_max_l* in which to store the lengths. The code calling *get_character_combination_hashes()* is 
        responsible for ensuring that *s_max_l* cannot exceed 63 and hence, with maximally four-byte character widths, that individual values 
        within the buffer can never exceed the capacity of a single byte (255).
    """
    cdef int tok_str_idx = tok_str_l - 1, suff_l_buf_idx = 0

    while suff_l_buf_idx < s_max_l:
        if (tok_str[tok_str_idx] & 0xc0) != 0x80: # not a continuation character
            suff_l_buf[suff_l_buf_idx] = tok_str_l - tok_str_idx
            suff_l_buf_idx += 1
        tok_str_idx -= 1
        if tok_str_idx < 0:
            break

    if suff_l_buf_idx < s_max_l:
        memset(suff_l_buf + suff_l_buf_idx, suff_l_buf[suff_l_buf_idx - 1], s_max_l - suff_l_buf_idx)


cdef uint64_t FNV1A_OFFSET_BASIS = 0xcbf29ce484222325
cdef uint64_t FNV1A_PRIME = 0x00000100000001B3


cdef int _write_hashes(
    const unsigned char* res_buf,
    const unsigned char* aff_l_buf,
    const unsigned char* offset_buf,
    const int res_buf_last,
    np.uint64_t* hashes_ptr,
) nogil:    
    """ Write 64-bit FNV1A hashes for a token/rich property group combination.

    res_buf: the string from which to generate the hash values.
    aff_l_buf: one-byte lengths describing how many characters to hash.
    offset_buf: one-byte lengths specifying the byte offset of each character within *res_buf*.
    res_buf_last: if affixes should start at the end of *res_buf*, the offset of the last byte in
         *res_buf*; if affixes should start at the beginning of *res_buf*, *0*.
    hashes_ptr: a pointer starting from which the new hashes should be written.

    Returns: the number of hashes written.
    """

    cdef int last_offset = 0, hash_idx = 0, offset, aff_l
    cdef uint64_t hash_val = FNV1A_OFFSET_BASIS
    
    while True:
        aff_l = aff_l_buf[hash_idx]
        if aff_l == 0:
            return hash_idx     
        offset = offset_buf[aff_l - 1]
        while last_offset < offset:
            if res_buf_last > 0:
                hash_val ^= res_buf[res_buf_last - last_offset]
            else:
                hash_val ^= res_buf[last_offset]
            hash_val *= FNV1A_PRIME
            last_offset += 1
        hashes_ptr[hash_idx] = hash_val
        hash_idx += 1
