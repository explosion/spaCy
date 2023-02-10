from pathlib import Path
import re
from wasabi import msg

import spacy
from spacy.language import Language

from ._util import app, Arg, Opt, Dict
from .configure import _check_single_tok2vec, _get_listeners, _get_tok2vecs
from .configure import _has_listener


def _increment_suffix(name: str) -> str:
    """Given a name, return an incremented version.

    If no numeric suffix is found, return the original with "2" appended.

    This is used to avoid name collisions in pipelines.
    """

    res = re.search(r"\d+$", name)
    if res is None:
        return f"{name}2"
    else:
        num = res.group()
        prefix = name[0 : -len(num)]
        return f"{prefix}{int(num) + 1}"


def _make_unique_pipe_names(nlp: Language, nlp2: Language) -> Dict[str, str]:
    """Given two pipelines, try to rename any collisions in component names.

    If a simple increment of a numeric suffix doesn't work, will give up.
    """

    fail_msg = """
        Tried automatically renaming {name} to {new_name}, but still
        had a collision, so bailing out. Please make your pipe names
        unique.
        """

    # map of components to be renamed
    rename = {}
    # check pipeline names
    names = nlp.pipe_names
    for name in nlp2.pipe_names:
        if name in names:
            inc = _increment_suffix(name)
            if inc in names or inc in nlp2.pipe_names:
                msg.fail(fail_msg.format(name=name, new_name=inc), exits=1)
            rename[name] = inc
    return rename


def _inner_merge(
    nlp: Language, nlp2: Language, replace_listeners: bool = False
) -> Language:
    """Actually do the merge.

    nlp (Language): Base pipeline to add components to.
    nlp2 (Language): Pipeline to add components from.
    replace_listeners (bool): Whether to replace listeners. Usually only true
      if there's one listener.
    returns: assembled pipeline.
    """

    # The outer merge already verified there was exactly one tok2vec
    tok2vec_name = _get_tok2vecs(nlp2.config)[0]
    rename = _make_unique_pipe_names(nlp, nlp2)

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
            nlp2.replace_listeners(tok2vec_name, comp, ["model.tok2vec"])
        nlp.add_pipe(comp, source=nlp2, name=rename.get(comp, comp))
        if comp in rename:
            msg.info(f"Renaming {comp} to {rename[comp]} to avoid collision...")
    return nlp


@app.command("merge")
def merge_pipelines(
    # fmt: off
    base_model: str = Arg(..., help="Name or path of base model"),
    added_model: str = Arg(..., help="Name or path of model to be merged"), 
    output_file: Path = Arg(..., help="Path to save merged model")
    # fmt: on
) -> Language:
    """Combine components from multiple pipelines.

    Given two pipelines, the components from them are merged into a single
    pipeline. The exact way this works depends on whether the second pipeline
    has one listener or more than one listener. In the single listener case
    `replace_listeners` is used, otherwise components are simply appended to
    the base pipeline.

    DOCS: https://spacy.io/api/cli#merge
    """
    nlp = spacy.load(base_model)
    nlp2 = spacy.load(added_model)

    # to merge models:
    # - lang must be the same
    # - vectors must be the same
    # - vocabs must be the same
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
    # TODO: take list of pipe names to copy, ignore others
    listeners = _get_listeners(nlp2)
    replace_listeners = len(listeners) == 1
    nlp_out = _inner_merge(nlp, nlp2, replace_listeners=replace_listeners)

    # write the final pipeline
    nlp.to_disk(output_file)
    msg.info(f"Saved pipeline to: {output_file}")

    return nlp
