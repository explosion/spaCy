"""Knowledge-base for entity or concept linking."""
from cymem.cymem cimport Pool
from preshed.maps cimport PreshMap

from libcpp.vector cimport vector
from libc.stdint cimport int32_t, int64_t
from libc.stdio cimport FILE

from spacy.vocab cimport Vocab
from .typedefs cimport hash_t

from .structs cimport KBEntryC, AliasC
ctypedef vector[KBEntryC] entry_vec
ctypedef vector[AliasC] alias_vec
ctypedef vector[float] float_vec
ctypedef vector[float_vec] float_matrix


# Object used by the Entity Linker that summarizes one entity-alias candidate combination.
cdef class Candidate:
    cdef readonly KnowledgeBase kb
    cdef hash_t entity_hash
    cdef float entity_freq
    cdef vector[float] entity_vector
    cdef hash_t alias_hash
    cdef float prior_prob


cdef class KnowledgeBase:
    cdef Pool mem
    cpdef readonly Vocab vocab
    cdef int64_t entity_vector_length

    # This maps 64bit keys (hash of unique entity string)
    # to 64bit values (position of the _KBEntryC struct in the _entries vector).
    # The PreshMap is pretty space efficient, as it uses open addressing. So
    # the only overhead is the vacancy rate, which is approximately 30%.
    cdef PreshMap _entry_index

    # Each entry takes 128 bits, and again we'll have a 30% or so overhead for
    # over allocation.
    # In total we end up with (N*128*1.3)+(N*128*1.3) bits for N entries.
    # Storing 1m entries would take 41.6mb under this scheme.
    cdef entry_vec _entries

    # This maps 64bit keys (hash of unique alias string)
    # to 64bit values (position of the _AliasC struct in the _aliases_table vector).
    cdef PreshMap _alias_index

    # This should map mention hashes to (entry_id, prob) tuples. The probability
    # should be P(entity | mention), which is pretty important to know.
    # We can pack both pieces of information into a 64-bit value, to keep things
    # efficient.
    cdef alias_vec _aliases_table

    # This is the part which might take more space: storing various
    # categorical features for the entries, and storing vectors for disambiguation
    # and possibly usage.
    # If each entry gets a 300-dimensional vector, for 1m entries we would need
    # 1.2gb. That gets expensive fast. What might be better is to avoid learning
    # a unique vector for every entity. We could instead have a compositional
    # model, that embeds different features of the entities into vectors. We'll
    # still want some per-entity features, like the Wikipedia text or entity
    # co-occurrence. Hopefully those vectors can be narrow, e.g. 64 dimensions.
    cdef float_matrix _vectors_table

    # It's very useful to track categorical features, at least for output, even
    # if they're not useful in the model itself. For instance, we should be
    # able to track stuff like a person's date of birth or whatever. This can
    # easily make the KB bigger, but if this isn't needed by the model, and it's
    # optional data, we can let users configure a DB as the backend for this.
    cdef object _features_table


    cdef inline int64_t c_add_vector(self, vector[float] entity_vector) nogil:
        """Add an entity vector to the vectors table."""
        cdef int64_t new_index = self._vectors_table.size()
        self._vectors_table.push_back(entity_vector)
        return new_index


    cdef inline int64_t c_add_entity(self, hash_t entity_hash, float prob,
                                     int32_t vector_index, int feats_row) nogil:
        """Add an entry to the vector of entries.
        After calling this method, make sure to update also the _entry_index using the return value"""
        # This is what we'll map the entity hash key to. It's where the entry will sit
        # in the vector of entries, so we can get it later.
        cdef int64_t new_index = self._entries.size()

        # Avoid struct initializer to enable nogil, cf https://github.com/cython/cython/issues/1642
        cdef KBEntryC entry
        entry.entity_hash = entity_hash
        entry.vector_index = vector_index
        entry.feats_row = feats_row
        entry.prob = prob

        self._entries.push_back(entry)
        return new_index

    cdef inline int64_t c_add_aliases(self, hash_t alias_hash, vector[int64_t] entry_indices, vector[float] probs) nogil:
        """Connect a mention to a list of potential entities with their prior probabilities .
        After calling this method, make sure to update also the _alias_index using the return value"""
        # This is what we'll map the alias hash key to. It's where the alias will be defined
        # in the vector of aliases.
        cdef int64_t new_index = self._aliases_table.size()

        # Avoid struct initializer to enable nogil
        cdef AliasC alias
        alias.entry_indices = entry_indices
        alias.probs = probs

        self._aliases_table.push_back(alias)
        return new_index

    cdef inline void _create_empty_vectors(self, hash_t dummy_hash) nogil:
        """ 
        Initializing the vectors and making sure the first element of each vector is a dummy,
        because the PreshMap maps pointing to indices in these vectors can not contain 0 as value
        cf. https://github.com/explosion/preshed/issues/17
        """
        cdef int32_t dummy_value = 0

        # Avoid struct initializer to enable nogil
        cdef KBEntryC entry
        entry.entity_hash = dummy_hash
        entry.vector_index = dummy_value
        entry.feats_row = dummy_value
        entry.prob = dummy_value

        # Avoid struct initializer to enable nogil
        cdef vector[int64_t] dummy_entry_indices
        dummy_entry_indices.push_back(0)
        cdef vector[float] dummy_probs
        dummy_probs.push_back(0)

        cdef AliasC alias
        alias.entry_indices = dummy_entry_indices
        alias.probs = dummy_probs

        self._entries.push_back(entry)
        self._aliases_table.push_back(alias)

    cpdef load_bulk(self, loc)
    cpdef set_entities(self, entity_list, prob_list, vector_list)


cdef class Writer:
    cdef FILE* _fp

    cdef int write_header(self, int64_t nr_entries, int64_t entity_vector_length) except -1
    cdef int write_vector_element(self, float element) except -1
    cdef int write_entry(self, hash_t entry_hash, float entry_prob, int32_t vector_index) except -1

    cdef int write_alias_length(self, int64_t alias_length) except -1
    cdef int write_alias_header(self, hash_t alias_hash, int64_t candidate_length) except -1
    cdef int write_alias(self, int64_t entry_index, float prob) except -1

    cdef int _write(self, void* value, size_t size) except -1

cdef class Reader:
    cdef FILE* _fp

    cdef int read_header(self, int64_t* nr_entries, int64_t* entity_vector_length) except -1
    cdef int read_vector_element(self, float* element) except -1
    cdef int read_entry(self, hash_t* entity_hash, float* prob, int32_t* vector_index) except -1

    cdef int read_alias_length(self, int64_t* alias_length) except -1
    cdef int read_alias_header(self, hash_t* alias_hash, int64_t* candidate_length) except -1
    cdef int read_alias(self, int64_t* entry_index, float* prob) except -1

    cdef int _read(self, void* value, size_t size) except -1

