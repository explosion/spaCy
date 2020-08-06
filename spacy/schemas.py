from typing import Dict, List, Union, Optional, Sequence, Any, Callable, Type
from typing import Iterable, TypeVar, TYPE_CHECKING
from enum import Enum
from pydantic import BaseModel, Field, ValidationError, validator
from pydantic import StrictStr, StrictInt, StrictFloat, StrictBool
from pydantic import root_validator
from collections import defaultdict
from thinc.api import Optimizer

from .attrs import NAMES

if TYPE_CHECKING:
    # This lets us add type hints for mypy etc. without causing circular imports
    from .language import Language  # noqa: F401
    from .gold import Example  # noqa: F401


ItemT = TypeVar("ItemT")
Batcher = Callable[[Iterable[ItemT]], Iterable[List[ItemT]]]
Reader = Callable[["Language", str], Iterable["Example"]]


def validate(schema: Type[BaseModel], obj: Dict[str, Any]) -> List[str]:
    """Validate data against a given pydantic schema.

    obj (Dict[str, Any]): JSON-serializable data to validate.
    schema (pydantic.BaseModel): The schema to validate against.
    RETURNS (List[str]): A list of error messages, if available.
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


def validate_token_pattern(obj: list) -> List[str]:
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

    @validator("*", pre=True, each_item=True)
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

    @validator("*", pre=True, each_item=True)
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


# Config schema
# We're not setting any defaults here (which is too messy) and are making all
# fields required, so we can raise validation errors for missing values. To
# provide a default, we include a separate .cfg file with all values and
# check that against this schema in the test suite to make sure it's always
# up to date.


class ConfigSchemaTraining(BaseModel):
    # fmt: off
    vectors: Optional[StrictStr] = Field(..., title="Path to vectors")
    train_corpus: Reader = Field(..., title="Reader for the training data")
    dev_corpus: Reader = Field(..., title="Reader for the dev data")
    batcher: Batcher = Field(..., title="Batcher for the training data")
    dropout: StrictFloat = Field(..., title="Dropout rate")
    patience: StrictInt = Field(..., title="How many steps to continue without improvement in evaluation score")
    max_epochs: StrictInt = Field(..., title="Maximum number of epochs to train for")
    max_steps: StrictInt = Field(..., title="Maximum number of update steps to train for")
    eval_frequency: StrictInt = Field(..., title="How often to evaluate during training (steps)")
    seed: Optional[StrictInt] = Field(..., title="Random seed")
    accumulate_gradient: StrictInt = Field(..., title="Whether to divide the batch up into substeps")
    score_weights: Dict[StrictStr, Union[StrictFloat, StrictInt]] = Field(..., title="Scores to report and their weights for selecting final model")
    init_tok2vec: Optional[StrictStr] = Field(..., title="Path to pretrained tok2vec weights")
    raw_text: Optional[StrictStr] = Field(default=None, title="Raw text")
    optimizer: Optimizer = Field(..., title="The optimizer to use")
    frozen_components: List[str] = Field(..., title="Pipeline components that shouldn't be updated during training")
    # fmt: on

    class Config:
        extra = "forbid"
        arbitrary_types_allowed = True


class ConfigSchemaNlp(BaseModel):
    # fmt: off
    lang: StrictStr = Field(..., title="The base language to use")
    pipeline: List[StrictStr] = Field(..., title="The pipeline component names in order")
    tokenizer: Callable = Field(..., title="The tokenizer to use")
    load_vocab_data: StrictBool = Field(..., title="Whether to load additional vocab data from spacy-lookups-data")
    before_creation: Optional[Callable[[Type["Language"]], Type["Language"]]] = Field(..., title="Optional callback to modify Language class before initialization")
    after_creation: Optional[Callable[["Language"], "Language"]] = Field(..., title="Optional callback to modify nlp object after creation and before the pipeline is constructed")
    after_pipeline_creation: Optional[Callable[["Language"], "Language"]] = Field(..., title="Optional callback to modify nlp object after the pipeline is constructed")
    # fmt: on

    class Config:
        extra = "forbid"
        arbitrary_types_allowed = True


class ConfigSchemaPretrain(BaseModel):
    # fmt: off
    max_epochs: StrictInt = Field(..., title="Maximum number of epochs to train for")
    min_length: StrictInt = Field(..., title="Minimum length of examples")
    max_length: StrictInt = Field(..., title="Maximum length of examples")
    dropout: StrictFloat = Field(..., title="Dropout rate")
    n_save_every: Optional[StrictInt] = Field(..., title="Saving frequency")
    batch_size: Union[Sequence[int], int] = Field(..., title="The batch size or batch size schedule")
    seed: Optional[StrictInt] = Field(..., title="Random seed")
    use_pytorch_for_gpu_memory: StrictBool = Field(..., title="Allocate memory via PyTorch")
    tok2vec_model: StrictStr = Field(..., title="tok2vec model in config, e.g. components.tok2vec.model")
    optimizer: Optimizer = Field(..., title="The optimizer to use")
    # TODO: use a more detailed schema for this?
    objective: Dict[str, Any] = Field(..., title="Pretraining objective")
    # fmt: on

    class Config:
        extra = "forbid"
        arbitrary_types_allowed = True


class ConfigSchema(BaseModel):
    training: ConfigSchemaTraining
    nlp: ConfigSchemaNlp
    pretraining: Optional[ConfigSchemaPretrain]
    components: Dict[str, Dict[str, Any]]

    @root_validator
    def validate_config(cls, values):
        """Perform additional validation for settings with dependencies."""
        pt = values.get("pretraining")
        if pt and pt.objective.get("type") == "vectors" and not values["nlp"].vectors:
            err = "Need nlp.vectors if pretraining.objective.type is vectors"
            raise ValueError(err)
        return values

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
