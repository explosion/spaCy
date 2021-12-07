import pytest


def test_long_text(xx_tokenizer):
    # Excerpt: Text in Skolt Sami taken from https://www.samediggi.fi
    text = """
Säʹmmla lie Euroopp unioon oʹdinakai alggmeer. Säʹmmlai alggmeerstatus lij raʹvvjum Lääʹddjânnam vuâđđlääʹjjest.  
Alggmeer kriteeʹr vuâđđâʹvve meeraikõskksaž tuâjjorganisaatio, ILO, suåppmõʹšše nââmar 169. 
Suåppmõõžž mieʹldd jiõččvälddsaž jânnmin jälsteei meeraid ââʹnet alggmeeran, 
ko sij puõlvvâʹvve naroodâst, kååʹtt jânnam välddmõõžž leʹbe aazztummuž leʹbe ânnʼjõž riikkraaʹji šõddâm ääiʹj jälste 
jânnmest leʹbe tõn mäddtiõđlaž vuuʹdest, koozz jânnam kooll. Alggmeer ij leäkku mieʹrreei sââʹjest jiiʹjjes jälstemvuuʹdest. 
Alggmeer âlgg jiõčč ââʹnned jiiʹjjes alggmeeran leʹbe leeʹd tõn miõlâst, što sij lie alggmeer. 
Alggmeer lij õlggâm seeilted vuõiggâdvuõđlaž sââʹjest huõlǩâni obbnes leʹbe vueʹzzi jiiʹjjes sosiaalʼlaž, täälʼlaž, 
kulttuurlaž da poliittlaž instituutioid.

Säʹmmlai statuuzz ǩeeʹrjteš Lääʹddjânnam vuâđđläkka eeʹjj 1995. Säʹmmlain alggmeeran lij vuõiggâdvuõtt tuõʹllʼjed da 
ooudâsviikkâd ǩiõlâz da kulttuurâz di tõõzz kuulli ääʹrbvuâlaž jieʹllemvueʹjjeez. Sääʹmǩiõl ââʹnnmest veʹrǧǧniiʹǩǩi 
åʹrnn lij šiõttuum jiiʹjjes lääʹǩǩ. Säʹmmlain lij leämmaž eeʹjjest 1996 vueʹljeeʹl dommvuuʹdsteez ǩiõlâz da kulttuurâz kuõskki 
vuâđđlääʹjj meâldlaž jiõččvaaldâšm. Säʹmmlai jiõččvaldšma kuulli tuâjaid håidd säʹmmlai vaalin vaʹlljääm parlameʹntt, 
Sääʹmteʹǧǧ.
"""

    tokens = xx_tokenizer(text)
    assert len(tokens) == 179
