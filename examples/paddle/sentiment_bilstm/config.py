from paddle.trainer_config_helpers import *

define_py_data_sources2(train_list='train.list',
                        test_list='test.list',
                        module="dataprovider",
                        obj="process")

settings(
  batch_size=128,
  learning_rate=2e-3,
  learning_method=AdamOptimizer(),
  regularization=L2Regularization(8e-4),
  gradient_clipping_threshold=25
)
