import pytest


def test_long_text(sq_tokenizer):
    # Excerpt: European Convention on Human Rights
    text = """
Qeveritë nënshkruese, anëtare të Këshillit të Evropës,
Duke pasur parasysh Deklaratën Universale të të Drejtave të
Njeriut, të shpallur nga Asambleja e Përgjithshme e Kombeve të
Bashkuara më 10 dhjetor 1948;
Duke pasur parasysh, se kjo Deklaratë ka për qëllim të sigurojë
njohjen dhe zbatimin universal dhe efektiv të të drejtave të
shpallura në të;
Duke pasur parasysh se qëllimi i Këshillit të Evropës është që të
realizojë një bashkim më të ngushtë midis anëtarëve të tij dhe
se një nga mjetet për të arritur këtë qëllim është mbrojtja dhe
zhvillimi i të drejtave të njeriut dhe i lirive themelore;
Duke ripohuar besimin e tyre të thellë në këto liri themelore që
përbëjnë themelet e drejtësisë dhe të paqes në botë, ruajtja e të
cilave mbështetet kryesisht mbi një regjim politik demokratik nga
njëra anë, dhe nga ana tjetër mbi një kuptim dhe respektim të
përbashkët të të drejtave të njeriut nga të cilat varen;
"""
    tokens = sq_tokenizer(text)
    assert len(tokens) == 182
