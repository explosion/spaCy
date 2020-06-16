import ray
from wasabi import msg
from .. import util

cp = None
nccl = None

from typing import Dict, Optional, Union, Tuple, List, cast
from thinc.types import FloatsXd

def _create_optimizer(config_path):
    msg.info(f"Loading config from: {config_path}")
    config = util.load_config(config_path, create_objects=False)
    util.fix_random_seed(config["training"]["seed"])  # Fix this.
    config = util.load_config(config_path, create_objects=True)
    training = config["training"]
    return training["optimizer"]

class OptimizerWorker:
    def __init__(self, config_path):
        self.optimizer = _create_optimizer(config_path)
        self.weights_dict = {}

    def call(self, key, weights, gradient, *, lr_scale=1.0):
        if key not in self.weights_dict:
            self.weights_dict[key] = weights.copy()
        new_weights, new_grads = self.optimizer(
            key, self.weights_dict[key], gradient.copy(), lr_scale=lr_scale)
        self.weights_dict[key] = new_weights
        return new_weights, new_grads

    def fetch(self):
        return self.optimizer

    def step_schedules(self):
        self.optimizer.step_schedules()

class RayOptimizer:
    local_optimizer = None

    def __init__(self, config_path, use_gpu):
        RemoteOptimizer = ray.remote(OptimizerWorker)
        if use_gpu >= 0:
            RemoteOptimizer = RemoteOptimizer.options(num_gpus=0.1)
        self.optimizer = RemoteOptimizer.remote(config_path)
        self.sync()

    def sync(self):
        self.local_optimizer = ray.get(self.optimizer.fetch.remote())

    def __call__(self, *args, **kwargs):
        weights, grads = ray.get(self.optimizer.call.remote(*args, **kwargs))
        return weights.copy(), grads.copy()

    def __getattr__(self, name):
        return getattr(self.local_optimizer, name)

    def step_schedules(self):
        self.optimizer.step_schedules.remote()
        self.sync()

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
        self.optimizer = _create_optimizer(config_path)
        self.communicator = communicator

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
        # weights = self.allreduce(weights)
        gradient = self.allreduce(gradient)
        flat_weights, gradient = self.optimizer(key, weights, gradient, lr_scale=lr_scale)
        return flat_weights, gradient


    def __getattr__(self, name):
        return getattr(self.optimizer, name)
