from .syntax.parser cimport Parser
from .syntax.ner cimport BiluoPushDown
from .syntax.arc_eager cimport ArcEager
from .vocab cimport Vocab
from .tagger import Tagger

# TODO: The disorganization here is pretty embarrassing. At least it's only
# internals.
from .syntax.parser import get_templates as get_feature_templates


cdef class EntityRecognizer(Parser):
    TransitionSystem = BiluoPushDown
    
    feature_templates = get_feature_templates('ner')


cdef class DependencyParser(Parser):
    TransitionSystem = ArcEager

    feature_templates = get_feature_templates('basic')
    

__all__ = [Tagger, DependencyParser, EntityRecognizer]
