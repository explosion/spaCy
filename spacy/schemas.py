from typing import Dict, List, Union, Optional
from enum import Enum
from pydantic import BaseModel, Field, ValidationError, validator
from pydantic import StrictStr, StrictInt, StrictFloat, StrictBool
from collections import defaultdict

from .attrs import NAMES


def validate(schema, obj):
    """Validate data against a given pydantic schema.

    obj (dict): JSON-serializable data to validate.
    schema (pydantic.BaseModel): The schema to validate against.
    RETURNS (list): A list of error messages, if available.
    """
    try:
        schema(**obj)
        return []
    except ValidationError as e:
        errors = e.errors()
        data = defaultdict(list)
        for error in errors:
            err_loc = " -> ".join([str(p) for p in error.get("loc", [])])
            data[err_loc].append(error.get("msg"))
        return [f"[{loc}] {', '.join(msg)}" for loc, msg in data.items()]


# Matcher token patterns


def validate_token_pattern(obj):
    # Try to convert non-string keys (e.g. {ORTH: "foo"} -> {"ORTH": "foo"})
    get_key = lambda k: NAMES[k] if isinstance(k, int) and k < len(NAMES) else k
    if isinstance(obj, list):
        converted = []
        for pattern in obj:
            if isinstance(pattern, dict):
                pattern = {get_key(k): v for k, v in pattern.items()}
            converted.append(pattern)
        obj = converted
    return validate(TokenPatternSchema, {"pattern": obj})


class TokenPatternString(BaseModel):
    REGEX: Optional[StrictStr]
    IN: Optional[List[StrictStr]]
    NOT_IN: Optional[List[StrictStr]]

    class Config:
        extra = "forbid"

    @validator("*", pre=True, whole=True)
    def raise_for_none(cls, v):
        if v is None:
            raise ValueError("None / null is not allowed")
        return v


class TokenPatternNumber(BaseModel):
    REGEX: Optional[StrictStr] = None
    IN: Optional[List[StrictInt]] = None
    NOT_IN: Optional[List[StrictInt]] = None
    EQ: Union[StrictInt, StrictFloat] = Field(None, alias="==")
    GEQ: Union[StrictInt, StrictFloat] = Field(None, alias=">=")
    LEQ: Union[StrictInt, StrictFloat] = Field(None, alias="<=")
    GT: Union[StrictInt, StrictFloat] = Field(None, alias=">")
    LT: Union[StrictInt, StrictFloat] = Field(None, alias="<")

    class Config:
        extra = "forbid"

    @validator("*", pre=True, whole=True)
    def raise_for_none(cls, v):
        if v is None:
            raise ValueError("None / null is not allowed")
        return v


class TokenPatternOperator(str, Enum):
    plus: StrictStr = "+"
    start: StrictStr = "*"
    question: StrictStr = "?"
    exclamation: StrictStr = "!"


StringValue = Union[TokenPatternString, StrictStr]
NumberValue = Union[TokenPatternNumber, StrictInt, StrictFloat]
UnderscoreValue = Union[
    TokenPatternString, TokenPatternNumber, str, int, float, list, bool,
]


class TokenPattern(BaseModel):
    orth: Optional[StringValue] = None
    text: Optional[StringValue] = None
    lower: Optional[StringValue] = None
    pos: Optional[StringValue] = None
    tag: Optional[StringValue] = None
    dep: Optional[StringValue] = None
    lemma: Optional[StringValue] = None
    shape: Optional[StringValue] = None
    ent_type: Optional[StringValue] = None
    norm: Optional[StringValue] = None
    length: Optional[NumberValue] = None
    spacy: Optional[StrictBool] = None
    is_alpha: Optional[StrictBool] = None
    is_ascii: Optional[StrictBool] = None
    is_digit: Optional[StrictBool] = None
    is_lower: Optional[StrictBool] = None
    is_upper: Optional[StrictBool] = None
    is_title: Optional[StrictBool] = None
    is_punct: Optional[StrictBool] = None
    is_space: Optional[StrictBool] = None
    is_bracket: Optional[StrictBool] = None
    is_quote: Optional[StrictBool] = None
    is_left_punct: Optional[StrictBool] = None
    is_right_punct: Optional[StrictBool] = None
    is_currency: Optional[StrictBool] = None
    is_stop: Optional[StrictBool] = None
    is_sent_start: Optional[StrictBool] = None
    sent_start: Optional[StrictBool] = None
    like_num: Optional[StrictBool] = None
    like_url: Optional[StrictBool] = None
    like_email: Optional[StrictBool] = None
    op: Optional[TokenPatternOperator] = None
    underscore: Optional[Dict[StrictStr, UnderscoreValue]] = Field(None, alias="_")

    class Config:
        extra = "forbid"
        allow_population_by_field_name = True
        alias_generator = lambda value: value.upper()

    @validator("*", pre=True)
    def raise_for_none(cls, v):
        if v is None:
            raise ValueError("None / null is not allowed")
        return v


class TokenPatternSchema(BaseModel):
    pattern: List[TokenPattern] = Field(..., minItems=1)

    class Config:
        extra = "forbid"


# Model meta


class ModelMetaSchema(BaseModel):
    # fmt: off
    lang: StrictStr = Field(..., title="Two-letter language code, e.g. 'en'")
    name: StrictStr = Field(..., title="Model name")
    version: StrictStr = Field(..., title="Model version")
    spacy_version: Optional[StrictStr] = Field(None, title="Compatible spaCy version identifier")
    parent_package: Optional[StrictStr] = Field("spacy", title="Name of parent spaCy package, e.g. spacy or spacy-nightly")
    pipeline: Optional[List[StrictStr]] = Field([], title="Names of pipeline components")
    description: Optional[StrictStr] = Field(None, title="Model description")
    license: Optional[StrictStr] = Field(None, title="Model license")
    author: Optional[StrictStr] = Field(None, title="Model author name")
    email: Optional[StrictStr] = Field(None, title="Model author email")
    url: Optional[StrictStr] = Field(None, title="Model author URL")
    sources: Optional[Union[List[StrictStr], Dict[str, str]]] = Field(None, title="Training data sources")
    vectors: Optional[Dict[str, int]] = Field(None, title="Included word vectors")
    accuracy: Optional[Dict[str, Union[float, int]]] = Field(None, title="Accuracy numbers")
    speed: Optional[Dict[str, Union[float, int]]] = Field(None, title="Speed evaluation numbers")
    # fmt: on


# Training data object in "simple training style"


class SimpleTrainingSchema(BaseModel):
    # TODO: write

    class Config:
        title = "Schema for training data dict in passed to nlp.update"
        extra = "forbid"


# JSON training format


class TrainingSchema(BaseModel):
    # TODO: write

    class Config:
        title = "Schema for training data in spaCy's JSON format"
        extra = "forbid"
