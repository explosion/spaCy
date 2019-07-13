from thinc.v2v import Maxout, Affine, Model
from thinc.t2v import Pooling, sum_pool
from thinc.api import layerize, chain
from thinc.misc import LayerNorm, Residual
from .pipes import Pipe
from .._ml import logistic, zero_init, Tok2Vec


class SpanCategorizer(Pipe):
    """Predict labels for spans of text."""

    @classmethod
    def Model(cls, nO, **cfg):
        # TODO: Settings here
        tok2vec = Tok2Vec(**cfg)
        with Model.define_operators({">>": chain}):
            span2scores = (
                reshape_add_lengths
                #>> SoftAttention
                >> Pooling(sum_pool)
                >> LayerNorm(Residual(Maxout(tok2vec.nO)))
                >> zero_init(Affine(nO, tok2vec.nO))
                >> logistic
            )
        return SpanCategorizerModel(tok2vec, span2scores)

    def __init__(self, vocab, user_data_key="phrases", max_length=10,
            get_spans=None, model=True):
        self.cfg = {
            "user_data_key": user_data_key,
            "labels": [],
            "max_length": max_length
        }
        self.vocab = vocab
        self.user_data_key = user_data_key
        self.span_getter = get_spans
        self.model = model

    @property
    def tok2vec(self):
        if self.model in (None, True, False):
            return None
        else:
            return self.model.tok2vec

    @property
    def labels(self):
        return tuple(self.cfg.setdefault("labels", []))

    @labels.setter
    def labels(self, value):
        self.cfg["labels"] = tuple(value)

    def add_label(self, label):
        """Add an output label, to be predicted by the model."""
        self.cfg["labels"].append(label)

    def begin_training(
        self, get_gold_tuples=lambda: [], pipeline=None, sgd=None, **kwargs
    ):
        """Initialize the pipe for training, using data exampes if available.
        If no model has been initialized yet, the model is added."""
        for gold in get_gold_tuples():
            if "phrases" in gold:
                for label in gold["phrases"]:
                    self.add_label(label)
        return Pipe.begin_training(self, get_gold_tuples, pipeline, sgd, **kwargs)

    def get_spans(self, docs):
        if self.span_getter is not None:
            return self.span_getter(docs)
        spans = []
        offset = 0
        for doc in docs:
            spans.extend(_get_all_spans(len(doc), self.max_length, offset=offset))
            offset += len(doc)
        return spans

    def predict(self, docs, drop=0.0):
        spans = self.get_spans(docs)
        tokvecs = self.model.tok2vec(docs)
        scores = _predict_batched(self.model.span2scores, tokvecs, spans)
        predictions = _scores2spans(docs, scores, self.labels)
        return {
            "tokvecs": tokvecs,
            "predictions": predictions,
            "scores": scores,
            "spans": spans,
        }

    def set_annotations(self, docs, predictions):
        for doc, doc_predictions in zip(docs, predictions):
            phrases = predictions["predictions"]
            doc.user_data.setdefault(self.user_data_key, [])
            doc.user_data[self.user_data_key].extend(phrases)

    def get_loss(self, spans_scores, token_label_matrix):
        """Regression loss, predicting what % of a span's tokens are in a
        gold-standard span of a given type."""
        spans, scores = indices_scores
        d_scores = numpy.zeros(scores.shape, dtype=scores.dtype)
        labels = scores.argmax(axis=1)
        for i, (start, end) in enumerate(spans):
            target = token_label_weights[start:end].sum(axis=0)
            d_scores[i] = scores - target
        return self.model.ops.asarray(d_scores)

    def update(self, docs, golds, sgd=None, drop=0.0, losses=None):
        if losses is None:
            losses = {self.name: 0.0}
        spans = self.get_spans(docs)
        tokvecs, backprop_tokvecs = self.model.tok2vec.begin_update(docs, drop=drop)
        d_tokvecs = self.ops.allocate(tokvecs.shape, dtype="f")

        grads = {}

        def get_grads(W, dW, key=None):
            grads[key] = (W, dW)

        get_grads.alpha = sgd.alpha
        get_grads.b1 = sgd.b1
        get_grads.b2 = sgd.b2

        golds = [getattr(g, "spans", g) for g in golds]

        token_label_matrix = _get_token_label_matrix(golds, [len(d) for d in docs], self.labels)

        for indices, starts, length in _batch_spans_by_length(spans):
            X = _get_span_batch(tokvecs, starts, length)
            Y, backprop = self.model.spans2scores.begin_update(X, drop=drop)
            dY = self.get_loss((indices, Y), token_label_matrix)
            dX = backprop(dY, sgd=get_grads)
            for i, start in enumerate(starts):
                d_tokvecs[start : start + length] += dX[i]
            losses[self.name] += (dY ** 2).sum()
        backprop_tokvecs(d_tokvecs, sgd=get_grads)
        if sgd is not None:
            for key, (W, dW) in grads.items():
                sgd(W, dW, key=key)
        return losses


class SpanCategorizerModel(Model):
    """Predict labels for spans, using two component models: a tok2vec model,
    and a span2scores model. The input to the SpanCategorizerModel should be
    a tuple (docs, spans), where the spans are an array with two columns:
    (start, end).

    The output will be a tuple (outputs, spans), where the outputs array
    will have one row per span. In the backward pass, we take the gradients w.r.t.
    the spans, and backprop through the input vectors.

    A naive implementation of this process would make a single array, padded
    for all spans. However, the longest span may be very long, and we might
    have lots of spans, so this array could consume an enormous amount of
    memory. Instead, we sort the spans by length and work in batches. This
    reduces the total amount of padding, and means we do not need to hold
    expanded arrays for the whole data. As a bonus, the input model also
    doesn't need to worry about masking: we know that the
    data it works over has no empty items.
    """
    name = "spancat_model"
    def __init__(self, tok2vec, span2scores):
        Model.__init__(self)
        self.tok2vec = tok2vec
        self.span2scores = span2scores
        self._layers.append(tok2vec)
        self._layers.append(span2scores)
        
    @property
    def nO(self):
        return span2scores.nO

    def predict(self, docs_spans):
        """Predict scores for the spans, batching by length."""
        scores = self.ops.xp.zeros((len(spans), model.nO), dtype="f")
        for indices, starts, length in _batch_spans_by_length(spans):
            X = _get_span_batch(tokvecs, starts, length)
            batchY = model(X)
            for i, output_idx in enumerate(indices):
                scores[output_idx] = Y[i]
        return scores

    def begin_update(self, docs_spans, drop=0.):
        """Do the forward pass of the span classification, batching the input.
        
        Returns a tuple (scores, callback), where the callback takes an array
        d_scores and performs the backward pass."""
        docs, spans = docs_spans
        tokvecs, bp_tokvecs = self.tok2vec.begin_update(docs, drop=drop)
        scores = self.ops.xp.zeros((len(spans), model.nO), dtype="f")
        backprops = []
        for indices, starts, length in _batch_spans_by_length(spans):
            X = _get_span_batch(tokvecs, starts, length)
            batchY, backprop = self.span2scores.begin_update(X, drop=drop)
            for i, output_idx in enumerate(indices):
                scores[output_idx] = Y[i]
            backprops.append((indices, starts, length, backprop))
        shape = tokvecs.shape

        def backprop_spancat_model(d_scores, sgd=None):
            d_tokvecs = self.ops.xp.zeros(shape, dtype=d_output.dtype)
            for indices, starts, ends, backprop in backprops:
                dY = d_output[indices]
                dX = backprop(dY)
                for i, (start, end) in enumerate(zip(starts, ends)):
                    d_tokvecs[start:end] += dX[i, : end - start]
            return bp_tokvecs(d_tokvecs, sgd=sgd)

        return scores, backprop_spancat_model


@layerize
def reshape_add_lengths(X, drop=0.):
    xp = get_array_module(X)
    length = X.shape[1]
    lengths = xp.zeros((X.shape[0],), dtype='i')
    lengths += length
    Y = X.reshape((-1, X.shape[-1]))

    def backprop_reshape(dY, sgd=None):
        return dY.reshape((-1, length, dY.shape[-1]))

    return Y, backprop_reshape


def _get_token_label_matrix(gold_phrases, lengths, labels):
    """Figure out how each token should be labelled w.r.t. some gold-standard
    spans, where the labels indicate whether that token is part of the span."""
    output = numpy.zeros((sum(lengths), len(labels)), dtype="i")
    label2class = {label: i for i, label in enumerate(labels)}
    offset = 0
    for doc_phrases, length in gold_phrases:
        for phrase in phrases:
            clas = label2class[phrase.label]
            for i in range(phrase.start, phrase.end):
                output[offset + i, clas] = 1
        offset += length
    return output


def _scores2spans(docs, scores, starts, ends, labels, threshold=0.5):
    """Produce labelled Span objects implied by the model's predictions."""
    token_to_doc = _get_token_to_doc(docs)
    output = []
    # When we predict, assume only one label per identical span.
    guesses = scores.argmax(axis=1)
    bests = scores.max(axis=1)
    for i, start in enumerate(starts):
        doc_i, offset = token_to_doc[start]
        if bests[i] >= threshold:
            span = Span(docs[doc_i], start, ends[i], label=labels[guesses[i]])
            output.append(span)
    return output


def _get_token_to_doc(docs):
    """Map token positions within a batch to a tuple (doc_index, doc_offset).
    When we flatten an array for the batch, this lets us easily find the token
    each row in the flat array corresponds to."""
    offset = 0
    token_to_doc = {}
    for i, doc in enumerate(docs):
        for j in range(len(doc)):
            token_to_doc[j+offset] = (i, offset)
        offset += len(doc)
    return token_to_doc


def _get_all_spans(length, max_len, offset=0):
    """List (start, end) indices of all subsequences up to `max_len`,
    for a sequence of length `length`. Indices may be offset by `offset`.
    """
    spans = []
    for start in range(length):
        for end in range(i + 1, min(i + 1 + max_len, length)):
            spans.append((offset + start, offset + end))
    return spans


def _batch_spans_by_length(spans):
    """Generate groups of spans that have the same length, starting with the
    longest group (going backwards may reduce allocations).
    For each group, yield a tuple (indices, starts, length), where indices
    shows which items from the spans array are in the batch.
    """
    spans = [(e - s, i, s) for i, (s, e) in enumerate(spans)]
    spans.sort(reverse=True)
    batch_start = 0
    i = 0
    while True:
        i += 1
        if i >= len(spans) or spans[i][0] != spans[batch_start][0]:
            _, indices, starts = zip(*spans[batch_start:i])
            yield indices, starts, spans[batch_start][0]
            batch_start = i


def _get_span_batch(vectors, starts, length):
    """Make a contiguous array for spans of a certain length."""
    xp = get_array_module(vectors)
    output = xp.zeros((len(starts), length, vectors.shape[1]))
    for i, start in enumerate(starts):
        output[i] = vectors[start : start + length]
    return output
