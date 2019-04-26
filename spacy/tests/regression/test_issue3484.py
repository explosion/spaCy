# coding: utf8
import spacy


# The following must be run multiple times, manually from the command line
# and will not be run with the automated tests.
# If the bug is present it will produce either 'dose' or 'dos' randomly
# if the fix is present, it should consistantly produce one of the two words
# ('dose' under my test)
# Unfortunately I'm not aware of any way to put this inside of the pytest 
# framework because the bug only exists when starting the python interpreter
# multiple times (ie.. you can't just run the print statement multiple times)
if __name__ == '__main__':
    nlp = spacy.load('en_core_web_sm')
    print([tok.lemma_ for tok in nlp('doses')])
