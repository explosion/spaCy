from typing import List, Union, Callable, Tuple
from thinc.types import Ints2d
from thinc.api import Model, registry

from ..tokens import Doc


@registry.layers("spacy.FeatureExtractor.v1")
def FeatureExtractor(columns: List[Union[int, str]]) -> Model[List[Doc], List[Ints2d]]:
    return Model("extract_features", forward, attrs={"columns": columns})


def forward(
    model: Model[List[Doc], List[Ints2d]], docs, is_train: bool
) -> Tuple[List[Ints2d], Callable]:
    columns = model.attrs["columns"]
    features: List[Ints2d] = []
    for doc in docs:
        if hasattr(doc, "to_array"):
            attrs = doc.to_array(columns)
        else:
            attrs = doc.doc.to_array(columns)[doc.start : doc.end]
        if attrs.ndim == 1:
            attrs = attrs.reshape((attrs.shape[0], 1))
        features.append(model.ops.asarray2i(attrs, dtype="uint64"))

    backprop: Callable[[List[Ints2d]], List] = lambda d_features: []
    return features, backprop
