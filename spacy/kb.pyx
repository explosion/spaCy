# cython: profile=True
# coding: utf8
from spacy.errors import user_warning


cdef class Entity:

    def __init__(self, KnowledgeBase kb, entity_id_hash, confidence):
        self.kb = kb
        self.entity_id_hash = entity_id_hash
        self.confidence = confidence

    property kb_id_:
        """RETURNS (unicode): ID of this entity in the KB"""
        def __get__(self):
            return self.kb.strings[self.entity_id_hash]

    property kb_id:
        """RETURNS (uint64): hash of the entity's KB ID"""
        def __get__(self):
            return self.entity_id_hash

    property confidence:
        def __get__(self):
            return self.confidence


cdef class Candidate:

    def __init__(self, KnowledgeBase kb, entity_id_hash, alias_hash, prior_prob):
        self.kb = kb
        self.entity_id_hash = entity_id_hash
        self.alias_hash = alias_hash
        self.prior_prob = prior_prob

    property entity_id:
        """RETURNS (uint64): hash of the entity's KB ID"""
        def __get__(self):
            return self.entity_id_hash

    property entity_id_:
        """RETURNS (unicode): ID of this entity in the KB"""
        def __get__(self):
            return self.kb.strings[self.entity_id]

    property entity_name:
        """RETURNS (uint64): hash of the entity's KB name"""
        def __get__(self):
            entry_index = <int64_t>self.kb._entry_index.get(self.entity_id)
            return self.kb._entries[entry_index].entity_name_hash

    property entity_name_:
        """RETURNS (unicode): name of this entity in the KB"""
        def __get__(self):
            return self.kb.strings[self.entity_name]

    property alias:
        """RETURNS (uint64): hash of the alias"""
        def __get__(self):
            return self.alias_hash

    property alias_:
        """RETURNS (unicode): ID of the original alias"""
        def __get__(self):
            return self.kb.strings[self.alias]

    property prior_prob:
        def __get__(self):
            return self.prior_prob


cdef class KnowledgeBase:

    def __init__(self):
        self._entry_index = PreshMap()
        self._alias_index = PreshMap()
        self.mem = Pool()
        self.strings = StringStore()
        self._create_empty_vectors()

    def __len__(self):
        return self.get_size_entities()

    def get_size_entities(self):
        return self._entries.size() - 1  # not counting dummy element on index 0

    def get_size_aliases(self):
        return self._aliases_table.size() - 1 # not counting dummy element on index 0

    def add_entity(self, unicode entity_id, unicode entity_name=None, float prob=0.5, vectors=None, features=None):
        """
        Add an entity to the KB.
        Return the hash of the entity ID at the end
        """
        if not entity_name:
            entity_name = entity_id
        cdef hash_t id_hash = self.strings.add(entity_id)
        cdef hash_t name_hash = self.strings.add(entity_name)

        # Return if this entity was added before
        if id_hash in self._entry_index:
            user_warning("Entity " + entity_id + " already exists in the KB")
            return

        cdef int32_t dummy_value = 342
        self.c_add_entity(entity_id_hash=id_hash, entity_name_hash=name_hash, prob=prob, vector_rows=&dummy_value, feats_row=dummy_value)
        # TODO self._vectors_table.get_pointer(vectors),
        # self._features_table.get(features))

        return id_hash

    def add_alias(self, unicode alias, entities, probabilities):
        """
        For a given alias, add its potential entities and prior probabilies to the KB.
        Return the alias_hash at the end
        """

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
            entity_id_hash = self.strings[entity]
            if not entity_id_hash in self._entry_index:
                raise ValueError("Alias '" + alias + "' defined for unknown entity '" + entity + "'")

            entry_index = <int64_t>self._entry_index.get(entity_id_hash)
            entry_indices.push_back(int(entry_index))
            probs.push_back(float(prob))

        self.c_add_aliases(alias_hash=alias_hash, entry_indices=entry_indices, probs=probs)

        return alias_hash


    def get_candidates(self, unicode alias):
        cdef hash_t alias_hash = self.strings[alias]
        alias_index = <int64_t>self._alias_index.get(alias_hash)
        alias_entry = self._aliases_table[alias_index]

        return [Candidate(kb=self,
                          entity_id_hash=self._entries[entry_index].entity_id_hash,
                          alias_hash=alias_hash,
                          prior_prob=prob)
                for (entry_index, prob) in zip(alias_entry.entry_indices, alias_entry.probs)
                if entry_index != 0]
