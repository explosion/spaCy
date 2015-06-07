from os import path
import json

class Config(object):
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def get(self, attr, default=None):
        return self.__dict__.get(attr, default)

    @classmethod
    def write(cls, model_dir, name, **kwargs):
        open(path.join(model_dir, '%s.json' % name), 'w').write(json.dumps(kwargs))

    @classmethod
    def read(cls, model_dir, name):
        return cls(**json.load(open(path.join(model_dir, '%s.json' % name))))
