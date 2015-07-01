from __future__ import unicode_literals
cimport parts_of_speech


POS_SENSES[<int>parts_of_speech.NO_TAG] = 0
POS_SENSES[<int>parts_of_speech.ADJ] = 0
POS_SENSES[<int>parts_of_speech.ADV] = 0
POS_SENSES[<int>parts_of_speech.ADP] = 0
POS_SENSES[<int>parts_of_speech.CONJ] = 0
POS_SENSES[<int>parts_of_speech.DET] = 0
POS_SENSES[<int>parts_of_speech.NOUN] = 0
POS_SENSES[<int>parts_of_speech.NUM] = 0
POS_SENSES[<int>parts_of_speech.PRON] = 0
POS_SENSES[<int>parts_of_speech.PRT] = 0
POS_SENSES[<int>parts_of_speech.VERB] = 0
POS_SENSES[<int>parts_of_speech.X] = 0
POS_SENSES[<int>parts_of_speech.PUNCT] = 0
POS_SENSES[<int>parts_of_speech.EOL] = 0


cdef int _sense = 0

for _sense in range(A_behavior, N_act):
    POS_SENSES[<int>parts_of_speech.ADJ] |= 1 << _sense

for _sense in range(N_act, V_body):
    POS_SENSES[<int>parts_of_speech.NOUN] |= 1 << _sense

for _sense in range(V_body, V_weather+1):
    POS_SENSES[<int>parts_of_speech.VERB] |= 1 << _sense



STRINGS = (
    'A_behavior',
    'A_body',
    'A_feeling',
    'A_mind',
    'A_motion',
    'A_perception',
    'A_quantity',
    'A_relation',
    'A_social',
    'A_spatial',
    'A_substance',
    'A_time',
    'A_weather',
    'N_act',
    'N_animal',
    'N_artifact',
    'N_attribute',
    'N_body',
    'N_cognition',
    'N_communication',
    'N_event',
    'N_feeling',
    'N_food',
    'N_group',
    'N_location',
    'N_motive',
    'N_object',
    'N_person',
    'N_phenomenon',
    'N_plant',
    'N_possession',
    'N_process',
    'N_quantity',
    'N_relation',
    'N_shape',
    'N_state',
    'N_substance',
    'N_time',
    'V_body',
    'V_change',
    'V_cognition',
    'V_communication',
    'V_competition',
    'V_consumption',
    'V_contact',
    'V_creation',
    'V_emotion',
    'V_motion',
    'V_perception',
    'V_possession',
    'V_social',
    'V_stative',
    'V_weather'
)
