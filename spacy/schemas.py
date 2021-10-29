from typing import Dict, List, Union, Optional, Any, Callable, Type, Tuple
from typing import Iterable, TypeVar, TYPE_CHECKING
from enum import Enum
from pydantic import BaseModel, Field, ValidationError, validator, create_model
from pydantic import StrictStr, StrictInt, StrictFloat, StrictBool
from pydantic.main import ModelMetaclass
from thinc.api import Optimizer, ConfigValidationError, Model
from thinc.config import Promise
from collections import defaultdict
import inspect

from .attrs import NAMES
from .lookups import Lookups
from .util import is_cython_func

if TYPE_CHECKING:
    # This lets us add type hints for mypy etc. without causing circular imports
    from .language import Language  # noqa: F401
    from .training import Example  # noqa: F401
    from .vocab import Vocab  # noqa: F401


# fmt: off
ItemT = TypeVar("ItemT")
Batcher = Union[Callable[[Iterable[ItemT]], Iterable[List[ItemT]]], Promise]
Reader = Union[Callable[["Language", str], Iterable["Example"]], Promise]
Logger = Union[Callable[["Language"], Tuple[Callable[[Dict[str, Any]], None], Callable]], Promise]
# fmt: on


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
        return [f"[{loc}] {', '.join(msg)}" for loc, msg in data.items()]  # type: ignore[arg-type]


# Initialization


class ArgSchemaConfig:
    extra = "forbid"
    arbitrary_types_allowed = True


class ArgSchemaConfigExtra:
    extra = "forbid"
    arbitrary_types_allowed = True


def get_arg_model(
    func: Callable,
    *,
    exclude: Iterable[str] = tuple(),
    name: str = "ArgModel",
    strict: bool = True,
) -> ModelMetaclass:
    """Generate a pydantic model for function arguments.

    func (Callable): The function to generate the schema for.
    exclude (Iterable[str]): Parameter names to ignore.
    name (str): Name of created model class.
    strict (bool): Don't allow extra arguments if no variable keyword arguments
        are allowed on the function.
    RETURNS (ModelMetaclass): A pydantic model.
    """
    sig_args = {}
    try:
        sig = inspect.signature(func)
    except ValueError:
        # Typically happens if the method is part of a Cython module without
        # binding=True. Here we just use an empty model that allows everything.
        return create_model(name, __config__=ArgSchemaConfigExtra)  # type: ignore[arg-type, return-value]
    has_variable = False
    for param in sig.parameters.values():
        if param.name in exclude:
            continue
        if param.kind == param.VAR_KEYWORD:
            # The function allows variable keyword arguments so we shouldn't
            # include **kwargs etc. in the schema and switch to non-strict
            # mode and pass through all other values
            has_variable = True
            continue
        # If no annotation is specified assume it's anything
        annotation = param.annotation if param.annotation != param.empty else Any
        # If no default value is specified assume that it's required. Cython
        # functions/methods will have param.empty for default value None so we
        # need to treat them differently
        default_empty = None if is_cython_func(func) else ...
        default = param.default if param.default != param.empty else default_empty
        sig_args[param.name] = (annotation, default)
    is_strict = strict and not has_variable
    sig_args["__config__"] = ArgSchemaConfig if is_strict else ArgSchemaConfigExtra  # type: ignore[assignment]
    return create_model(name, **sig_args)  # type: ignore[arg-type, return-value]


def validate_init_settings(
    func: Callable,
    settings: Dict[str, Any],
    *,
    section: Optional[str] = None,
    name: str = "",
    exclude: Iterable[str] = ("get_examples", "nlp"),
) -> Dict[str, Any]:
    """Validate initialization settings against the expected arguments in
    the method signature. Will parse values if possible (e.g. int to string)
    and return the updated settings dict. Will raise a ConfigValidationError
    if types don't match or required values are missing.

    func (Callable): The initialize method of a given component etc.
    settings (Dict[str, Any]): The settings from the respective [initialize] block.
    section (str): Initialize section, for error message.
    name (str): Name of the block in the section.
    exclude (Iterable[str]): Parameter names to exclude from schema.
    RETURNS (Dict[str, Any]): The validated settings.
    """
    schema = get_arg_model(func, exclude=exclude, name="InitArgModel")
    try:
        return schema(**settings).dict()
    except ValidationError as e:
        block = "initialize" if not section else f"initialize.{section}"
        title = f"Error validating initialization settings in [{block}]"
        raise ConfigValidationError(
            title=title, errors=e.errors(), config=settings, parent=name
        ) from None


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
    REGEX: Optional[StrictStr] = Field(None, alias="regex")
    IN: Optional[List[StrictStr]] = Field(None, alias="in")
    NOT_IN: Optional[List[StrictStr]] = Field(None, alias="not_in")
    IS_SUBSET: Optional[List[StrictStr]] = Field(None, alias="is_subset")
    IS_SUPERSET: Optional[List[StrictStr]] = Field(None, alias="is_superset")
    INTERSECTS: Optional[List[StrictStr]] = Field(None, alias="intersects")

    class Config:
        extra = "forbid"
        allow_population_by_field_name = True  # allow alias and field name

    @validator("*", pre=True, each_item=True, allow_reuse=True)
    def raise_for_none(cls, v):
        if v is None:
            raise ValueError("None / null is not allowed")
        return v


class TokenPatternNumber(BaseModel):
    REGEX: Optional[StrictStr] = Field(None, alias="regex")
    IN: Optional[List[StrictInt]] = Field(None, alias="in")
    NOT_IN: Optional[List[StrictInt]] = Field(None, alias="not_in")
    IS_SUBSET: Optional[List[StrictInt]] = Field(None, alias="is_subset")
    IS_SUPERSET: Optional[List[StrictInt]] = Field(None, alias="is_superset")
    INTERSECTS: Optional[List[StrictInt]] = Field(None, alias="intersects")
    EQ: Union[StrictInt, StrictFloat] = Field(None, alias="==")
    NEQ: Union[StrictInt, StrictFloat] = Field(None, alias="!=")
    GEQ: Union[StrictInt, StrictFloat] = Field(None, alias=">=")
    LEQ: Union[StrictInt, StrictFloat] = Field(None, alias="<=")
    GT: Union[StrictInt, StrictFloat] = Field(None, alias=">")
    LT: Union[StrictInt, StrictFloat] = Field(None, alias="<")

    class Config:
        extra = "forbid"
        allow_population_by_field_name = True  # allow alias and field name

    @validator("*", pre=True, each_item=True, allow_reuse=True)
    def raise_for_none(cls, v):
        if v is None:
            raise ValueError("None / null is not allowed")
        return v


class TokenPatternOperator(str, Enum):
    plus: StrictStr = StrictStr("+")
    start: StrictStr = StrictStr("*")
    question: StrictStr = StrictStr("?")
    exclamation: StrictStr = StrictStr("!")


StringValue = Union[TokenPatternString, StrictStr]
NumberValue = Union[TokenPatternNumber, StrictInt, StrictFloat]
UnderscoreValue = Union[
    TokenPatternString, TokenPatternNumber, str, int, float, list, bool
]


class TokenPattern(BaseModel):
    orth: Optional[StringValue] = None
    text: Optional[StringValue] = None
    lower: Optional[StringValue] = None
    pos: Optional[StringValue] = None
    tag: Optional[StringValue] = None
    morph: Optional[StringValue] = None
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

    @validator("*", pre=True, allow_reuse=True)
    def raise_for_none(cls, v):
        if v is None:
            raise ValueError("None / null is not allowed")
        return v


class TokenPatternSchema(BaseModel):
    pattern: List[TokenPattern] = Field(..., min_items=1)

    class Config:
        extra = "forbid"


# Model meta


class ModelMetaSchema(BaseModel):
    # fmt: off
    lang: StrictStr = Field(..., title="Two-letter language code, e.g. 'en'")
    name: StrictStr = Field(..., title="Model name")
    version: StrictStr = Field(..., title="Model version")
    spacy_version: StrictStr = Field("", title="Compatible spaCy version identifier")
    parent_package: StrictStr = Field("spacy", title="Name of parent spaCy package, e.g. spacy or spacy-nightly")
    requirements: List[StrictStr] = Field([], title="Additional Python package dependencies, used for the Python package setup")
    pipeline: List[StrictStr] = Field([], title="Names of pipeline components")
    description: StrictStr = Field("", title="Model description")
    license: StrictStr = Field("", title="Model license")
    author: StrictStr = Field("", title="Model author name")
    email: StrictStr = Field("", title="Model author email")
    url: StrictStr = Field("", title="Model author URL")
    sources: Optional[Union[List[StrictStr], List[Dict[str, str]]]] = Field(None, title="Training data sources")
    vectors: Dict[str, Any] = Field({}, title="Included word vectors")
    labels: Dict[str, List[str]] = Field({}, title="Component labels, keyed by component name")
    performance: Dict[str, Any] = Field({}, title="Accuracy and speed numbers")
    spacy_git_version: StrictStr = Field("", title="Commit of spaCy version used")
    # fmt: on


# Config schema
# We're not setting any defaults here (which is too messy) and are making all
# fields required, so we can raise validation errors for missing values. To
# provide a default, we include a separate .cfg file with all values and
# check that against this schema in the test suite to make sure it's always
# up to date.


class ConfigSchemaTraining(BaseModel):
    # fmt: off
    dev_corpus: StrictStr = Field(..., title="Path in the config to the dev data")
    train_corpus: StrictStr = Field(..., title="Path in the config to the training data")
    batcher: Batcher = Field(..., title="Batcher for the training data")
    dropout: StrictFloat = Field(..., title="Dropout rate")
    patience: StrictInt = Field(..., title="How many steps to continue without improvement in evaluation score")
    max_epochs: StrictInt = Field(..., title="Maximum number of epochs to train for")
    max_steps: StrictInt = Field(..., title="Maximum number of update steps to train for")
    eval_frequency: StrictInt = Field(..., title="How often to evaluate during training (steps)")
    seed: Optional[StrictInt] = Field(..., title="Random seed")
    gpu_allocator: Optional[StrictStr] = Field(..., title="Memory allocator when running on GPU")
    accumulate_gradient: StrictInt = Field(..., title="Whether to divide the batch up into substeps")
    score_weights: Dict[StrictStr, Optional[Union[StrictFloat, StrictInt]]] = Field(..., title="Scores to report and their weights for selecting final model")
    optimizer: Optimizer = Field(..., title="The optimizer to use")
    logger: Logger = Field(..., title="The logger to track training progress")
    frozen_components: List[str] = Field(..., title="Pipeline components that shouldn't be updated during training")
    annotating_components: List[str] = Field(..., title="Pipeline components that should set annotations during training")
    before_to_disk: Optional[Callable[["Language"], "Language"]] = Field(..., title="Optional callback to modify nlp object after training, before it's saved to disk")
    # fmt: on

    class Config:
        extra = "forbid"
        arbitrary_types_allowed = True


class ConfigSchemaNlp(BaseModel):
    # fmt: off
    lang: StrictStr = Field(..., title="The base language to use")
    pipeline: List[StrictStr] = Field(..., title="The pipeline component names in order")
    disabled: List[StrictStr] = Field(..., title="Pipeline components to disable by default")
    tokenizer: Callable = Field(..., title="The tokenizer to use")
    before_creation: Optional[Callable[[Type["Language"]], Type["Language"]]] = Field(..., title="Optional callback to modify Language class before initialization")
    after_creation: Optional[Callable[["Language"], "Language"]] = Field(..., title="Optional callback to modify nlp object after creation and before the pipeline is constructed")
    after_pipeline_creation: Optional[Callable[["Language"], "Language"]] = Field(..., title="Optional callback to modify nlp object after the pipeline is constructed")
    batch_size: Optional[int] = Field(..., title="Default batch size")
    # fmt: on

    class Config:
        extra = "forbid"
        arbitrary_types_allowed = True


class ConfigSchemaPretrainEmpty(BaseModel):
    class Config:
        extra = "forbid"


class ConfigSchemaPretrain(BaseModel):
    # fmt: off
    max_epochs: StrictInt = Field(..., title="Maximum number of epochs to train for")
    dropout: StrictFloat = Field(..., title="Dropout rate")
    n_save_every: Optional[StrictInt] = Field(..., title="Saving frequency")
    optimizer: Optimizer = Field(..., title="The optimizer to use")
    corpus: StrictStr = Field(..., title="Path in the config to the training data")
    batcher: Batcher = Field(..., title="Batcher for the training data")
    component: str = Field(..., title="Component to find the layer to pretrain")
    layer: str = Field(..., title="Layer to pretrain. Whole model if empty.")
    objective: Callable[["Vocab", Model], Model] = Field(..., title="A function that creates the pretraining objective.")
    # fmt: on

    class Config:
        extra = "forbid"
        arbitrary_types_allowed = True


class ConfigSchemaInit(BaseModel):
    # fmt: off
    vocab_data: Optional[StrictStr] = Field(..., title="Path to JSON-formatted vocabulary file")
    lookups: Optional[Lookups] = Field(..., title="Vocabulary lookups, e.g. lexeme normalization")
    vectors: Optional[StrictStr] = Field(..., title="Path to vectors")
    init_tok2vec: Optional[StrictStr] = Field(..., title="Path to pretrained tok2vec weights")
    tokenizer: Dict[StrictStr, Any] = Field(..., help="Arguments to be passed into Tokenizer.initialize")
    components: Dict[StrictStr, Dict[StrictStr, Any]] = Field(..., help="Arguments for TrainablePipe.initialize methods of pipeline components, keyed by component")
    before_init: Optional[Callable[["Language"], "Language"]] = Field(..., title="Optional callback to modify nlp object before initialization")
    after_init: Optional[Callable[["Language"], "Language"]] = Field(..., title="Optional callback to modify nlp object after initialization")
    # fmt: on

    class Config:
        extra = "forbid"
        arbitrary_types_allowed = True


class ConfigSchema(BaseModel):
    training: ConfigSchemaTraining
    nlp: ConfigSchemaNlp
    pretraining: Union[ConfigSchemaPretrain, ConfigSchemaPretrainEmpty] = {}  # type: ignore[assignment]
    components: Dict[str, Dict[str, Any]]
    corpora: Dict[str, Reader]
    initialize: ConfigSchemaInit

    class Config:
        extra = "allow"
        arbitrary_types_allowed = True


CONFIG_SCHEMAS = {
    "nlp": ConfigSchemaNlp,
    "training": ConfigSchemaTraining,
    "pretraining": ConfigSchemaPretrain,
    "initialize": ConfigSchemaInit,
}


# Project config Schema


class ProjectConfigAssetGitItem(BaseModel):
    # fmt: off
    repo: StrictStr = Field(..., title="URL of Git repo to download from")
    path: StrictStr = Field(..., title="File path or sub-directory to download (used for sparse checkout)")
    branch: StrictStr = Field("master", title="Branch to clone from")
    # fmt: on


class ProjectConfigAssetURL(BaseModel):
    # fmt: off
    dest: StrictStr = Field(..., title="Destination of downloaded asset")
    url: Optional[StrictStr] = Field(None, title="URL of asset")
    checksum: str = Field(None, title="MD5 hash of file", regex=r"([a-fA-F\d]{32})")
    description: StrictStr = Field("", title="Description of asset")
    # fmt: on


class ProjectConfigAssetGit(BaseModel):
    # fmt: off
    git: ProjectConfigAssetGitItem = Field(..., title="Git repo information")
    checksum: str = Field(None, title="MD5 hash of file", regex=r"([a-fA-F\d]{32})")
    description: Optional[StrictStr] = Field(None, title="Description of asset")
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
    vars: Dict[StrictStr, Any] = Field({}, title="Optional variables to substitute in commands")
    env: Dict[StrictStr, Any] = Field({}, title="Optional variable names to substitute in commands, mapped to environment variable names")
    assets: List[Union[ProjectConfigAssetURL, ProjectConfigAssetGit]] = Field([], title="Data assets")
    workflows: Dict[StrictStr, List[StrictStr]] = Field({}, title="Named workflows, mapped to list of project commands to run in order")
    commands: List[ProjectConfigCommand] = Field([], title="Project command shortucts")
    title: Optional[str] = Field(None, title="Project title")
    spacy_version: Optional[StrictStr] = Field(None, title="spaCy version range that the project is compatible with")
    # fmt: on

    class Config:
        title = "Schema for project configuration file"


# Recommendations for init config workflows


class RecommendationTrfItem(BaseModel):
    name: str
    size_factor: int


class RecommendationTrf(BaseModel):
    efficiency: RecommendationTrfItem
    accuracy: RecommendationTrfItem


class RecommendationSchema(BaseModel):
    word_vectors: Optional[str] = None
    transformer: Optional[RecommendationTrf] = None
    has_letters: bool = True
