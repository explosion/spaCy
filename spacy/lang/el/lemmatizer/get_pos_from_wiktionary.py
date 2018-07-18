# coding: utf8
import re
import pickle

from gensim.corpora.wikicorpus import extract_pages

regex = re.compile(r'==={{(\w+)\|el}}===')
regex2 = re.compile(r'==={{(\w+ \w+)\|el}}===')

# get words based on the Wiktionary dump
# check only for specific parts

# ==={{κύριο όνομα|el}}===
expected_parts = ['μετοχή', 'ρήμα', 'επίθετο',
                  'επίρρημα',  'ουσιαστικό', 'κύριο όνομα', 'άρθρο']

unwanted_parts = '''
    {'αναγραμματισμοί': 2, 'σύνδεσμος': 94, 'απαρέμφατο': 1, 'μορφή άρθρου': 1, 'ένθημα': 1, 'μερική συνωνυμία': 57, 'ορισμός': 1, 'σημείωση': 3, 'πρόσφυμα': 3, 'ταυτόσημα': 8, 'χαρακτήρας': 51, 'μορφή επιρρήματος': 1, 'εκφράσεις': 22, 'ρηματικό σχήμα': 3, 'πολυλεκτικό επίρρημα': 2, 'μόριο': 35, 'προφορά': 412, 'ρηματική έκφραση': 15, 'λογοπαίγνια': 2, 'πρόθεση': 46, 'ρηματικό επίθετο': 1, 'κατάληξη επιρρημάτων': 10, 'συναφείς όροι': 1, 'εξωτερικοί σύνδεσμοι': 1, 'αρσενικό γένος': 1, 'πρόθημα': 169, 'κατάληξη': 3, 'υπώνυμα': 7, 'επιφώνημα': 197, 'ρηματικός τύπος': 1, 'συντομομορφή': 560, 'μορφή ρήματος': 68282, 'μορφή επιθέτου': 61779, 'μορφές': 71, 'ιδιωματισμός': 2, 'πολυλεκτικός όρος': 719, 'πολυλεκτικό ουσιαστικό': 180, 'παράγωγα': 25, 'μορφή μετοχής': 806, 'μορφή αριθμητικού': 3, 'άκλιτο': 1, 'επίθημα': 181, 'αριθμητικό': 129, 'συγγενικά': 94, 'σημειώσεις': 45, 'Ιδιωματισμός': 1, 'ρητά': 12, 'φράση': 9, 'συνώνυμα': 556, 'μεταφράσεις': 1, 'κατάληξη ρημάτων': 15, 'σύνθετα': 27, 'υπερώνυμα': 1, 'εναλλακτικός τύπος': 22, 'μορφή ουσιαστικού': 35122, 'επιρρηματική έκφραση': 12, 'αντώνυμα': 76, 'βλέπε': 7, 'μορφή αντωνυμίας': 51, 'αντωνυμία': 100, 'κλίση': 11, 'σύνθετοι τύποι': 1, 'παροιμία': 5, 'μορφή_επιθέτου': 2, 'έκφραση': 738, 'σύμβολο': 8, 'πολυλεκτικό επίθετο': 1, 'ετυμολογία': 867}
'''


wiktionary_file_path = '/data/gsoc2018-spacy/spacy/lang/el/res/elwiktionary-latest-pages-articles.xml'

proper_names_dict={
    'ουσιαστικό':'nouns',
    'επίθετο':'adjectives',
    'άρθρο':'dets',
    'επίρρημα':'adverbs',
    'κύριο όνομα': 'proper_names',
    'μετοχή': 'participles',
    'ρήμα': 'verbs'
}
expected_parts_dict = {}
for expected_part in expected_parts:
    expected_parts_dict[expected_part] = []

other_parts = {}
for title, text, pageid in extract_pages(wiktionary_file_path):
    if text.startswith('#REDIRECT'):
        continue
    title = title.lower()
    all_regex = regex.findall(text)
    all_regex.extend(regex2.findall(text))
    for a in all_regex:
        if a in expected_parts:
            expected_parts_dict[a].append(title)


for i in expected_parts_dict:
    with open('_{0}.py'.format(proper_names_dict[i]), 'w') as f:
        f.write('from __future__ import unicode_literals\n')
        f.write('{} = set(\"\"\"\n'.format(proper_names_dict[i].upper()))
        words = sorted(expected_parts_dict[i])
        line = ''
        to_write = []
        for word in words:            
            if len(line + ' ' + word) > 79:
                to_write.append(line)
                line = ''
            else:
                line = line + ' ' + word
        f.write('\n'.join(to_write))
        f.write('\n\"\"\".split())')



