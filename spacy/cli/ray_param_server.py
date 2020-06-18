"""Parameter Server distributed training with Ray."""
import threading
import ray
from wasabi import msg
from .. import util
from spacy.cli.ray_utils import create_optimizer

class OptimizerWorker:
    def __init__(self, config_path, world_size):
        self.optimizer = create_optimizer(config_path)
        self.new_weights = None
        self.barrier = threading.Barrier(world_size)
        self.lock = threading.Lock()
        self.waiting = 0
        self.weights_dict = {}
        self.grad_dict = {}
        self.world_size = world_size

    def call(self, key, weights, gradient, *, lr_scale=1.0):
        self.lock.acquire()

        if self.waiting < self.world_size - 1:
            if self.waiting == 0:
                self.gradient[key] = gradient.copy()
                self.weights_dict[key] = weights.copy()
            else:
                self.gradient[key] += gradient
            self.waiting = self.barrier.n_waiting + 1
            self.lock.release()
            self.barrier.wait()
        else:
            self.gradient[key] += gradient
            self.lock.release()
            self.gradient[key] /= self.world_size
            new_weights, new_grads = self.optimizer(
                key, self.weights_dict[key], self.gradient[key], lr_scale=lr_scale)
            self.weights_dict[key] = new_weights
            self.gradient[key] = new_grads
            self.waiting = 0
            self.barrier.wait()
        return self.weights_dict[key], self.gradient[key]

    def fetch(self):
        return self.optimizer

    def step_schedules(self):
        self.optimizer.step_schedules()

class RayOptimizer:
    local_optimizer = None

    def __init__(self, config_path, use_gpu, rank):
        RemoteOptimizer = ray.remote(OptimizerWorker)
        if use_gpu >= 0:
            RemoteOptimizer = RemoteOptimizer.options(num_gpus=0.1)
        self.optimizer = RemoteOptimizer.remote(config_path)
        self.rank = rank
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
