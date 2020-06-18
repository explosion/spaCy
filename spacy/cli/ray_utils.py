"""Allreduce distributed training with Ray."""

import random
import ray
import numpy
from wasabi import msg
from .. import util

cp = None
nccl = None

from typing import Dict, Optional, Union, Tuple, List, cast
from thinc.types import FloatsXd


def create_optimizer(config_path):
    msg.info(f"Loading config from: {config_path}")
    config = util.load_config(config_path, create_objects=False)
    util.fix_random_seed(config["training"]["seed"])
    config = util.load_config(config_path, create_objects=True)
    training = config["training"]
    return training["optimizer"]

class RayWorker:
    def __init__(self, rank, world_size):
        global nccl
        from cupy.cuda import nccl
        self.rank = rank
        self.world_size = world_size
        self.unique_id = nccl.get_unique_id()

    def initialize(self, head_id):
        self.communicator = nccl.NcclCommunicator(self.world_size, head_id, self.rank)

    def get_unique_id(self):
        return self.unique_id

    def execute(self, fn):
        return fn(self)

class AllreduceOptimizer:
    def __init__(self, config_path, communicator):
        global cp
        import cupy as cp
        global nccl
        from cupy.cuda import nccl
        self.optimizer = create_optimizer(config_path)
        self.communicator = communicator
        self.weights_synced = set()

    def allreduce(self, tensor):
        self.communicator.allReduce(
            tensor.data.ptr,
            tensor.data.ptr,
            tensor.size,
            nccl.NCCL_FLOAT32,
            nccl.NCCL_SUM,  # TODO: is this a sum?
            cp.cuda.Stream.null.ptr
        )
        return tensor

    def __call__(
        self,
        key: Tuple[int, str],
        weights: FloatsXd,
        gradient: FloatsXd,
        *,
        lr_scale: float = 1.0,
    ):
        if key not in self.weights_synced:
            self.weights_synced.add(key)
            weights = self.allreduce(weights) / self.communicator.size()


        gradient = self.allreduce(gradient) / self.communicator.size()
        flat_weights, gradient = self.optimizer(key, weights, gradient, lr_scale=lr_scale)
        return flat_weights, gradient


    def __getattr__(self, name):
        return getattr(self.optimizer, name)
