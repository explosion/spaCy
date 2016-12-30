from paddle.trainer_config_helpers import *


def bidirectional_lstm_net(input_dim,
                           class_dim=2,
                           emb_dim=128,
                           lstm_dim=128,
                           is_predict=False):
    data = data_layer("word", input_dim)
    emb = embedding_layer(input=data, size=emb_dim)
    bi_lstm = bidirectional_lstm(input=emb, size=lstm_dim)
    dropout = dropout_layer(input=bi_lstm, dropout_rate=0.5)
    output = fc_layer(input=dropout, size=class_dim, act=SoftmaxActivation())

    if not is_predict:
        lbl = data_layer("label", 1)
        outputs(classification_cost(input=output, label=lbl))
    else:
        outputs(output)
