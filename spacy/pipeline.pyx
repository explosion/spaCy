from .syntax.parser cimport Parser
from .syntax.ner cimport BiluoPushDown
from .syntax.arc_eager cimport ArcEager
from .vocab cimport Vocab
from .tagger import Tagger

# TODO: The disorganization here is pretty embarrassing. At least it's only
# internals.
from .syntax.parser import get_templates as get_feature_templates
from .attrs import DEP, ENT_TYPE


cdef class EntityRecognizer(Parser):
    """Annotate named entities on Doc objects."""
    TransitionSystem = BiluoPushDown
    
    feature_templates = get_feature_templates('ner')

    def add_label(self, label):
        for action in self.moves.action_types:
            self.moves.add_action(action, label)
        if isinstance(label, basestring):
            label = self.vocab.strings[label]
        for attr, freqs in self.vocab.serializer_freqs:
            if attr == ENT_TYPE and label not in freqs:
                freqs.append([label, 1])
        # Super hacky :(
        self.vocab._serializer = None


cdef class DependencyParser(Parser):
    TransitionSystem = ArcEager

    feature_templates = get_feature_templates('basic')

    def add_label(self, label):
        for action in self.moves.action_types:
            self.moves.add_action(action, label)
        if isinstance(label, basestring):
            label = self.vocab.strings[label]
        for attr, freqs in self.vocab.serializer_freqs:
            if attr == DEP and label not in freqs:
                freqs.append([label, 1])
        # Super hacky :(
        self.vocab._serializer = None


__all__ = [Tagger, DependencyParser, EntityRecognizer]
