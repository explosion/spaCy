# cython: profile=True
# cython: embedsignature=True


cdef int set_morph_from_dict(Morphology* morph, dict props) except -1:
    morph.number = props.get('number', 0)
    morph.tenspect = props.get('tenspect', 0)
    morph.mood = props.get('mood', 0)
    morph.gender = props.get('gender', 0)
    morph.person = props.get('person', 0)
    morph.case = props.get('case', 0)
    morph.misc = props.get('misc', 0)
