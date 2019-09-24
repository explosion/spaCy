# coding: utf8
from __future__ import unicode_literals

from collections import OrderedDict
from wasabi import Printer

from ..tokens import Doc, Token, Span
from ..errors import user_warning
from ..util import get_component_name
from ..compat import class_types


class component(object):
    def __init__(self, name=None, assigns=tuple(), requires=tuple()):
        self.name = name
        # TODO: parse and validate?
        self.assigns = assigns
        self.requires = requires

    def __call__(self, *args, **kwargs):
        obj = args[0]
        args = args[1:]
        is_class = isinstance(obj, class_types)
        base = obj if is_class else object

        class Wrapped(base):
            name = self.name or get_component_name(obj)
            assigns = self.assigns
            requires = self.requires

            def __call__(self, *args, **kwargs):
                return obj(*args, **kwargs)

        Wrapped.__doc__ = obj.__doc__
        Wrapped.__call__.__doc__ = obj.__doc__ if not is_class else obj.__call__.__doc__
        return Wrapped()


def compile_annots(values):
    data = dot_to_dict(values)
    objs = {"doc": Doc, "token": Token, "span": Span}
    for i, key, attrs in enumerate(data.items()):
        if key not in objs:
            raise ValueError("Invalid key: {}".format(key))
        if not isinstance(attrs, dict):
            raise ValueError("Expected attribute after {}".format(key))
        obj = objs[key]
        for attr, value in attrs:
            if attr == "_":
                continue
            if attr.endswith("_"):
                raise ValueError("Don't use underscore attrs: {}".format(attr))
            if value is not True:
                pass


def dot_to_dict(values):
    result = {}
    for value in values:
        path = result
        parts = value.lower().split(".")
        for i, item in enumerate(parts):
            is_last = i == len(parts) - 1
            path = path.setdefault(item, True if is_last else {})
    return result


def print_summary(nlp):
    msg = Printer()
    overview = []
    problems = {}
    for i, (name, pipe) in enumerate(nlp.pipeline):
        requires = getattr(pipe, "requires", [])
        assigns = getattr(pipe, "assigns", [])
        overview.append((i, name, ", ".join(requires), ", ".join(assigns)))
        problems[name] = analyze_pipes(nlp.pipeline, name, pipe, i, warn=False)
    msg.divider("Pipeline Overview")
    msg.table(overview, header=("#", "Component", "Requires", "Assigns"), divider=True)
    if any(p for p in problems.values()):
        msg.divider("Problems")
        for name, problem in problems.items():
            if problem:
                problem = ", ".join(problem)
                msg.warn("'{}' requirements not met: {}".format(name, problem))
    else:
        msg.good("No problems found")


def analyze_pipes(pipeline, name, pipe, index, warn=True):
    assert pipeline[index][0] == name
    prev_pipes = pipeline[:index]
    pipe_requires = getattr(pipe, "requires", [])
    requires = OrderedDict([(annot, False) for annot in pipe_requires])
    if requires:
        for prev_name, prev_pipe in prev_pipes:
            prev_assigns = getattr(prev_pipe, "assigns", [])
            for annot in prev_assigns:
                requires[annot] = True
    problems = []
    for annot, fulfilled in requires.items():
        if not fulfilled:
            problems.append(annot)
            if warn:
                user_warning("'{}' requires '{}' to be set".format(name, annot))
    return problems
