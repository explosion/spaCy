"""Knowledge-base for entity or concept linking."""
from cymem.cymem cimport Pool
from preshed.maps cimport PreshMap
from libcpp.vector cimport vector
from libc.stdint cimport int32_t, int64_t
from .typedefs cimport hash_t


# Internal struct, for storage and disambiguation. This isn't what we return
# to the user as the answer to "here's your entity". It's the minimum number
# of bits we need to keep track of the answers.
cdef struct _EntryC:

    # Allows retrieval of one or more vectors.
    # Each element of vector_rows should be an index into a vectors table.
    # Every entry should have the same number of vectors, so we can avoid storing
    # the number of vectors in each knowledge-base struct
    const int32_t* vector_rows

    # Allows retrieval of a struct of non-vector features. We could make this a
    # pointer, but we have 32 bits left over in the struct after prob, so we'd
    # like this to only be 32 bits. We can also set this to -1, for the common
    # case where there are no features.
    int32_t feats_row

    # log probability of entity, based on corpus frequency
    float prob


cdef class KnowledgeBase:
    cdef Pool mem

    # This maps 64bit keys to 64bit values. Here the key would be a hash of
    # a unique string name for the entity, and the value would be the position
    # of the _EntryC struct in our vector.
    # The PreshMap is pretty space efficient, as it uses open addressing. So
    # the only overhead is the vacancy rate, which is approximately 30%.
    cdef PreshMap _index

    # Each entry takes 128 bits, and again we'll have a 30% or so overhead for
    # over allocation.
    # In total we end up with (N*128*1.3)+(N*128*1.3) bits for N entries.
    # Storing 1m entries would take 41.6mb under this scheme.
    cdef vector[_EntryC] _entries

    # This is the part which might take more space: storing various
    # categorical features for the entries, and storing vectors for disambiguation
    # and possibly usage.
    # If each entry gets a 300-dimensional vector, for 1m entries we would need
    # 1.2gb. That gets expensive fast. What might be better is to avoid learning
    # a unique vector for every entity. We could instead have a compositional
    # model, that embeds different features of the entities into vectors. We'll
    # still want some per-entity features, like the Wikipedia text or entity
    # co-occurrence. Hopefully those vectors can be narrow, e.g. 64 dimensions.
    cdef object _vectors_table

    # It's very useful to track categorical features, at least for output, even
    # if they're not useful in the model itself. For instance, we should be
    # able to track stuff like a person's date of birth or whatever. This can
    # easily make the KB bigger, but if this isn't needed by the model, and it's
    # optional data, we can let users configure a DB as the backend for this.
    cdef object _features_table

    # This should map mention hashes to (entry_id, prob) tuples. The probability
    # should be P(entity | mention), which is pretty important to know.
    # We can pack both pieces of information into a 64-bit value, to keep things
    # efficient.
    cdef object _aliases_table

    cdef void c_add_entity(self, hash_t key, float prob, const int32_t* vector_rows,
                    int feats_row) nogil:
        """Add an entry to the knowledge base."""
        # This is what we'll map the hash key to. It's where the entry will sit
        # in the vector of entries, so we can get it later.
        cdef int64_t index = self._entries.size()
        self._entries.push_back(
            _EntryC(
                vector_rows=vector_rows,
                feats_row=feats_row,
                prob=prob
            ))
        self._index[key] = index
        return index