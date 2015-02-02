from thinc.typedefs cimport class_t


cdef struct Entity:
    int start
    int end
    int label


cdef struct State:
    Entity curr
    Entity* ents
    int* tags
    int i
    int j
    int length


cdef struct Move:
    class_t clas
    int action
    int label
    bint accept
