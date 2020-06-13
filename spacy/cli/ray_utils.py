import ray
from wasabi import msg
from .. import util


class OptimizerWorker:
    def __init__(self, config_path):
        msg.info(f"Loading config from: {config_path}")
        config = util.load_config(config_path, create_objects=False)
        util.fix_random_seed(config["training"]["seed"])
        config = util.load_config(config_path, create_objects=True)
        training = config["training"]
        optimizer = training["optimizer"]
        self.optimizer = optimizer
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

    def __init__(self, config_path):
        RemoteOptimizer = ray.remote(OptimizerWorker)
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