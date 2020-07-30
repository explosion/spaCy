"""
Consider these two sentences with very similar structure. 
राम ने करण को आम बेचे। 
मैंने आपको आम बेचे।  
For machine to be able to understand structure better, these two should be broken down as 
राम ने करण को आम बेचे। 
मैं ने आप को आम बेचे।
"""

# coding: utf8
from __future__ import unicode_literals

from ...symbols import ORTH, LEMMA, TAG, NORM, PRON_LEMMA

# Hindi Pronoun: https://en.wiktionary.org/wiki/Category:Hindi_pronouns
# https://hi.wikipedia.org/wiki/कारक 

_exc = {}


pronoun_mapping = """
अपना = मैं + का 
अपनी = मैं + की 
अपने = मैं + के  
अपुन = मैं 

आपने = आप + ने
आपको = आप + को
आपसे = आप + से  
आपका = आप + का 
आपकी = आप + की 
आपके = आप + के 

इन्होंने = इन + ने
इनको = इन + को
इन्हें = इन + को 
इनसे = इन + से  
इनका = इन + का 
इनकी = इन + की 
इनके = इन + के 

इसने = इस + ने 
इसको = इस + को
इसे = इस + को  
इससे = इस + से 
इसका = इस + का 
इसकी = इस + की 
इसके = इस + के 
इसमें = इस + में 
इसी = इस 

उन्होंने = उन + ने
उनको = उन + को 
उन्हें = उन + को 
उनसे = उन + से  
उनका = उन + का 
उनकी = उन + की  
उनके = उन + के 

उसने = उस + ने 
उसको = उस + को 
उसे = उस + को 
उससे = उस + से 
उसका = उस + का 
उसकी = उक + की 
  
जिन्होंने = जिस + ने
जिनको = जिन + को 
जिन्हें = जिस  + को
जिनसे = जिन + से 
जिनका = जिस  + का 
जिनकी = जिन + की 
जिनके = जिन + के 
जिनमें = जिन + में  

जिसने = जिस + ने 
जिसको = जिस + को 
जिसे = जिस + को 
जो = जिस + को  
जिससे = जिस + से 
जिसका = जिस + का 
जिसकी = जिस + की 
जिसके = जिस + के 
जिसमें = जिस + में 

तुझ = तुम 
तुझको = तुम + को 
तुझे = तुम + को 
तुझसे = तुम + से 
तुझमें = तुम + में 

तुमने = तुम + ने 
तुमको = तुम + को  
तुम्हें = तुम + को 
तुमसे = तुम + से 
तुम्हारा = तुम + का
तुम्हारी = तुम + की 
तू = तुम 

तूने = तुम + ने 
तेरा = तुम + का 
तेरी = तुम + की 
तेरे = तुम + के 
तेरेको = तुम + को 
 
मैंने = मैं + ने
मुझको = मैं  + को 
मुझे = मैं + को  
मुझसे = मैं  + से
मेरा = मैं + का  
मेरी = मैं + की  
मेरे = मैं + के 

वही = वह + ई 
वे = वह + ऐ 
वो = वह + ओ 

हमने = हम + ने
हमको = हम + को
हमें = हम + को 
हमसे = हम + से  
हमारा = हम + का 
हमारी = हम + की
हमारे = हम + के  
"""


for line in pronoun_mapping.split("\n"):
    if len(line.strip())==0:
        continue 

    left, right = line.split("=")
    if "+" in right:
        right1, right2 = right.split("+")

        _exc[left.strip()] = [
            {ORTH: right1.strip(), LEMMA: PRON_LEMMA, NORM: right1.strip()},
            {ORTH: right2.strip(), LEMMA: right2.strip(), NORM: right2.strip()},
        ]
    else: 
        _exc[left.strip()] = [
            {ORTH: right.strip(), LEMMA: PRON_LEMMA, NORM: right.strip()},
        ]

TOKENIZER_EXCEPTIONS = _exc
