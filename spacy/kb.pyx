# cython: profile=True
# coding: utf8
from preshed.maps import PreshMap


cdef class KnowledgeBase:

    def __init__(self):
        self._entry_index = PreshMap()
        self._alias_index = PreshMap()
        self.mem = Pool()


    def __len__(self):
        return self._entries.size()

    def add_entity(self, unicode entity_id, float prob, vectors=None, features=None):
        cdef hash_t id_hash = hash_string(entity_id)

        # TODO: more friendly check for non-unique name
        if id_hash in self._entry_index:
            return


        cdef int32_t dummy_value = 342
        self.c_add_entity(entity_key=id_hash, prob=prob, vector_rows=&dummy_value, feats_row=dummy_value)
        # TODO self._vectors_table.get_pointer(vectors),
        # self._features_table.get(features))

    def add_alias(self, unicode alias, entities, probabilities):
        """For a given alias, add its potential entities and prior probabilies to the KB."""
        cdef hash_t alias_hash = hash_string(alias)

        # TODO: check that alias hadn't been defined before
        # TODO: check that entity is already in this KB (entity_index is OK)
        # TODO: check sum(probabilities) <= 1
        # TODO: check len(entities) == len(probabilities)

        self.c_add_aliases(alias_key=alias_hash, entities=entities, probabilities=probabilities)



