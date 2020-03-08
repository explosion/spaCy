from thinc.api import Model


def CharacterEmbed(nM, nC):
    # nM: Number of dimensions per character. nC: Number of characters.
    nO = nM * nC if (nM is not None and nC is not None) else None
    return Model(
        "charembed",
        forward,
        init=init,
        dims={"nM": nM, "nC": nC, "nO": nO, "nV": 256},
        params={"E": None},
    ).initialize()


def init(model, X=None, Y=None):
    vectors_table = model.ops.alloc3f(
        model.get_dim("nC"), model.get_dim("nV"), model.get_dim("nM")
    )
    model.set_param("E", vectors_table)


def forward(model, docs, is_train):
    if docs is None:
        return []
    ids = []
    output = []
    E = model.get_param("E")
    nC = model.get_dim("nC")
    nM = model.get_dim("nM")
    nO = model.get_dim("nO")
    # This assists in indexing; it's like looping over this dimension.
    # Still consider this weird witch craft...But thanks to Mark Neumann
    # for the tip.
    nCv = model.ops.xp.arange(nC)
    for doc in docs:
        doc_ids = doc.to_utf8_array(nr_char=nC)
        doc_vectors = model.ops.alloc3f(len(doc), nC, nM)
        # Let's say I have a 2d array of indices, and a 3d table of data. What numpy
        # incantation do I chant to get
        # output[i, j, k] == data[j, ids[i, j], k]?
        doc_vectors[:, nCv] = E[nCv, doc_ids[:, nCv]]
        output.append(doc_vectors.reshape((len(doc), nO)))
        ids.append(doc_ids)

    def backprop(d_output):
        dE = model.ops.alloc(E.shape, dtype=E.dtype)
        for doc_ids, d_doc_vectors in zip(ids, d_output):
            d_doc_vectors = d_doc_vectors.reshape((len(doc_ids), nC, nM))
            dE[nCv, doc_ids[:, nCv]] += d_doc_vectors[:, nCv]
        model.inc_grad("E", dE)
        return []

    return output, backprop
