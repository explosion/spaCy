from __future__ import unicode_literals
cimport cython
import json
from os import path
from collections import defaultdict
from libc.string cimport memset

from cymem.cymem cimport Pool
from thinc.typedefs cimport atom_t, weight_t
from thinc.extra.eg cimport Example
from thinc.structs cimport ExampleC
from thinc.linear.avgtron cimport AveragedPerceptron
from thinc.linalg cimport VecVec
from thinc.structs cimport FeatureC

from .typedefs cimport attr_t
from .tokens.doc cimport Doc
from .attrs cimport TAG
from .parts_of_speech cimport NO_TAG, ADJ, ADV, ADP, CONJ, DET, NOUN, NUM, PRON
from .parts_of_speech cimport VERB, X, PUNCT, EOL, SPACE

from .attrs cimport *

from .util import get_package

 
cpdef enum:
    P2_orth
    P2_cluster
    P2_shape
    P2_prefix
    P2_suffix
    P2_pos
    P2_lemma
    P2_flags

    P1_orth
    P1_cluster
    P1_shape
    P1_prefix
    P1_suffix
    P1_pos
    P1_lemma
    P1_flags

    W_orth
    W_cluster
    W_shape
    W_prefix
    W_suffix
    W_pos
    W_lemma
    W_flags

    N1_orth
    N1_cluster
    N1_shape
    N1_prefix
    N1_suffix
    N1_pos
    N1_lemma
    N1_flags

    N2_orth
    N2_cluster
    N2_shape
    N2_prefix
    N2_suffix
    N2_pos
    N2_lemma
    N2_flags

    N_CONTEXT_FIELDS


cdef class TaggerNeuralNet(NeuralNet):
    def __init__(self, n_classes,
            depth=5, hidden_width=50,
            words_width=30, shape_width=20, suffix_width=20, tags_width=20,
            learn_rate=0.1):
        input_length = 5 * words_width + 5 * shape_width + 5 * suffix_width + 2 * tags_width
        widths = [input_length] + [hidden_width] * depth + [n_classes]
        vector_widths = [words_width, shape_width, suffix_width, tags_width]
        slots = [0] * 5 + [1] * 5 + [2] * 5 + [3] * 2
        NeuralNet.__init__(
            self,
            widths,
            embed=(vector_widths, slots),
            eta=learn_rate,
            rho=1e-6,
            update_step='sgd')

    cdef void set_featuresC(self, ExampleC* eg, const TokenC* tokens, int i) except *:
        eg.nr_feat = self.nr_feat
        for j in range(eg.nr_feat):
            eg.features[j].value = 1.0
            eg.features[j].i = j
        eg.features[0].key = tokens[i].lex.lower
        eg.features[1].key = tokens[i-1].lex.lower
        eg.features[2].key = tokens[i-2].lex.lower
        eg.features[3].key = tokens[i+1].lex.lower
        eg.features[4].key = tokens[i+2].lex.lower
        eg.features[5].key = tokens[i].lex.shape
        eg.features[6].key = tokens[i-1].lex.shape
        eg.features[7].key = tokens[i-2].lex.shape
        eg.features[8].key = tokens[i+1].lex.shape
        eg.features[9].key = tokens[i+2].lex.shape
        eg.features[10].key = tokens[i].lex.suffix
        eg.features[11].key = tokens[i-1].lex.suffix
        eg.features[12].key = tokens[i-2].lex.suffix
        eg.features[13].key = tokens[i+1].lex.suffix
        eg.features[14].key = tokens[i+2].lex.suffix
 
        eg.features[15].key = tokens[i-2].tag
        eg.features[16].key = tokens[i-1].tag

    def end_training(self):
        pass

    def dump(self, loc):
        pass

    property nr_feat:
        def __get__(self):
            return 17


cdef class CharacterTagger(NeuralNet):
    def __init__(self, n_classes,
            depth=3, hidden_width=100, chars_width=5, tags_width=10, learn_rate=0.1,
            left_window=2, right_window=2, tags_window=10, chars_per_word=8):
        self.chars_per_word = chars_per_word
        self.chars_width = chars_width
        self.tags_width = tags_width
        self.left_window = left_window
        self.right_window = right_window
        self.tags_window = tags_window
        self.depth = depth
        self.hidden_width = hidden_width
        
        input_length = self.left_window * self.chars_width * self.chars_per_word \
                     + self.right_window * self.chars_width * self.chars_per_word \
                     + 1 * self.chars_width * self.chars_per_word \
                     + self.tags_window * self.tags_width
        
        widths = [input_length] + [self.hidden_width] * self.depth + [n_classes]
        
        vector_widths = [chars_width, tags_width]
        slots = [0] * self.left_window * self.chars_per_word \
              + [0] * self.right_window * self.chars_per_word \
              + [0] * 1 * self.chars_per_word \
              + [1] * self.tags_window
        NeuralNet.__init__(
            self,
            widths,
            embed=(vector_widths, slots),
            eta=learn_rate,
            rho=1e-6,
            update_step='sgd')

    cdef void set_featuresC(self, ExampleC* eg,
            const TokenC* tokens, object strings, const int i) except *:
        cdef unicode oov = ''
        p2 = strings[i-2] if i >= 2 else oov
        p1 = strings[i-1] if i >= 1 else oov
        w = strings[i]
        n1 = strings[i+1] if (i+1) < len(strings) else oov
        n2 = strings[i+2] if (i+2) < len(strings) else oov
        cdef int chars_per_word = self.chars_per_word
        eg.nr_feat = 0
        for string in (p2, p1, w, n1, n2):
            set_character_features(&eg.features[eg.nr_feat],
                string, chars_per_word)
            eg.nr_feat += chars_per_word
        cdef int hist
        for hist in range(1, self.tags_window+1):
            tag = tokens[i-hist].tag if hist <= i else 0
            eg.features[eg.nr_feat].key = tag
            eg.features[eg.nr_feat].value = 1.0
            eg.nr_feat += 1
        cdef int p
        for p in range(eg.nr_feat):
            eg.features[p].i = p
   
    def end_training(self):
        pass

    def dump(self, loc):
        pass

    property nr_feat:
        def __get__(self):
            nr_word = self.left_window + self.right_window + 1
            return self.chars_per_word * nr_word + self.tags_window


cdef inline void _fill_from_token(atom_t* context, const TokenC* t) nogil:
    context[0] = t.lex.lower
    context[1] = t.lex.cluster
    context[2] = t.lex.shape
    context[3] = t.lex.prefix
    context[4] = t.lex.suffix
    context[5] = t.tag
    context[6] = t.lemma
    if t.lex.flags & (1 << IS_ALPHA):
        context[7] = 1
    elif t.lex.flags & (1 << IS_PUNCT):
        context[7] = 2
    elif t.lex.flags & (1 << LIKE_URL):
        context[7] = 3
    elif t.lex.flags & (1 << LIKE_NUM):
        context[7] = 4
    else:
        context[7] = 0


cdef class Tagger:
    """A part-of-speech tagger for English"""
    @classmethod
    def read_config(cls, data_dir):
        return json.load(open(path.join(data_dir, 'pos', 'config.json')))

    @classmethod
    def default_templates(cls):
        return (
            (W_orth,),
            (P1_lemma, P1_pos),
            (P2_lemma, P2_pos),
            (N1_orth,),
            (N2_orth,),

            (W_suffix,),
            (W_prefix,),

            (P1_pos,),
            (P2_pos,),
            (P1_pos, P2_pos),
            (P1_pos, W_orth),
            (P1_suffix,),
            (N1_suffix,),

            (W_shape,),
            (W_cluster,),
            (N1_cluster,),
            (N2_cluster,),
            (P1_cluster,),
            (P2_cluster,),

            (W_flags,),
            (N1_flags,),
            (N2_flags,),
            (P1_flags,),
            (P2_flags,),
        )

    @classmethod
    def blank(cls, vocab, templates, **kwargs):
        model = CharacterTagger(vocab.morphology.n_tags, **kwargs)
        return cls(vocab, model)

    @classmethod
    def load(cls, data_dir, vocab):
        return cls.from_package(get_package(data_dir), vocab=vocab)

    @classmethod
    def from_package(cls, pkg, vocab):
        # TODO: templates.json deprecated? not present in latest package
        templates = cls.default_templates()
        # templates = package.load_utf8(json.load,
        #     'pos', 'templates.json',
        #     default=cls.default_templates())

        model = CharacterTagger()
        if pkg.has_file('pos', 'model'):
            model.load(pkg.file_path('pos', 'model'))
        return cls(vocab, model)

    def __init__(self, Vocab vocab, model):
        self.vocab = vocab
        self.model = model
        
        # TODO: Move this to tag map
        self.freqs = {TAG: defaultdict(int)}
        for tag in self.tag_names:
            self.freqs[TAG][self.vocab.strings[tag]] = 1
        self.freqs[TAG][0] = 1

    @property
    def tag_names(self):
        return self.vocab.morphology.tag_names

    def tag_from_strings(self, Doc tokens, object tag_strs):
        cdef int i
        for i in range(tokens.length):
            self.vocab.morphology.assign_tag(&tokens.c[i], tag_strs[i])
        tokens.is_tagged = True
        tokens._py_tokens = [None] * tokens.length

    def __call__(self, Doc tokens):
        """Apply the tagger, setting the POS tags onto the Doc object.

        Args:
            tokens (Doc): The tokens to be tagged.
        """
        if tokens.length == 0:
            return 0

        cdef Pool mem = Pool()

        cdef int i, tag
        cdef Example eg = Example(nr_atom=N_CONTEXT_FIELDS,
                                  widths=self.model.widths,
                                  nr_class=self.vocab.morphology.n_tags,
                                  nr_feat=self.model.nr_feat)
        strings = [tok.text for tok in tokens]
        for i in range(tokens.length):
            eg.reset()
            if tokens.c[i].pos == 0:
                self.model.set_featuresC(&eg.c, tokens.c, strings, i)
                self.model.predict_example(eg)
                
                guess = VecVec.arg_max_if_true(eg.c.scores, eg.c.is_valid, eg.c.nr_class)
                self.vocab.morphology.assign_tag(&tokens.c[i], guess)
        tokens.is_tagged = True
        tokens._py_tokens = [None] * tokens.length

    def pipe(self, stream, batch_size=1000, n_threads=2):
        for doc in stream:
            self(doc)
            yield doc
    
    def train(self, Doc tokens, object gold_tag_strs):
        assert len(tokens) == len(gold_tag_strs)
        for tag in gold_tag_strs:
            if tag not in self.tag_names:
                msg = ("Unrecognized gold tag: %s. tag_map.json must contain all"
                       "gold tags, to maintain coarse-grained mapping.")
                raise ValueError(msg % tag)
        golds = [self.tag_names.index(g) if g is not None else -1 for g in gold_tag_strs]
        strings = [tok.text for tok in tokens]
        cdef int correct = 0
        cdef Pool mem = Pool()
        cdef Example eg = Example(
            nr_atom=N_CONTEXT_FIELDS,
            nr_class=self.vocab.morphology.n_tags,
            widths=self.model.widths,
            nr_feat=self.model.nr_feat)
        for i in range(tokens.length):
            eg.reset()
            self.model.set_featuresC(&eg.c, tokens.c, strings, i)
            eg.costs = [golds[i] not in (j, -1) for j in range(eg.c.nr_class)]
            
            self.model.train_example(eg)
            
            self.vocab.morphology.assign_tag(&tokens.c[i], eg.guess)
            
            correct += eg.cost == 0
            self.freqs[TAG][tokens.c[i].tag] += 1
        tokens.is_tagged = True
        tokens._py_tokens = [None] * tokens.length
        return correct


@cython.cdivision(True)
cdef int set_character_features(FeatureC* feat, unicode string, int chars_per_word) except -1:
    cdef unicode oov = ''
    cdef int chars_per_side = min(chars_per_word / 2, len(string))
    # Fill from start
    cdef int c
    for c in range(chars_per_side):
        feat.key = ord(string[c])
        feat.value = 1.0
        feat += 1
    # If word is too short, zero this part of the array
    for c in range(chars_per_side, chars_per_word - chars_per_side):
        feat.key = 0
        feat.value = 0
        feat += 1
    # Fill suffix
    for c in range(chars_per_side):
        feat.key = ord(string[-(c+1)])
        feat.value = 1.0
        feat += 1
