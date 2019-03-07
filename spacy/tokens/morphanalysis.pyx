cdef class Morphanalysis:
    """Control access to morphological features for a token."""
    def __init__(self, Vocab vocab, features=None):
        pass

    @classmethod
    def from_id(self, Vocab vocab, hash_t key):
        pass

    def __contains__(self, feature):
        pass

    def __iter__(self):
        pass

    def __len__(self):
        pass

    def __str__(self):
        pass

    def __repr__(self):
        pass

    def __hash__(self):
        pass

    @property
    def is_base_form(self):
        pass

    @property
    def pos(self):
        pass

    @property
    def pos_(self):
        pass

    @property
    def id(self):
        pass

    def get(self, name):
        pass

    def set(self, name, value):
        pass

    def add(self, feature):
        pass

    def remove(self, feature):
        pass

    def to_json(self):
        pass
