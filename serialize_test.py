import srsly
from timeit import Timer

MSGPACK_SERIALIZED_EMPTY_LIST = srsly.msgpack_dumps([])


def return_empty_list():
    return []


def serialize_empty_list():
    return srsly.msgpack_dumps([])


def serialize_empty_list_known():
    return MSGPACK_SERIALIZED_EMPTY_LIST


def deserialize_empty_list():
    return srsly.msgpack_loads(MSGPACK_SERIALIZED_EMPTY_LIST)


def serialization_round_trip():
    return srsly.msgpack_loads(srsly.msgpack_dumps([]))


assert deserialize_empty_list() == return_empty_list()
assert serialize_empty_list() == serialize_empty_list_known()
assert serialization_round_trip() == return_empty_list()


print("return_empty_list()",min(Timer("return_empty_list()", globals=globals()).repeat()))
print("serialize_empty_list_known()",min(Timer("serialize_empty_list_known()", globals=globals()).repeat()))
print("serialize_empty_list()",min(Timer("serialize_empty_list()", globals=globals()).repeat()))
print("deserialize_empty_list()",min(Timer("deserialize_empty_list()", globals=globals()).repeat()))
print("serialization_round_trip()",min(Timer("serialization_round_trip()", globals=globals()).repeat()))
