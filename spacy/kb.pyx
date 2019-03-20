# cython: profile=True
# coding: utf8
from spacy.errors import user_warning


cdef class Candidate:


    # def inline __cinit__(self, _EntryC entity, hash_t alias_hash, float prior_prob):
    #     self.alias_hash = alias_hash
    #     self.entity = entity
    #     self.prior_prob = prior_prob

    @staticmethod
    cdef Candidate from_entry(_EntryC* entity, hash_t alias_hash, float prior_prob):
        """Factory function to create Candidate objects from entity entries."""
        # Call to __new__ bypasses __init__ constructor
        cdef Candidate candidate = Candidate.__new__(Candidate)
        candidate.entity = entity
        candidate.alias_hash = alias_hash
        candidate.prior_prob = prior_prob
        return candidate

    def __str__(self):
        return "alias=" + self.strings[self.alias_hash] + \
               " prior_prob=" + str(self.prior_prob)

    #" entry=" + self.strings[self.entity_hash] + \

    def __repr__(self):
        return self.__str__()


cdef class KnowledgeBase:

    def __init__(self):
        self._entry_index = PreshMap()
        self._alias_index = PreshMap()
        self.mem = Pool()
        self.strings = StringStore()
        self.create_empty_vectors()

    def __len__(self):
        return self.get_size_entities()

    def get_size_entities(self):
        return self._entries.size() - 1  # not counting dummy element on index 0

    def get_size_aliases(self):
        return self._aliases_table.size() - 1 # not counting dummy element on index 0

    def add_entity(self, unicode entity_id, float prob, vectors=None, features=None):
        cdef hash_t id_hash = self.strings.add(entity_id)

        # Return if this entity was added before
        if id_hash in self._entry_index:
            user_warning("Entity " + entity_id + " already exists in the KB")
            return

        cdef int32_t dummy_value = 342
        self.c_add_entity(entity_key=id_hash, prob=prob, vector_rows=&dummy_value, feats_row=dummy_value)
        # TODO self._vectors_table.get_pointer(vectors),
        # self._features_table.get(features))

    def add_alias(self, unicode alias, entities, probabilities):
        """For a given alias, add its potential entities and prior probabilies to the KB."""

        # Throw an error if the length of entities and probabilities are not the same
        if not len(entities) == len(probabilities):
            raise ValueError("The vectors for entities and probabilities for alias '" + alias
                             + "' should have equal length, but found "
                             + str(len(entities)) + " and " + str(len(probabilities)) + "respectively.")


        # Throw an error if the probabilities sum up to more than 1
        prob_sum = sum(probabilities)
        if prob_sum > 1:
            raise ValueError("The sum of prior probabilities for alias '" + alias + "' should not exceed 1, "
                             + "but found " + str(prob_sum))

        cdef hash_t alias_hash = self.strings.add(alias)

        # Return if this alias was added before
        if alias_hash in self._alias_index:
            user_warning("Alias " + alias + " already exists in the KB")
            return

        cdef hash_t entity_hash

        cdef vector[int64_t] entry_indices
        cdef vector[float] probs

        for entity, prob in zip(entities, probabilities):
            entity_hash = self.strings[entity]
            if not entity_hash in self._entry_index:
                raise ValueError("Alias '" + alias + "' defined for unknown entity '" + entity + "'")

            entry_index = <int64_t>self._entry_index.get(entity_hash)
            entry_indices.push_back(int(entry_index))
            probs.push_back(float(prob))

        self.c_add_aliases(alias_key=alias_hash, entry_indices=entry_indices, probs=probs)


    def get_candidates(self, unicode alias):
        cdef hash_t alias_hash = self.strings[alias]
        alias_index = <int64_t>self._alias_index.get(alias_hash)
        alias_entry = self._aliases_table[alias_index]

        for (entry_index, prob) in zip(alias_entry.entry_indices, alias_entry.probs):
            entity = <_EntryC>self._entries[entry_index]
            # candidate = Candidate(entity=entity, alias_hash=alias_hash, prior_prob=prob)
            candidate = Candidate.from_entry(entity=&entity, alias_hash=alias_hash, prior_prob=prob)
            print(candidate)

        # return [Candidate(entity=<_EntryC>self._entries[<int64_t>self._entry_index[entry_index]],
        #                  alias_hash=alias_hash,
        #                  prior_prob=prob)
        #        for (entry_index, prob) in zip(alias_entry.entry_indices, alias_entry.probs)]


