# coding: utf8
from __future__ import unicode_literals

import warnings

from collections import OrderedDict
from wasabi import Printer

from .tokens import Doc, Token, Span
from .errors import Errors, Warnings


def analyze_pipes(pipeline, name, pipe, index, warn=True):
    """Analyze a pipeline component with respect to its position in the current
    pipeline and the other components. Will check whether requirements are
    fulfilled (e.g. if previous components assign the attributes).

    pipeline (list): A list of (name, pipe) tuples e.g. nlp.pipeline.
    name (unicode): The name of the pipeline component to analyze.
    pipe (callable): The pipeline component function to analyze.
    index (int): The index of the component in the pipeline.
    warn (bool): Show user warning if problem is found.
    RETURNS (list): The problems found for the given pipeline component.
    """
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
                warnings.warn(Warnings.W025.format(name=name, attr=annot))
    return problems


def analyze_all_pipes(pipeline, warn=True):
    """Analyze all pipes in the pipeline in order.

    pipeline (list): A list of (name, pipe) tuples e.g. nlp.pipeline.
    warn (bool): Show user warning if problem is found.
    RETURNS (dict): The problems found, keyed by component name.
    """
    problems = {}
    for i, (name, pipe) in enumerate(pipeline):
        problems[name] = analyze_pipes(pipeline, name, pipe, i, warn=warn)
    return problems


def dot_to_dict(values):
    """Convert dot notation to a dict. For example: ["token.pos", "token._.xyz"]
    become {"token": {"pos": True, "_": {"xyz": True }}}.

    values (iterable): The values to convert.
    RETURNS (dict): The converted values.
    """
    result = {}
    for value in values:
        path = result
        parts = value.lower().split(".")
        for i, item in enumerate(parts):
            is_last = i == len(parts) - 1
            path = path.setdefault(item, True if is_last else {})
    return result


def validate_attrs(values):
    """Validate component attributes provided to "assigns", "requires" etc.
    Raises error for invalid attributes and formatting. Doesn't check if
    custom extension attributes are registered, since this is something the
    user might want to do themselves later in the component.

    values (iterable): The string attributes to check, e.g. `["token.pos"]`.
    RETURNS (iterable): The checked attributes.
    """
    data = dot_to_dict(values)
    objs = {"doc": Doc, "token": Token, "span": Span}
    for obj_key, attrs in data.items():
        if obj_key == "span":
            # Support Span only for custom extension attributes
            span_attrs = [attr for attr in values if attr.startswith("span.")]
            span_attrs = [attr for attr in span_attrs if not attr.startswith("span._.")]
            if span_attrs:
                raise ValueError(Errors.E180.format(attrs=", ".join(span_attrs)))
        if obj_key not in objs:  # first element is not doc/token/span
            invalid_attrs = ", ".join(a for a in values if a.startswith(obj_key))
            raise ValueError(Errors.E181.format(obj=obj_key, attrs=invalid_attrs))
        if not isinstance(attrs, dict):  # attr is something like "doc"
            raise ValueError(Errors.E182.format(attr=obj_key))
        for attr, value in attrs.items():
            if attr == "_":
                if value is True:  # attr is something like "doc._"
                    raise ValueError(Errors.E182.format(attr="{}._".format(obj_key)))
                for ext_attr, ext_value in value.items():
                    # We don't check whether the attribute actually exists
                    if ext_value is not True:  # attr is something like doc._.x.y
                        good = "{}._.{}".format(obj_key, ext_attr)
                        bad = "{}.{}".format(good, ".".join(ext_value))
                        raise ValueError(Errors.E183.format(attr=bad, solution=good))
                continue  # we can't validate those further
            if attr.endswith("_"):  # attr is something like "token.pos_"
                raise ValueError(Errors.E184.format(attr=attr, solution=attr[:-1]))
            if value is not True:  # attr is something like doc.x.y
                good = "{}.{}".format(obj_key, attr)
                bad = "{}.{}".format(good, ".".join(value))
                raise ValueError(Errors.E183.format(attr=bad, solution=good))
            obj = objs[obj_key]
            if not hasattr(obj, attr):
                raise ValueError(Errors.E185.format(obj=obj_key, attr=attr))
    return values


def _get_feature_for_attr(pipeline, attr, feature):
    assert feature in ["assigns", "requires"]
    result = []
    for pipe_name, pipe in pipeline:
        pipe_assigns = getattr(pipe, feature, [])
        if attr in pipe_assigns:
            result.append((pipe_name, pipe))
    return result


def get_assigns_for_attr(pipeline, attr):
    """Get all pipeline components that assign an attr, e.g. "doc.tensor".

    pipeline (list): A list of (name, pipe) tuples e.g. nlp.pipeline.
    attr (unicode): The attribute to check.
    RETURNS (list): (name, pipeline) tuples of components that assign the attr.
    """
    return _get_feature_for_attr(pipeline, attr, "assigns")


def get_requires_for_attr(pipeline, attr):
    """Get all pipeline components that require an attr, e.g. "doc.tensor".

    pipeline (list): A list of (name, pipe) tuples e.g. nlp.pipeline.
    attr (unicode): The attribute to check.
    RETURNS (list): (name, pipeline) tuples of components that require the attr.
    """
    return _get_feature_for_attr(pipeline, attr, "requires")


def print_summary(nlp, pretty=True, no_print=False):
    """Print a formatted summary for the current nlp object's pipeline. Shows
    a table with the pipeline components and why they assign and require, as
    well as any problems if available.

    nlp (Language): The nlp object.
    pretty (bool): Pretty-print the results (color etc).
    no_print (bool): Don't print anything, just return the data.
    RETURNS (dict): A dict with "overview" and "problems".
    """
    msg = Printer(pretty=pretty, no_print=no_print)
    overview = []
    problems = {}
    for i, (name, pipe) in enumerate(nlp.pipeline):
        requires = getattr(pipe, "requires", [])
        assigns = getattr(pipe, "assigns", [])
        retok = getattr(pipe, "retokenizes", False)
        overview.append((i, name, requires, assigns, retok))
        problems[name] = analyze_pipes(nlp.pipeline, name, pipe, i, warn=False)
    msg.divider("Pipeline Overview")
    header = ("#", "Component", "Requires", "Assigns", "Retokenizes")
    msg.table(overview, header=header, divider=True, multiline=True)
    n_problems = sum(len(p) for p in problems.values())
    if any(p for p in problems.values()):
        msg.divider("Problems ({})".format(n_problems))
        for name, problem in problems.items():
            if problem:
                problem = ", ".join(problem)
                msg.warn("'{}' requirements not met: {}".format(name, problem))
    else:
        msg.good("No problems found.")
    if no_print:
        return {"overview": overview, "problems": problems}
