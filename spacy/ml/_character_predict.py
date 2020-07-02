# Stuff for character-based pretraining


def get_characters_loss(ops, docs, prediction, nr_char):
    target_ids = numpy.vstack([doc.to_utf8_array(nr_char=nr_char) for doc in docs])
    target_ids = target_ids.reshape((-1,))
    target = ops.asarray(to_categorical(target_ids, nb_classes=256), dtype="f")
    target = target.reshape((-1, 256*nr_char))
    diff = prediction - target
    loss = (diff**2).sum()
    d_target = diff / float(prediction.shape[0])
    return loss, d_target


"""
# TODO: Update this to new-thinc.

@describe.attributes(
    W=Synapses("Weights matrix", lambda obj: (obj.nO, obj.nI), lambda W, ops: None)
)
class MultiSoftmax(Affine):
    #"""Neural network layer that predicts several multi-class attributes at once.
    #For instance, we might predict one class with 6 variables, and another with 5.
    #We predict the 11 neurons required for this, and then softmax them such
    #that columns 0-6 make a probability distribution and coumns 6-11 make another.
    #"""
    name = "multisoftmax"

    def __init__(self, out_sizes, nI=None, **kwargs):
        Model.__init__(self, **kwargs)
        self.out_sizes = out_sizes
        self.nO = sum(out_sizes)
        self.nI = nI

    def predict(self, input__BI):
        output__BO = self.ops.affine(self.W, self.b, input__BI)
        i = 0
        for out_size in self.out_sizes:
            self.ops.softmax(output__BO[:, i : i + out_size], inplace=True)
            i += out_size
        return output__BO

    def begin_update(self, input__BI, drop=0.0):
        output__BO = self.predict(input__BI)

        def finish_update(grad__BO, sgd=None):
            self.d_W += self.ops.gemm(grad__BO, input__BI, trans1=True)
            self.d_b += grad__BO.sum(axis=0)
            grad__BI = self.ops.gemm(grad__BO, self.W)
            if sgd is not None:
                sgd(self._mem.weights, self._mem.gradient, key=self.id)
            return grad__BI

        return output__BO, finish_update
"""
