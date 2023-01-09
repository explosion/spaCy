from spacy.morphology import Morphology


def test_feats_converters():
    feats = "Case=dat,gen|Number=sing"
    feats_dict = {"Case": "dat,gen", "Number": "sing"}

    # simple conversions
    assert Morphology.dict_to_feats(feats_dict) == feats
    assert Morphology.feats_to_dict(feats) == feats_dict

    # roundtrips
    assert Morphology.dict_to_feats(Morphology.feats_to_dict(feats)) == feats
    assert Morphology.feats_to_dict(Morphology.dict_to_feats(feats_dict)) == feats_dict

    # unsorted input is normalized
    unsorted_feats = "Number=sing|Case=gen,dat"
    unsorted_feats_dict = {"Case": "gen,dat", "Number": "sing"}
    assert Morphology.feats_to_dict(unsorted_feats) == feats_dict
    assert Morphology.dict_to_feats(unsorted_feats_dict) == feats
    assert Morphology.dict_to_feats(Morphology.feats_to_dict(unsorted_feats)) == feats
