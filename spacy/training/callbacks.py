from typing import TYPE_CHECKING, Callable, Optional

from ..errors import Errors
from ..util import load_model, logger, registry

if TYPE_CHECKING:
    from ..language import Language


def create_copy_from_base_model(
    tokenizer: Optional[str] = None,
    vocab: Optional[str] = None,
) -> Callable[["Language"], "Language"]:
    def copy_from_base_model(nlp):
        if tokenizer:
            logger.info("Copying tokenizer from: %s", tokenizer)
            base_nlp = load_model(tokenizer)
            if nlp.config["nlp"]["tokenizer"] == base_nlp.config["nlp"]["tokenizer"]:
                nlp.tokenizer.from_bytes(base_nlp.tokenizer.to_bytes(exclude=["vocab"]))
            else:
                raise ValueError(
                    Errors.E872.format(
                        curr_config=nlp.config["nlp"]["tokenizer"],
                        base_config=base_nlp.config["nlp"]["tokenizer"],
                    )
                )
        if vocab:
            logger.info("Copying vocab from: %s", vocab)
            # only reload if the vocab is from a different model
            if tokenizer != vocab:
                base_nlp = load_model(vocab)
            nlp.vocab.from_bytes(base_nlp.vocab.to_bytes())

    return copy_from_base_model
