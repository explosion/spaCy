import numpy

from thinc.api import chain, Maxout, LayerNorm, Softmax, Linear, zero_init, Model


def build_multi_task_model(tok2vec, maxout_pieces, token_vector_width, nO=None):
    softmax = Softmax(nO=nO, nI=token_vector_width * 2)
    model = chain(
        tok2vec,
        Maxout(
            nO=token_vector_width * 2,
            nI=token_vector_width,
            nP=maxout_pieces,
            dropout=0.0,
        ),
        LayerNorm(token_vector_width * 2),
        softmax,
    )
    model.set_ref("tok2vec", tok2vec)
    model.set_ref("output_layer", softmax)
    return model


def build_cloze_multi_task_model(vocab, tok2vec, maxout_pieces, nO=None):
    # nO = vocab.vectors.data.shape[1]
    output_layer = chain(
        Maxout(
            nO=nO,
            nI=tok2vec.get_dim("nO"),
            nP=maxout_pieces,
            normalize=True,
            dropout=0.0,
        ),
        Linear(nO=nO, nI=nO, init_W=zero_init),
    )
    model = chain(tok2vec, output_layer)
    model = build_masked_language_model(vocab, model)
    model.set_ref("tok2vec", tok2vec)
    model.set_ref("output_layer", output_layer)
    return model


def build_masked_language_model(vocab, wrapped_model, mask_prob=0.15):
    """Convert a model into a BERT-style masked language model"""

    random_words = _RandomWords(vocab)

    def mlm_forward(model, docs, is_train):
        mask, docs = _apply_mask(docs, random_words, mask_prob=mask_prob)
        mask = model.ops.asarray(mask).reshape((mask.shape[0], 1))
        output, backprop = model.get_ref("wrapped-model").begin_update(docs)

        def mlm_backward(d_output):
            d_output *= 1 - mask
            return backprop(d_output)

        return output, mlm_backward

    mlm_model = Model("masked-language-model", mlm_forward, layers=[wrapped_model])
    mlm_model.set_ref("wrapped-model", wrapped_model)

    return mlm_model


class _RandomWords(object):
    def __init__(self, vocab):
        self.words = [lex.text for lex in vocab if lex.prob != 0.0]
        self.probs = [lex.prob for lex in vocab if lex.prob != 0.0]
        self.words = self.words[:10000]
        self.probs = self.probs[:10000]
        self.probs = numpy.exp(numpy.array(self.probs, dtype="f"))
        self.probs /= self.probs.sum()
        self._cache = []

    def next(self):
        if not self._cache:
            self._cache.extend(
                numpy.random.choice(len(self.words), 10000, p=self.probs)
            )
        index = self._cache.pop()
        return self.words[index]


def _apply_mask(docs, random_words, mask_prob=0.15):
    # This needs to be here to avoid circular imports
    from ...tokens import Doc

    N = sum(len(doc) for doc in docs)
    mask = numpy.random.uniform(0.0, 1.0, (N,))
    mask = mask >= mask_prob
    i = 0
    masked_docs = []
    for doc in docs:
        words = []
        for token in doc:
            if not mask[i]:
                word = _replace_word(token.text, random_words)
            else:
                word = token.text
            words.append(word)
            i += 1
        spaces = [bool(w.whitespace_) for w in doc]
        # NB: If you change this implementation to instead modify
        # the docs in place, take care that the IDs reflect the original
        # words. Currently we use the original docs to make the vectors
        # for the target, so we don't lose the original tokens. But if
        # you modified the docs in place here, you would.
        masked_docs.append(Doc(doc.vocab, words=words, spaces=spaces))
    return mask, masked_docs


def _replace_word(word, random_words, mask="[MASK]"):
    roll = numpy.random.random()
    if roll < 0.8:
        return mask
    elif roll < 0.9:
        return random_words.next()
    else:
        return word
