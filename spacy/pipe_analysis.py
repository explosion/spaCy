from typing import TYPE_CHECKING, Dict, ItemsView, Iterable, List, Set, Union

from wasabi import msg

from .errors import Errors
from .tokens import Doc, Span, Token
from .util import dot_to_dict

if TYPE_CHECKING:
    # This lets us add type hints for mypy etc. without causing circular imports
    from .language import Language  # noqa: F401


DEFAULT_KEYS = ["requires", "assigns", "scores", "retokenizes"]


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


def get_attr_info(nlp: "Language", attr: str) -> Dict[str, List[str]]:
    """Check which components in the pipeline assign or require an attribute.

    nlp (Language): The current nlp object.
    attr (str): The attribute, e.g. "doc.tensor".
    RETURNS (Dict[str, List[str]]): A dict keyed by "assigns" and "requires",
        mapped to a list of component names.
    """
    result: Dict[str, List[str]] = {"assigns": [], "requires": []}
    for pipe_name in nlp.pipe_names:
        meta = nlp.get_pipe_meta(pipe_name)
        if attr in meta.assigns:
            result["assigns"].append(pipe_name)
        if attr in meta.requires:
            result["requires"].append(pipe_name)
    return result


def analyze_pipes(
    nlp: "Language", *, keys: List[str] = DEFAULT_KEYS
) -> Dict[str, Dict[str, Union[List[str], Dict]]]:
    """Print a formatted summary for the current nlp object's pipeline. Shows
    a table with the pipeline components and why they assign and require, as
    well as any problems if available.

    nlp (Language): The nlp object.
    keys (List[str]): The meta keys to show in the table.
    RETURNS (dict): A dict with "summary" and "problems".
    """
    result: Dict[str, Dict[str, Union[List[str], Dict]]] = {
        "summary": {},
        "problems": {},
    }
    all_attrs: Set[str] = set()
    for i, name in enumerate(nlp.pipe_names):
        meta = nlp.get_pipe_meta(name)
        all_attrs.update(meta.assigns)
        all_attrs.update(meta.requires)
        result["summary"][name] = {key: getattr(meta, key, None) for key in keys}
        prev_pipes = nlp.pipeline[:i]
        requires = {annot: False for annot in meta.requires}
        if requires:
            for prev_name, prev_pipe in prev_pipes:
                prev_meta = nlp.get_pipe_meta(prev_name)
                for annot in prev_meta.assigns:
                    requires[annot] = True
        result["problems"][name] = [
            annot for annot, fulfilled in requires.items() if not fulfilled
        ]
    result["attrs"] = {attr: get_attr_info(nlp, attr) for attr in all_attrs}
    return result


def print_pipe_analysis(
    analysis: Dict[str, Dict[str, Union[List[str], Dict]]],
    *,
    keys: List[str] = DEFAULT_KEYS,
) -> None:
    """Print a formatted version of the pipe analysis produced by analyze_pipes.

    analysis (Dict[str, Union[List[str], Dict[str, List[str]]]]): The analysis.
    keys (List[str]): The meta keys to show in the table.
    """
    msg.divider("Pipeline Overview")
    header = ["#", "Component", *[key.capitalize() for key in keys]]
    summary: ItemsView = analysis["summary"].items()
    body = [[i, n, *[v for v in m.values()]] for i, (n, m) in enumerate(summary)]
    msg.table(body, header=header, divider=True, multiline=True)
    n_problems = sum(len(p) for p in analysis["problems"].values())
    if any(p for p in analysis["problems"].values()):
        msg.divider(f"Problems ({n_problems})")
        for name, problem in analysis["problems"].items():
            if problem:
                msg.warn(f"'{name}' requirements not met: {', '.join(problem)}")
    else:
        msg.good("No problems found.")
