"""Knowledge-base for entity or concept linking."""
from cymem.cymem cimport Pool
from preshed.maps cimport PreshMap
from libcpp.vector cimport vector
from libc.stdint cimport int32_t, int64_t
from .typedefs cimport hash_t
from .strings cimport hash_string


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


# Each alias struct stores a list of Entry pointers with their prior probabilities
# for this specific mention/alias.
cdef struct _AliasC:

    # All entry candidates for this alias
    vector[int64_t] entry_indices

    # Prior probability P(entity|alias) - should sum up to (at most) 1.
    vector[float] probs


cdef class KnowledgeBase:
    cdef Pool mem

    # This maps 64bit keys (hash of unique entity string)
    # to 64bit values (position of the _EntryC struct in the _entries vector).
    # The PreshMap is pretty space efficient, as it uses open addressing. So
    # the only overhead is the vacancy rate, which is approximately 30%.
    cdef PreshMap _entry_index

    # Each entry takes 128 bits, and again we'll have a 30% or so overhead for
    # over allocation.
    # In total we end up with (N*128*1.3)+(N*128*1.3) bits for N entries.
    # Storing 1m entries would take 41.6mb under this scheme.
    cdef vector[_EntryC] _entries

    # This maps 64bit keys (hash of unique alias string)
    # to 64bit values (position of the _AliasC struct in the _aliases_table vector).
    cdef PreshMap _alias_index

    # This should map mention hashes to (entry_id, prob) tuples. The probability
    # should be P(entity | mention), which is pretty important to know.
    # We can pack both pieces of information into a 64-bit value, to keep things
    # efficient.
    cdef vector[_AliasC] _aliases_table

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


    cdef inline int64_t c_add_entity(self, hash_t entity_key, float prob, const int32_t* vector_rows,
                    int feats_row):
        """Add an entry to the knowledge base."""
        # This is what we'll map the hash key to. It's where the entry will sit
        # in the vector of entries, so we can get it later.
        cdef int64_t entity_index = self._entries.size()
        self._entries.push_back(
            _EntryC(
                vector_rows=vector_rows,
                feats_row=feats_row,
                prob=prob
            ))
        self._entry_index[entity_key] = entity_index
        return entity_index

    cdef inline int64_t c_add_aliases(self, hash_t alias_key, entities, probabilities):
        """Connect a mention to a list of potential entities with their prior probabilities ."""
        cdef int64_t alias_index = self._aliases_table.size()

        cdef vector[int64_t] entry_indices
        cdef vector[float] probs

        for entity, prob in zip(entities, probs):
            entry_index = self._entry_index[hash_string(entity)]
            entry_indices.push_back(entry_index)
            probs.push_back(prob)

        self._aliases_table.push_back(
            _AliasC(
                entry_indices=entry_indices,
                probs=probs
            ))
        self._alias_index[alias_key] = alias_index
        return alias_index


