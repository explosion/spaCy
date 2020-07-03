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
