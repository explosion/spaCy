from ..errors import Errors
from ..language import Language
from ..util import load_model, registry


@registry.callbacks("spacy.copy_from_base_model.v1")
def create_copy_from_base_model(
    base_model: str,
    tokenizer: bool = True,
    vocab: bool = True,
) -> Language:
    def copy_from_base_model(nlp):
        base_nlp = load_model(base_model)
        if tokenizer:
            if nlp.config["nlp"]["tokenizer"] == base_nlp.config["nlp"]["tokenizer"]:
                nlp.tokenizer.from_bytes(base_nlp.tokenizer.to_bytes())
            else:
                raise ValueError(Errors.E872.format(curr_config=nlp.config["nlp"]["tokenizer"], base_config=base_nlp.config["nlp"]["tokenizer"]))
        if vocab:
            nlp.vocab.from_bytes(base_nlp.vocab.to_bytes())

    return copy_from_base_model
