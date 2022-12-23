from pathlib import Path
import re
from wasabi import msg
import typer

import spacy
from spacy.language import Language

from ._util import configure_cli, Arg, Opt

# These are the architectures that are recognized as tok2vec/feature sources.
TOK2VEC_ARCHS = [("spacy", "Tok2Vec"), ("spacy-transformers", "TransformerModel")]
# These are the listeners.
LISTENER_ARCHS = [
    ("spacy", "Tok2VecListener"),
    ("spacy-transformers", "TransformerListener"),
]


def _deep_get(obj, key, default):
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


def _get_tok2vecs(config):
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


def _has_listener(nlp, pipe_name):
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


def _get_listeners(nlp):
    """Get the name of every component that contains a listener.

    Does not check that they listen to the same thing; assumes a pipeline has
    only one feature source.
    """
    out = []
    for name in nlp.pipe_names:
        if _has_listener(nlp, name):
            out.append(name)
    return out


def _increment_suffix(name):
    """Given a name, return an incremented version.

    If no numeric suffix is found, return the original with "2" appended.

    This is used to avoid name collisions in pipelines.
    """

    res = re.search(r"\d+$", name)
    if res is None:
        return f"{name}2"
    else:
        num = res.match
        prefix = name[0 : -len(num)]
        return f"{prefix}{int(num) + 1}"


def _check_single_tok2vec(name, config):
    """Check if there is just one tok2vec in a config.

    A very simple check, but used in multiple functions.
    """
    tok2vecs = _get_tok2vecs(config)
    fail_msg = f"""
        Can't handle pipelines with more than one feature source, 
        but {name} has {len(tok2vecs)}."""
    if len(tok2vecs) > 1:
        msg.fail(fail_msg, exits=1)


def _check_pipeline_names(nlp, nlp2):
    """Given two pipelines, try to rename any collisions in component names.

    If a simple increment of a numeric suffix doesn't work, will give up.
    """

    fail_msg = """
        Tried automatically renaming {name} to {new_name}, but still
        had a collision, so bailing out. Please make your pipe names
        more unique.
        """

    # map of components to be renamed
    rename = {}
    # check pipeline names
    names = nlp.pipe_names
    for name in nlp2.pipe_names:
        if name in names:
            inc = _increment_suffix(name)
            # TODO Would it be better to just keep incrementing?
            if inc in names or inc in nlp2.pipe_names:
                msg.fail(fail_msg.format(name=name, new_name=inc), exits=1)
            rename[name] = inc
    return rename


@configure_cli.command("resume")
def configure_resume_cli(
    # fmt: off
    base_model: Path = Arg(..., help="Path or name of base model to use for config"),
    output_path: Path = Arg(..., help="File to save the config to or - for stdout (will only output config and no additional logging info)", allow_dash=True),
    # fmt: on
):
    """Create a config for resuming training.

    A config for resuming training is the same as the input config, but with
    all components sourced.
    """

    nlp = spacy.load(base_model)
    conf = nlp.config

    # Paths are not JSON serializable
    path_str = str(base_model)

    for comp in nlp.pipe_names:
        conf["components"][comp] = {"source": path_str}

    if str(output_path) == "-":
        print(conf.to_str())
    else:
        conf.to_disk(output_path)
        msg.good("Saved config", output_path)

    return conf


@configure_cli.command("transformer")
def use_transformer(
    base_model: str, output_path: Path, transformer_name: str = "roberta-base"
):
    """Replace pipeline tok2vec with transformer."""

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
    trf = nlp.add_pipe("transformer", config=trf_config, first=True)

    # TODO maybe remove vectors?

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

    if str(output_path) == "-":
        print(nlp.config.to_str())
    else:
        nlp.config.to_disk(output_path)
        msg.good("Saved config", output_path)

    return nlp.config


@configure_cli.command("tok2vec")
def use_tok2vec(base_model: str, output_path: Path) -> Language:
    """Replace pipeline tok2vec with CNN tok2vec."""
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

    if str(output_path) == "-":
        print(nlp.config.to_str())
    else:
        nlp.config.to_disk(output_path)
        msg.good("Saved config", output_path)

    return nlp.config


def _inner_merge(nlp, nlp2, replace_listeners=False) -> Language:
    """Actually do the merge.

    nlp: Base pipeline to add components to.
    nlp2: Pipeline to add components from.
    replace_listeners (bool): Whether to replace listeners. Usually only true
      if there's one listener.
    returns: assembled pipeline.
    """

    # we checked earlier, so there's definitely just one
    tok2vec_name = _get_tok2vecs(nlp2.config)[0]
    rename = _check_pipeline_names(nlp, nlp2)

    if len(_get_listeners(nlp2)) > 1:
        if replace_listeners:
            msg.warn(
                """
                Replacing listeners for multiple components. Note this can make
                your pipeline large and slow. Consider chaining pipelines (like
                nlp2(nlp(text))) instead.
                """
            )
        else:
            # TODO provide a guide for what to do here
            msg.warn(
                """
                The result of this merge will have two feature sources
                (tok2vecs) and multiple listeners. This will work for
                inference, but will probably not work when training without
                extra adjustment. If you continue to train the pipelines
                separately this is not a problem.
                """
            )

    for comp in nlp2.pipe_names:
        if replace_listeners and comp == tok2vec_name:
            # the tok2vec should not be copied over
            continue
        if replace_listeners and _has_listener(nlp2, comp):
            # TODO does "model.tok2vec" work for everything?
            nlp2.replace_listeners(tok2vec_name, comp, ["model.tok2vec"])
        nlp.add_pipe(comp, source=nlp2, name=rename.get(comp, comp))
        if comp in rename:
            msg.info(f"Renaming {comp} to {rename[comp]} to avoid collision...")
    return nlp


@configure_cli.command("merge")
def merge_pipelines(base_model: str, added_model: str, output_path: Path) -> Language:
    """Combine components from multiple pipelines."""
    nlp = spacy.load(base_model)
    nlp2 = spacy.load(added_model)

    # to merge models:
    # - lang must be the same
    # - vectors must be the same
    # - vocabs must be the same (how to check?)
    # - tokenizer must be the same (only partially checkable)
    if nlp.lang != nlp2.lang:
        msg.fail("Can't merge - languages don't match", exits=1)

    # check vector equality
    if (
        nlp.vocab.vectors.shape != nlp2.vocab.vectors.shape
        or nlp.vocab.vectors.key2row != nlp2.vocab.vectors.key2row
        or nlp.vocab.vectors.to_bytes(exclude=["strings"])
        != nlp2.vocab.vectors.to_bytes(exclude=["strings"])
    ):
        msg.fail("Can't merge - vectors don't match", exits=1)

    if nlp.config["nlp"]["tokenizer"] != nlp2.config["nlp"]["tokenizer"]:
        msg.fail("Can't merge - tokenizers don't match", exits=1)

    # Check that each pipeline only has one feature source
    _check_single_tok2vec(base_model, nlp.config)
    _check_single_tok2vec(added_model, nlp2.config)

    # Check how many listeners there are and replace based on that
    # TODO: option to recognize frozen tok2vecs
    # TODO: take list of pipe names to copy
    listeners = _get_listeners(nlp2)
    replace_listeners = len(listeners) == 1
    print(replace_listeners, len(listeners))
    nlp_out = _inner_merge(nlp, nlp2, replace_listeners=replace_listeners)

    # write the final pipeline
    nlp.to_disk(output_path)
    msg.info(f"Saved pipeline to: {output_path}")

    return nlp
