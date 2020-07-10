from typing import Dict, List, Union, Optional, Sequence, Any
from enum import Enum
from pydantic import BaseModel, Field, ValidationError, validator
from pydantic import StrictStr, StrictInt, StrictFloat, StrictBool
from pydantic import FilePath, DirectoryPath
from collections import defaultdict
from thinc.api import Model, Optimizer

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
    NEQ: Union[StrictInt, StrictFloat] = Field(None, alias="!=")
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
    vectors: Optional[Dict[str, Any]] = Field(None, title="Included word vectors")
    accuracy: Optional[Dict[str, Union[float, int]]] = Field(None, title="Accuracy numbers")
    speed: Optional[Dict[str, Union[float, int]]] = Field(None, title="Speed evaluation numbers")
    # fmt: on


# JSON training format


class TrainingSchema(BaseModel):
    # TODO: write

    class Config:
        title = "Schema for training data in spaCy's JSON format"
        extra = "forbid"


# Config schema
# We're not setting any defaults here (which is too messy) and are making all
# fields required, so we can raise validation errors for missing values. To
# provide a default, we include a separate .cfg file with all values and
# check that against this schema in the test suite to make sure it's always
# up to date.


class ConfigSchemaTraining(BaseModel):
    # fmt: off
    gold_preproc: StrictBool = Field(..., title="Whether to train on gold-standard sentences and tokens")
    max_length: StrictInt = Field(..., title="Maximum length of examples (longer examples are divided into sentences if possible)")
    limit: StrictInt = Field(..., title="Number of examples to use (0 for all)")
    orth_variant_level: StrictFloat = Field(..., title="Orth variants for data augmentation")
    dropout: StrictFloat = Field(..., title="Dropout rate")
    patience: StrictInt = Field(..., title="How many steps to continue without improvement in evaluation score")
    max_epochs: StrictInt = Field(..., title="Maximum number of epochs to train for")
    max_steps: StrictInt = Field(..., title="Maximum number of update steps to train for")
    eval_frequency: StrictInt = Field(..., title="How often to evaluate during training (steps)")
    seed: Optional[StrictInt] = Field(..., title="Random seed")
    accumulate_gradient: StrictInt = Field(..., title="Whether to divide the batch up into substeps")
    use_pytorch_for_gpu_memory: StrictBool = Field(..., title="Allocate memory via PyTorch")
    use_gpu: StrictInt = Field(..., title="GPU ID or -1 for CPU")
    scores: List[StrictStr] = Field(..., title="Score types to be printed in overview")
    score_weights: Dict[StrictStr, Union[StrictFloat, StrictInt]] = Field(..., title="Weights of each score type for selecting final model")
    init_tok2vec: Optional[FilePath] = Field(..., title="Path to pretrained tok2vec weights")
    discard_oversize: StrictBool = Field(..., title="Whether to skip examples longer than batch size")
    omit_extra_lookups: StrictBool = Field(..., title="Don't include extra lookups in model")
    batch_by: StrictStr = Field(..., title="Batch examples by type")
    raw_text: Optional[FilePath] = Field(..., title="Raw text")
    tag_map: Optional[FilePath] = Field(..., title="Path to JSON-formatted tag map")
    batch_size: Union[Sequence[int], int] = Field(..., title="The batch size or batch size schedule")
    optimizer: Optimizer = Field(..., title="The optimizer to use")
    # fmt: on

    class Config:
        extra = "forbid"
        arbitrary_types_allowed = True


class ConfigSchemaNlpComponent(BaseModel):
    factory: StrictStr = Field(..., title="Component factory name")
    model: Model = Field(..., title="Component model")
    # TODO: add config schema / types for components so we can fill and validate
    # component options like learn_tokens, min_action_freq etc.

    class Config:
        extra = "allow"
        arbitrary_types_allowed = True


class ConfigSchemaPipeline(BaseModel):
    __root__: Dict[str, ConfigSchemaNlpComponent]

    class Config:
        extra = "allow"


class ConfigSchemaNlp(BaseModel):
    lang: StrictStr = Field(..., title="The base language to use")
    vectors: Optional[DirectoryPath] = Field(..., title="Path to vectors")
    pipeline: Optional[ConfigSchemaPipeline]

    class Config:
        extra = "forbid"
        arbitrary_types_allowed = True


class ConfigSchema(BaseModel):
    training: ConfigSchemaTraining
    nlp: ConfigSchemaNlp

    class Config:
        extra = "allow"
        arbitrary_types_allowed = True


# Project config Schema


class ProjectConfigAsset(BaseModel):
    # fmt: off
    dest: StrictStr = Field(..., title="Destination of downloaded asset")
    url: Optional[StrictStr] = Field(None, title="URL of asset")
    checksum: str = Field(None, title="MD5 hash of file", regex=r"([a-fA-F\d]{32})")
    # fmt: on


class ProjectConfigCommand(BaseModel):
    # fmt: off
    name: StrictStr = Field(..., title="Name of command")
    help: Optional[StrictStr] = Field(None, title="Command description")
    script: List[StrictStr] = Field([], title="List of CLI commands to run, in order")
    deps: List[StrictStr] = Field([], title="File dependencies required by this command")
    outputs: List[StrictStr] = Field([], title="Outputs produced by this command")
    outputs_no_cache: List[StrictStr] = Field([], title="Outputs not tracked by DVC (DVC only)")
    no_skip: bool = Field(False, title="Never skip this command, even if nothing changed")
    # fmt: on

    class Config:
        title = "A single named command specified in a project config"
        extra = "forbid"


class ProjectConfigSchema(BaseModel):
    # fmt: off
    variables: Dict[StrictStr, Union[str, int, float, bool]] = Field({}, title="Optional variables to substitute in commands")
    assets: List[ProjectConfigAsset] = Field([], title="Data assets")
    workflows: Dict[StrictStr, List[StrictStr]] = Field({}, title="Named workflows, mapped to list of project commands to run in order")
    commands: List[ProjectConfigCommand] = Field([], title="Project command shortucts")
    # fmt: on

    class Config:
        title = "Schema for project configuration file"
