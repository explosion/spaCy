from .strings cimport hash_string


cdef class KnowledgeBase:
    def __len__(self):
        return self._entries.size()

    def add_entity(self, name, float prob, vectors=None, features=None, aliases=None):
        # TODO: more friendly check for non-unique name
        if name in self:
            return

        cdef hash_t name_hash = hash_string(name)
        self.c_add_entity(name_hash, prob, self._vectors_table.get_pointer(vectors),
                   self._features_table.get(features))

    def add_alias(self, alias, entities, probabilities):
        """For a given alias, add its potential entities and prior probabilies to the KB."""
        cdef hash_t alias_hash = hash_string(alias)

        # TODO: check len(entities) == len(probabilities)
        for entity, prob in zip(entities, probabilities):
            cdef hash_t entity_hash = hash_string(entity)
            cdef int64_t entity_index = self._index[entity_hash]
            # TODO: check that entity is already in this KB (entity_index is OK)
            self._aliases_table.add(alias_hash, entity_index, prob)

