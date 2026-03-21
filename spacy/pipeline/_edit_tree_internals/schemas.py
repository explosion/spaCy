from collections import defaultdict
from typing import Any, Dict, List, Union

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    RootModel,
    StrictBool,
    StrictInt,
    StrictStr,
    ValidationError,
)


class MatchNodeSchema(BaseModel):
    prefix_len: StrictInt = Field(..., title="Prefix length")
    suffix_len: StrictInt = Field(..., title="Suffix length")
    prefix_tree: StrictInt = Field(..., title="Prefix tree")
    suffix_tree: StrictInt = Field(..., title="Suffix tree")

    model_config = ConfigDict(extra="forbid")


class SubstNodeSchema(BaseModel):
    orig: Union[int, StrictStr] = Field(..., title="Original substring")
    subst: Union[int, StrictStr] = Field(..., title="Replacement substring")

    model_config = ConfigDict(extra="forbid")


class EditTreeSchema(RootModel[Union[MatchNodeSchema, SubstNodeSchema]]):
    pass


def validate_edit_tree(obj: Dict[str, Any]) -> List[str]:
    """Validate edit tree.

    obj (Dict[str, Any]): JSON-serializable data to validate.
    RETURNS (List[str]): A list of error messages, if available.
    """
    try:
        EditTreeSchema.model_validate(obj)
        return []
    except ValidationError as e:
        errors = e.errors()
        data = defaultdict(list)
        for error in errors:
            err_loc = " -> ".join([str(p) for p in error.get("loc", [])])
            data[err_loc].append(error.get("msg"))
        return [f"[{loc}] {', '.join(msg)}" for loc, msg in data.items()]  # type: ignore[arg-type]
