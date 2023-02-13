from pathlib import Path
from wasabi import msg
import typer
from thinc.api import Config
from typing import Any, Dict, Iterable, List, Union

import spacy
from spacy.language import Language

from ._util import configure_cli, Arg, Opt

# These are the architectures that are recognized as tok2vec/feature sources.
TOK2VEC_ARCHS = [
    ("spacy", "Tok2Vec"),
    ("spacy", "HashEmbedCNN"),
    ("spacy-transformers", "TransformerModel"),
]
# These are the listeners.
LISTENER_ARCHS = [
    ("spacy", "Tok2VecListener"),
    ("spacy-transformers", "TransformerListener"),
]


def _deep_get(
    obj: Union[Dict[str, Any], Config], key: Iterable[str], default: Any
) -> Any:
    """Given a multi-part key, try to get the key. If at any point this isn't
    possible, return the default.
    """
    out = None
    slot = obj
    for notch in key:
        if slot is None or notch not in slot:
            return default
        slot = slot[notch]
    return slot


def _get_tok2vecs(config: Config) -> List[str]:
    """Given a pipeline config, return the names of components that are
    tok2vecs (or Transformers).
    """
    out = []
    for name, comp in config["components"].items():
        arch = _deep_get(comp, ("model", "@architectures"), False)
        if not arch:
            continue

        ns, model, ver = arch.split(".")
        if (ns, model) in TOK2VEC_ARCHS:
            out.append(name)
    return out


def _has_listener(nlp: Language, pipe_name: str):
    """Given a pipeline and a component name, check if it has a listener."""
    arch = _deep_get(
        nlp.config,
        ("components", pipe_name, "model", "tok2vec", "@architectures"),
        False,
    )
    if not arch:
        return False
    ns, model, ver = arch.split(".")
    return (ns, model) in LISTENER_ARCHS


def _get_listeners(nlp: Language) -> List[str]:
    """Get the name of every component that contains a listener.

    Does not check that they listen to the same thing; assumes a pipeline has
    only one feature source.
    """
    out = []
    for name in nlp.pipe_names:
        if _has_listener(nlp, name):
            out.append(name)
    return out


def _check_single_tok2vec(name: str, config: Config) -> None:
    """Check if there is just one tok2vec in a config.

    A very simple check, but used in multiple functions.
    """
    tok2vecs = _get_tok2vecs(config)
    fail_msg = f"""
        Can't handle pipelines with more than one feature source, 
        but {name} has {len(tok2vecs)}."""
    if len(tok2vecs) > 1:
        msg.fail(fail_msg, exits=1)


@configure_cli.command("resume")
def configure_resume_cli(
    # fmt: off
    base_model: Path = Arg(..., help="Path or name of base model to use for config"),
    output_file: Path = Arg(..., help="File to save the config to or - for stdout (will only output config and no additional logging info)", allow_dash=True),
    # fmt: on
) -> Config:
    """Create a config for resuming training.

    A config for resuming training is the same as the input config, but with
    all components sourced.

    DOCS: https://spacy.io/api/cli#configure-resume
    """

    nlp = spacy.load(base_model)
    conf = nlp.config

    # Paths are not JSON serializable
    path_str = str(base_model)

    for comp in nlp.pipe_names:
        conf["components"][comp] = {"source": path_str}

    if str(output_file) == "-":
        print(conf.to_str())
    else:
        conf.to_disk(output_file)
        msg.good("Saved config", output_file)

    return conf


@configure_cli.command("transformer")
def use_transformer(
    base_model: str, output_file: Path, transformer_name: str = "roberta-base"
) -> Config:
    """Replace pipeline tok2vec with transformer.

    DOCS: https://spacy.io/api/cli#configure-transformer
    """

    # 1. identify tok2vec
    # 2. replace tok2vec
    # 3. replace listeners
    nlp = spacy.load(base_model)
    _check_single_tok2vec(base_model, nlp.config)

    tok2vecs = _get_tok2vecs(nlp.config)
    assert len(tok2vecs) > 0, "Must have tok2vec to replace!"

    nlp.remove_pipe(tok2vecs[0])
    # the rest can be default values
    trf_config = {
        "model": {
            "name": transformer_name,
        }
    }
    try:
        trf = nlp.add_pipe("transformer", config=trf_config, first=True)
    except ValueError:
        fail_msg = (
            "Configuring a transformer requires spacy-transformers. "
            "Install with: pip install spacy-transformers"
        )
        msg.fail(fail_msg, exits=1)

    # now update the listeners
    listeners = _get_listeners(nlp)
    for listener in listeners:
        listener_config = {
            "@architectures": "spacy-transformers.TransformerListener.v1",
            "grad_factor": 1.0,
            "upstream": "transformer",
            "pooling": {"@layers": "reduce_mean.v1"},
        }
        nlp.config["components"][listener]["model"]["tok2vec"] = listener_config

    if str(output_file) == "-":
        print(nlp.config.to_str())
    else:
        nlp.config.to_disk(output_file)
        msg.good("Saved config", output_file)

    return nlp.config


@configure_cli.command("tok2vec")
def use_tok2vec(base_model: str, output_file: Path) -> Config:
    """Replace pipeline tok2vec with CNN tok2vec.

    DOCS: https://spacy.io/api/cli#configure-tok2vec
    """
    nlp = spacy.load(base_model)
    _check_single_tok2vec(base_model, nlp.config)

    tok2vecs = _get_tok2vecs(nlp.config)
    assert len(tok2vecs) > 0, "Must have tok2vec to replace!"

    nlp.remove_pipe(tok2vecs[0])

    tok2vec = nlp.add_pipe("tok2vec", first=True)
    width = "${components.tok2vec.model.encode:width}"

    listeners = _get_listeners(nlp)
    for listener in listeners:
        listener_config = {
            "@architectures": "spacy.Tok2VecListener.v1",
            "width": width,
            "upstream": "tok2vec",
        }
        nlp.config["components"][listener]["model"]["tok2vec"] = listener_config

    if str(output_file) == "-":
        print(nlp.config.to_str())
    else:
        nlp.config.to_disk(output_file)
        msg.good("Saved config", output_file)

    return nlp.config
