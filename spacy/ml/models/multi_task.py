from thinc.api import chain, Maxout, LayerNorm, Softmax, Linear, zero_init


def build_multi_task_model(n_tags, tok2vec=None, token_vector_width=96):
    model = chain(
        tok2vec,
        Maxout(nO=token_vector_width * 2, nI=token_vector_width, nP=3, dropout=0.0),
        LayerNorm(token_vector_width * 2),
        Softmax(nO=n_tags, nI=token_vector_width * 2),
    )
    return model


def build_cloze_multi_task_model(vocab, tok2vec):
    output_size = vocab.vectors.data.shape[1]
    output_layer = chain(
        Maxout(
            nO=output_size, nI=tok2vec.get_dim("nO"), nP=3, normalize=True, dropout=0.0
        ),
        Linear(nO=output_size, nI=output_size, init_W=zero_init),
    )
    model = chain(tok2vec, output_layer)
    model = build_masked_language_model(vocab, model)
    return model


def build_masked_language_model(*args, **kwargs):
    # TODO cf https://github.com/explosion/spaCy/blob/2c107f02a4d60bda2440db0aad1a88cbbf4fb52d/spacy/_ml.py#L828
    raise NotImplementedError
