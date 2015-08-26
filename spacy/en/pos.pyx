from os import path

from ..parts_of_speech cimport NOUN, VERB, ADJ

from ..lemmatizer import Lemmatizer


cdef class EnPosTagger(Tagger):
    """A part-of-speech tagger for English"""
    def make_lemmatizer(self, data_dir):
        return Lemmatizer(path.join(data_dir, 'wordnet'), NOUN, VERB, ADJ)
