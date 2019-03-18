from .strings cimport hash_string


cdef class KnowledgeBase:
    def __len__(self):
        return self._entries.size()

    def add_entity(self, entity_id: str, float prob, vectors=None, features=None):
        # TODO: more friendly check for non-unique name
        if entity_id in self:
            return

        cdef hash_t id_hash = hash_string(entity_id)
        cdef int32_t dummy_value = 342
        self.c_add_entity(entity_key=id_hash, prob=prob, vector_rows=&dummy_value, feats_row=dummy_value)
        # TODO self._vectors_table.get_pointer(vectors),
        # self._features_table.get(features))

    def add_alias(self, alias, entities, probabilities):
        """For a given alias, add its potential entities and prior probabilies to the KB."""
        cdef hash_t alias_hash = hash_string(alias)
        cdef hash_t entity_hash = 0
        cdef int64_t entity_index = 0

        cdef vector[int64_t] entry_indices = [self._entry_index[hash_string(entity)] for entity in entities]

        self.c_add_aliases(alias_key=alias_hash, entry_indices=entry_indices, probs=probabilities)

        # TODO: check that alias hadn't been defined before
        # TODO: check that entity is already in this KB (entity_index is OK)
        # TODO: check sum(probabilities) <= 1
        # TODO: check len(entities) == len(probabilities)


