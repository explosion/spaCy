from __future__ import unicode_literals
cimport parts_of_speech


lexnames_str = """
-1      NO_SENSE       -1
00      J_all 3
01      A_pert        3 
02      A_all 4
03      N_Tops       1  
04      N_act        1
05      N_animal     1
06      N_artifact   1
07      N_attribute  1
08      N_body       1
09      N_cognition  1
10      N_communication      1
11      N_event      1
12      N_feeling    1
13      N_food       1
14      N_group      1
15      N_location   1
16      N_motive     1
17      N_object     1
18      N_person     1
19      N_phenomenon 1
20      N_plant      1
21      N_possession 1
22      N_process    1
23      N_quantity   1
24      N_relation   1
25      N_shape      1
26      N_state      1
27      N_substance  1
28      N_time       1
29      V_body       2
30      V_change     2
31      V_cognition  2
32      V_communication      2
33      V_competition        2
34      V_consumption        2
35      V_contact    2
36      V_creation   2
37      V_emotion    2
38      V_motion     2
39      V_perception 2
40      V_possession 2
41      V_social     2
42      V_stative    2
43      V_weather    2
44      A_ppl 3
""".strip()

STRINGS = tuple(line.split()[1] for line in lexnames_str.split('\n'))

IDS = dict((sense_str, i) for i, sense_str in enumerate(STRINGS))


cdef flags_t encode_sense_strs(sense_names) except 0:
    cdef flags_t sense_bits = 0
    if len(sense_names) == 0:
        return sense_bits | (1 << NO_SENSE)
    cdef flags_t sense_id = 0
    for sense_str in sense_names:
        sense_str = sense_str.replace('noun', 'N').replace('verb', 'V')
        sense_str = sense_str.replace('adj', 'J').replace('adv', 'A')
        sense_id = IDS[sense_str]
        sense_bits |= (1 << sense_id)
    return sense_bits
