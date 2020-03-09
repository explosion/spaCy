import numpy
from thinc.api import Model, Unserializable


def SpacyVectors(vectors) -> Model:
    attrs = {"vectors": Unserializable(vectors)}
    model = Model("spacy_vectors", forward, attrs=attrs)
    return model


def forward(model, docs, is_train: bool):
    batch = []
    vectors = model.attrs["vectors"].obj
    for doc in docs:
        indices = numpy.zeros((len(doc),), dtype="i")
        for i, word in enumerate(doc):
            if word.orth in vectors.key2row:
                indices[i] = vectors.key2row[word.orth]
            else:
                indices[i] = 0
        batch_vectors = vectors.data[indices]
        batch.append(batch_vectors)

        def backprop(dY):
            return None

    return batch, backprop
