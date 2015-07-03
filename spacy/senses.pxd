# Enum of Wordnet supersenses
cimport parts_of_speech
from .typedefs cimport flags_t

cpdef enum:
    NO_SENSE
    N_act
    N_animal
    N_artifact
    N_attribute
    N_body
    N_cognition
    N_communication
    N_event
    N_feeling
    N_food
    N_group
    N_location
    N_motive
    N_object
    N_person
    N_phenomenon
    N_plant
    N_possession
    N_process
    N_quantity
    N_relation
    N_shape
    N_state
    N_substance
    N_time
    V_body
    V_change
    V_cognition
    V_communication
    V_competition
    V_consumption
    V_contact
    V_creation
    V_emotion
    V_motion
    V_perception
    V_possession
    V_social
    V_stative
    V_weather
    N_SENSES


cdef flags_t[<int>parts_of_speech.N_UNIV_TAGS] POS_SENSES


cdef flags_t encode_sense_strs(sense_names) except 0
