from .syntax.parser cimport Parser
from .syntax.beam_parser cimport BeamParser
from .syntax.ner cimport BiluoPushDown
from .syntax.arc_eager cimport ArcEager
from .tagger cimport Tagger


cdef class EntityRecognizer(BeamParser):
    pass


cdef class DependencyParser(Parser):
    pass
