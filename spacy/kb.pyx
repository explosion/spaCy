# cython: profile=True
# coding: utf8
from spacy.errors import Errors, Warnings, user_warning


cdef class Candidate:

    def __init__(self, KnowledgeBase kb, entity_hash, alias_hash, prior_prob):
        self.kb = kb
        self.entity_hash = entity_hash
        self.alias_hash = alias_hash
        self.prior_prob = prior_prob

    @property
    def entity(self):
        """RETURNS (uint64): hash of the entity's KB ID/name"""
        return self.entity_hash

    @property
    def entity_(self):
        """RETURNS (unicode): ID/name of this entity in the KB"""
        return self.kb.vocab.strings[self.entity]

    @property
    def alias(self):
        """RETURNS (uint64): hash of the alias"""
        return self.alias_hash

    @property
    def alias_(self):
        """RETURNS (unicode): ID of the original alias"""
        return self.kb.vocab.strings[self.alias]

    @property
    def prior_prob(self):
        return self.prior_prob


cdef class KnowledgeBase:

    def __init__(self, Vocab vocab):
        self.vocab = vocab
        self._entry_index = PreshMap()
        self._alias_index = PreshMap()
        self.mem = Pool()
        self._create_empty_vectors()

    def __len__(self):
        return self.get_size_entities()

    def get_size_entities(self):
        return self._entries.size() - 1  # not counting dummy element on index 0

    def get_size_aliases(self):
        return self._aliases_table.size() - 1 # not counting dummy element on index 0

    def add_entity(self, unicode entity, float prob=0.5, vectors=None, features=None):
        """
        Add an entity to the KB.
        Return the hash of the entity ID at the end
        """
        cdef hash_t entity_hash = self.vocab.strings.add(entity)

        # Return if this entity was added before
        if entity_hash in self._entry_index:
            user_warning(Warnings.W018.format(entity=entity))
            return

        cdef int32_t dummy_value = 342
        self.c_add_entity(entity_hash=entity_hash, prob=prob,
                          vector_rows=&dummy_value, feats_row=dummy_value)
        # TODO self._vectors_table.get_pointer(vectors),
        # self._features_table.get(features))

        return entity_hash

    def add_alias(self, unicode alias, entities, probabilities):
        """
        For a given alias, add its potential entities and prior probabilies to the KB.
        Return the alias_hash at the end
        """

        # Throw an error if the length of entities and probabilities are not the same
        if not len(entities) == len(probabilities):
            raise ValueError(Errors.E132.format(alias=alias,
                                                entities_length=len(entities),
                                                probabilities_length=len(probabilities)))

        # Throw an error if the probabilities sum up to more than 1
        prob_sum = sum(probabilities)
        if prob_sum > 1:
            raise ValueError(Errors.E133.format(alias=alias, sum=prob_sum))

        cdef hash_t alias_hash = self.vocab.strings.add(alias)

        # Return if this alias was added before
        if alias_hash in self._alias_index:
            user_warning(Warnings.W017.format(alias=alias))
            return

        cdef hash_t entity_hash

        cdef vector[int64_t] entry_indices
        cdef vector[float] probs

        for entity, prob in zip(entities, probabilities):
            entity_hash = self.vocab.strings[entity]
            if not entity_hash in self._entry_index:
                raise ValueError(Errors.E134.format(alias=alias, entity=entity))

            entry_index = <int64_t>self._entry_index.get(entity_hash)
            entry_indices.push_back(int(entry_index))
            probs.push_back(float(prob))

        self.c_add_aliases(alias_hash=alias_hash, entry_indices=entry_indices, probs=probs)

        return alias_hash


    def get_candidates(self, unicode alias):
        """ TODO: where to put this functionality ?"""
        cdef hash_t alias_hash = self.vocab.strings[alias]
        alias_index = <int64_t>self._alias_index.get(alias_hash)
        alias_entry = self._aliases_table[alias_index]

        return [Candidate(kb=self,
                          entity_hash=self._entries[entry_index].entity_hash,
                          alias_hash=alias_hash,
                          prior_prob=prob)
                for (entry_index, prob) in zip(alias_entry.entry_indices, alias_entry.probs)
                if entry_index != 0]
