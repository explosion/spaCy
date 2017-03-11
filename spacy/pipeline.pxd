from .syntax.parser cimport Parser
from .syntax.beam_parser cimport BeamParser
from .syntax.ner cimport BiluoPushDown
from .syntax.arc_eager cimport ArcEager
from .tagger cimport Tagger


cdef class EntityRecognizer(Parser):
    pass


cdef class DependencyParser(Parser):
    pass


cdef class BeamEntityRecognizer(BeamParser):
    pass


cdef class BeamDependencyParser(BeamParser):
    pass
