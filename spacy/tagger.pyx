# cython: infer_types=True
# cython: profile=True
import json
import pathlib
from collections import defaultdict
from libc.string cimport memset, memcpy
from libcpp.vector cimport vector
from libc.stdint cimport uint64_t, int32_t, int64_t
cimport numpy as np
import numpy as np
np.import_array()

from cymem.cymem cimport Pool
from thinc.typedefs cimport atom_t, weight_t
from thinc.extra.eg cimport Example
from thinc.structs cimport ExampleC
from thinc.linear.avgtron cimport AveragedPerceptron
from thinc.linalg cimport Vec, VecVec
from thinc.structs cimport FeatureC
from thinc.neural.optimizers import Adam, SGD
from thinc.neural.ops import NumpyOps

from .typedefs cimport attr_t
from .tokens.doc cimport Doc
from .attrs cimport TAG
from .parts_of_speech cimport NO_TAG, ADJ, ADV, ADP, CCONJ, DET, NOUN, NUM, PRON
from .parts_of_speech cimport VERB, X, PUNCT, EOL, SPACE
from .gold cimport GoldParse

from .attrs cimport *


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


cdef class TaggerModel(LinearModel):
    cdef int set_featuresC(self, FeatureC* features, atom_t* context,
            const TokenC* tokens, int i) nogil:
        _fill_from_token(&context[P2_orth], &tokens[i-2])
        _fill_from_token(&context[P1_orth], &tokens[i-1])
        _fill_from_token(&context[W_orth], &tokens[i])
        _fill_from_token(&context[N1_orth], &tokens[i+1])
        _fill_from_token(&context[N2_orth], &tokens[i+2])
        nr_feat = self.extracter.set_features(features, context)
        return nr_feat


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
    """Annotate part-of-speech tags on Doc objects."""
    @classmethod
    def load(cls, path, vocab, require=False):
        """Load the statistical model from the supplied path.

        Arguments:
            path (Path):
                The path to load from.
            vocab (Vocab):
                The vocabulary. Must be shared by the documents to be processed.
            require (bool):
                Whether to raise an error if the files are not found.
        Returns (Tagger):
            The newly created object.
        """
        # TODO: Change this to expect config.json when we don't have to
        # support old data.
        path = path if not isinstance(path, basestring) else pathlib.Path(path)
        if (path / 'templates.json').exists():
            with (path / 'templates.json').open('r', encoding='utf8') as file_:
                templates = json.load(file_)
        elif require:
            raise IOError(
                "Required file %s/templates.json not found when loading Tagger" % str(path))
        else:
            templates = cls.feature_templates
        self = cls(vocab, model=None, feature_templates=templates)

        if (path / 'model').exists():
            self.model.load(str(path / 'model'))
        elif require:
            raise IOError(
                "Required file %s/model not found when loading Tagger" % str(path))
        return self

    def __init__(self, Vocab vocab, TaggerModel model=None, **cfg):
        """Create a Tagger.

        Arguments:
            vocab (Vocab):
                The vocabulary object. Must be shared with documents to be processed.
            model (thinc.linear.AveragedPerceptron):
                The statistical model.
        Returns (Tagger):
            The newly constructed object.
        """
        if model is None:
            print("Create tagger")
            model = TaggerModel(vocab.morphology.n_tags,
                        cfg.get('features', self.feature_templates),
                        learn_rate=0.01, size=2**18)
        self.vocab = vocab
        self.model = model
        # TODO: Move this to tag map
        self.freqs = {TAG: defaultdict(int)}
        for tag in self.tag_names:
            self.freqs[TAG][self.vocab.strings[tag]] = 1
        self.freqs[TAG][0] = 1
        self.cfg = cfg
        self.optimizer = SGD(NumpyOps(), 0.001, momentum=0.9)

    @property
    def tag_names(self):
        return self.vocab.morphology.tag_names

    def __reduce__(self):
        return (self.__class__, (self.vocab, self.model), None, None)

    def tag_from_strings(self, Doc tokens, object tag_strs):
        cdef int i
        for i in range(tokens.length):
            self.vocab.morphology.assign_tag(&tokens.c[i], tag_strs[i])
        tokens.is_tagged = True
        tokens._py_tokens = [None] * tokens.length

    def __call__(self, Doc tokens):
        """Apply the tagger, setting the POS tags onto the Doc object.

        Arguments:
            doc (Doc): The tokens to be tagged.
        Returns:
            None
        """
        if tokens.length == 0:
            return 0

        cdef atom_t[N_CONTEXT_FIELDS] context

        cdef int nr_class = self.vocab.morphology.n_tags
        cdef Pool mem = Pool()
        scores = <weight_t*>mem.alloc(nr_class, sizeof(weight_t))
        features = <FeatureC*>mem.alloc(self.model.nr_feat, sizeof(FeatureC))
        for i in range(tokens.length):
            if tokens.c[i].pos == 0:
                nr_feat = self.model.set_featuresC(features, context, tokens.c, i)
                self.model.set_scoresC(scores,
                    features, nr_feat)
                guess = Vec.arg_max(scores, nr_class)
                self.vocab.morphology.assign_tag_id(&tokens.c[i], guess)
                memset(scores, 0, sizeof(weight_t) * nr_class)
                memset(features, 0, sizeof(FeatureC) * nr_feat)
                memset(context, 0, sizeof(N_CONTEXT_FIELDS))
        tokens.is_tagged = True
        tokens._py_tokens = [None] * tokens.length

    def pipe(self, stream, batch_size=1000, n_threads=2):
        """Tag a stream of documents.

        Arguments:
            stream: The sequence of documents to tag.
            batch_size (int):
                The number of documents to accumulate into a working set.
            n_threads (int):
                The number of threads with which to work on the buffer in parallel,
                if the Matcher implementation supports multi-threading.
        Yields:
            Doc Documents, in order.
        """
        for doc in stream:
            self(doc)
            yield doc

    def update(self, Doc tokens, GoldParse gold, itn=0):
        """Update the statistical model, with tags supplied for the given document.

        Arguments:
            doc (Doc):
                The document to update on.
            gold (GoldParse):
                Manager for the gold-standard tags.
        Returns (int):
            Number of tags correct.
        """
        gold_tag_strs = gold.tags
        assert len(tokens) == len(gold_tag_strs)
        for tag in gold_tag_strs:
            if tag != None and tag not in self.tag_names:
                msg = ("Unrecognized gold tag: %s. tag_map.json must contain all "
                       "gold tags, to maintain coarse-grained mapping.")
                raise ValueError(msg % tag)
        cdef Pool mem = Pool()
        golds = <int*>mem.alloc(sizeof(int), len(gold_tag_strs))
        for i, g in enumerate(gold_tag_strs):
            golds[i] = self.tag_names.index(g) if g is not None else -1

        cdef atom_t[N_CONTEXT_FIELDS] context
        cdef int nr_class = self.model.nr_class
        costs = <weight_t*>mem.alloc(sizeof(weight_t), nr_class)
        features = <FeatureC*>mem.alloc(sizeof(FeatureC), self.model.nr_feat)
        scores = <weight_t*>mem.alloc(sizeof(weight_t), nr_class)
        d_scores = <weight_t*>mem.alloc(sizeof(weight_t), nr_class)

        cdef int correct = 0
        for i in range(tokens.length):
            nr_feat = self.model.set_featuresC(features, context, tokens.c, i)
            self.model.set_scoresC(scores,
                features, nr_feat)

            if golds[i] != -1:
                for j in range(nr_class):
                    costs[j] = 1
                costs[golds[i]] = 0
            self.model.log_lossC(d_scores, scores, costs)
            self.model.set_gradientC(d_scores, features, nr_feat)

            guess = Vec.arg_max(scores, nr_class)
            #print(tokens[i].text, golds[i], guess, [features[i].key for i in range(nr_feat)])

            self.vocab.morphology.assign_tag_id(&tokens.c[i], guess)

            self.freqs[TAG][tokens.c[i].tag] += 1
            correct += costs[guess] == 0

            memset(features, 0, sizeof(FeatureC) * nr_feat)
            memset(costs, 0, sizeof(weight_t) * nr_class)
            memset(scores, 0, sizeof(weight_t) * nr_class)
            memset(d_scores, 0, sizeof(weight_t) * nr_class)
 
        #if itn % 10 == 0:
        #    self.optimizer(self.model.weights.ravel(), self.model.d_weights.ravel(),
        #                   key=1)
        tokens.is_tagged = True
        tokens._py_tokens = [None] * tokens.length
        return correct


    feature_templates = (
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
