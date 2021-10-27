from typing import Callable, Optional
from ..errors import Errors
from ..language import Language
from ..util import load_model, registry, logger


@registry.callbacks("spacy.copy_from_base_model.v1")
def create_copy_from_base_model(
    tokenizer: Optional[str] = None,
    vocab: Optional[str] = None,
) -> Callable[[Language], Language]:
    def copy_from_base_model(nlp):
        if tokenizer:
            logger.info(f"Copying tokenizer from: {tokenizer}")
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
            logger.info(f"Copying vocab from: {vocab}")
            # only reload if the vocab is from a different model
            if tokenizer != vocab:
                base_nlp = load_model(vocab)
            nlp.vocab.from_bytes(base_nlp.vocab.to_bytes())

    return copy_from_base_model
