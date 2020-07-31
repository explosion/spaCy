from typing import List, Dict, Iterable, Optional, Union, TYPE_CHECKING
from wasabi import Printer
import warnings

from .tokens import Doc, Token, Span
from .errors import Errors, Warnings
from .util import dot_to_dict

if TYPE_CHECKING:
    # This lets us add type hints for mypy etc. without causing circular imports
    from .language import Language  # noqa: F401


def analyze_pipes(
    nlp: "Language", name: str, index: int, warn: bool = True
) -> List[str]:
    """Analyze a pipeline component with respect to its position in the current
    pipeline and the other components. Will check whether requirements are
    fulfilled (e.g. if previous components assign the attributes).

    nlp (Language): The current nlp object.
    name (str): The name of the pipeline component to analyze.
    index (int): The index of the component in the pipeline.
    warn (bool): Show user warning if problem is found.
    RETURNS (List[str]): The problems found for the given pipeline component.
    """
    assert nlp.pipeline[index][0] == name
    prev_pipes = nlp.pipeline[:index]
    meta = nlp.get_pipe_meta(name)
    requires = {annot: False for annot in meta.requires}
    if requires:
        for prev_name, prev_pipe in prev_pipes:
            prev_meta = nlp.get_pipe_meta(prev_name)
            for annot in prev_meta.assigns:
                requires[annot] = True
    problems = []
    for annot, fulfilled in requires.items():
        if not fulfilled:
            problems.append(annot)
            if warn:
                warnings.warn(Warnings.W025.format(name=name, attr=annot))
    return problems


def validate_attrs(values: Iterable[str]) -> Iterable[str]:
    """Validate component attributes provided to "assigns", "requires" etc.
    Raises error for invalid attributes and formatting. Doesn't check if
    custom extension attributes are registered, since this is something the
    user might want to do themselves later in the component.

    values (Iterable[str]): The string attributes to check, e.g. `["token.pos"]`.
    RETURNS (Iterable[str]): The checked attributes.
    """
    data = dot_to_dict({value: True for value in values})
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
                        good = f"{obj_key}._.{ext_attr}"
                        bad = f"{good}.{'.'.join(ext_value)}"
                        raise ValueError(Errors.E183.format(attr=bad, solution=good))
                continue  # we can't validate those further
            if attr.endswith("_"):  # attr is something like "token.pos_"
                raise ValueError(Errors.E184.format(attr=attr, solution=attr[:-1]))
            if value is not True:  # attr is something like doc.x.y
                good = f"{obj_key}.{attr}"
                bad = f"{good}.{'.'.join(value)}"
                raise ValueError(Errors.E183.format(attr=bad, solution=good))
            obj = objs[obj_key]
            if not hasattr(obj, attr):
                raise ValueError(Errors.E185.format(obj=obj_key, attr=attr))
    return values


def _get_feature_for_attr(nlp: "Language", attr: str, feature: str) -> List[str]:
    assert feature in ["assigns", "requires"]
    result = []
    for pipe_name in nlp.pipe_names:
        meta = nlp.get_pipe_meta(pipe_name)
        pipe_assigns = getattr(meta, feature, [])
        if attr in pipe_assigns:
            result.append(pipe_name)
    return result


def get_assigns_for_attr(nlp: "Language", attr: str) -> List[str]:
    """Get all pipeline components that assign an attr, e.g. "doc.tensor".

    pipeline (Language): The current nlp object.
    attr (str): The attribute to check.
    RETURNS (List[str]): Names of components that require the attr.
    """
    return _get_feature_for_attr(nlp, attr, "assigns")


def get_requires_for_attr(nlp: "Language", attr: str) -> List[str]:
    """Get all pipeline components that require an attr, e.g. "doc.tensor".

    pipeline (Language): The current nlp object.
    attr (str): The attribute to check.
    RETURNS (List[str]): Names of components that require the attr.
    """
    return _get_feature_for_attr(nlp, attr, "requires")


def print_summary(
    nlp: "Language",
    *,
    keys: List[str] = ["requires", "assigns", "scores", "retokenizes"],
    pretty: bool = True,
    no_print: bool = False,
) -> Optional[Dict[str, Union[List[str], Dict[str, List[str]]]]]:
    """Print a formatted summary for the current nlp object's pipeline. Shows
    a table with the pipeline components and why they assign and require, as
    well as any problems if available.

    nlp (Language): The nlp object.
    keys (List[str]): The meta keys to show in the table.
    pretty (bool): Pretty-print the results (color etc).
    no_print (bool): Don't print anything, just return the data.
    RETURNS (dict): A dict with "overview" and "problems".
    """
    msg = Printer(pretty=pretty, no_print=no_print)
    overview = {}
    problems = {}
    for i, name in enumerate(nlp.pipe_names):
        meta = nlp.get_pipe_meta(name)
        overview[name] = {"i": i, "name": name}
        for key in keys:
            overview[name][key] = getattr(meta, key, None)
        problems[name] = analyze_pipes(nlp, name, i, warn=False)
    msg.divider("Pipeline Overview")
    header = ["#", "Component", *[key.capitalize() for key in keys]]
    body = [[info for info in entry.values()] for entry in overview.values()]
    msg.table(body, header=header, divider=True, multiline=True)
    n_problems = sum(len(p) for p in problems.values())
    if any(p for p in problems.values()):
        msg.divider(f"Problems ({n_problems})")
        for name, problem in problems.items():
            if problem:
                msg.warn(f"'{name}' requirements not met: {', '.join(problem)}")
    else:
        msg.good("No problems found.")
    if no_print:
        return {"overview": overview, "problems": problems}


def count_pipeline_interdependencies(nlp: "Language") -> List[int]:
    """Count how many subsequent components require an annotation set by each
    component in the pipeline.

    nlp (Language): The current nlp object.
    RETURNS (List[int]): The interdependency counts.
    """
    pipe_assigns = []
    pipe_requires = []
    for name in nlp.pipe_names:
        meta = nlp.get_pipe_meta(name)
        pipe_assigns.append(set(meta.assigns))
        pipe_requires.append(set(meta.requires))
    counts = []
    for i, assigns in enumerate(pipe_assigns):
        count = 0
        for requires in pipe_requires[i + 1 :]:
            if assigns.intersection(requires):
                count += 1
        counts.append(count)
    return counts
