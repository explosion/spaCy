# coding: utf-8
import pytest
from ...attrs import ENT_IOB, ENT_TYPE
from ...tokens import Doc


@pytest.mark.xfail
@pytest.mark.models('en')
def test_issue3012(EN):
    sentence = 'This is 10%.'

    doc = EN(sentence)

    ten = doc[2]  # 10
    assert (ten.orth_, ten.orth_, ten.tag_, ten.ent_type_) == (10, 'NUM', 'CD', 'PERCENT')

    # now removing '10%' entity
    assert len(doc.ents) == 1
    header = [ENT_IOB, ENT_TYPE]
    ent_array = doc.to_array(header)
    ent = doc.ents[0]
    for idx in range(ent.start, ent.end):
        ent_array[idx, 0] = 0
        ent_array[idx, 1] = 0
    doc.from_array(header, ent_array)
    assert len(doc.ents) == 0

    # still making sure nothing changed on array() calls
    ten = doc[2]  # 10
    assert (ten.orth_, ten.orth_, ten.tag_, ten.ent_type_) == (10, 'NUM', 'CD', 'PERCENT')

    # serializing then deserializing
    bytes = doc.to_bytes()
    doc2 = Doc(EN.vocab).from_bytes(bytes)

    assert len(doc2.ents) == 0
    ten2 = doc2[2]  # 10
    assert (ten2.orth_, ten2.orth_, ten2.tag_, ten2.ent_type_) == (10, 'NUM', 'CD', 'PERCENT')
