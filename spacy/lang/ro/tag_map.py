from __future__ import unicode_literals

from ...symbols import POS, ADJ, ADP, ADV, INTJ, NOUN, NUM, PART
from ...symbols import PRON, PROPN, PUNCT, SYM, VERB, X, CCONJ, SCONJ, DET, AUX

TAG_MAP = {
    "Afcfson": {
        
        "Degree": "Cmp",
        "Gender": "Fem",
        "Number": "Sing",
        POS: ADJ,
    },
    "Afcfsrn": {
        
        "Degree": "Cmp",
        "Gender": "Fem",
        "Number": "Sing",
        POS: ADJ,
    },
    "Afp": {"Degree": "Pos", POS: ADJ},
    "Afp-p-n": {"Degree": "Pos", "Number": "Plur", POS: ADJ},
    "Afp-p-ny": {"Degree": "Pos", "Number": "Plur", POS: ADJ},
    "Afp-poy": { "Degree": "Pos", "Number": "Plur", POS: ADJ},
    "Afpf--n": {"Degree": "Pos", "Gender": "Fem", POS: ADJ},
    "Afpfp-n": {"Degree": "Pos", "Gender": "Fem", "Number": "Plur", POS: ADJ},
    "Afpfpoy": {
        
        "Degree": "Pos",
        "Gender": "Fem",
        "Number": "Plur",
        POS: ADJ,
    },
    "Afpfpry": {
        
        "Degree": "Pos",
        "Gender": "Fem",
        "Number": "Plur",
        POS: ADJ,
    },
    "Afpfson": {
        
        "Degree": "Pos",
        "Gender": "Fem",
        "Number": "Sing",
        POS: ADJ,
    },
    "Afpfsoy": {
        
        "Degree": "Pos",
        "Gender": "Fem",
        "Number": "Sing",
        POS: ADJ,
    },
    "Afpfsrn": {
        
        "Degree": "Pos",
        "Gender": "Fem",
        "Number": "Sing",
        POS: ADJ,
    },
    "Afpfsry": {
        
        "Degree": "Pos",
        "Gender": "Fem",
        "Number": "Sing",
        POS: ADJ,
    },
    "Afpmp-n": {"Degree": "Pos", "Gender": "Masc", "Number": "Plur", POS: ADJ},
    "Afpmpoy": {
        
        "Degree": "Pos",
        "Gender": "Masc",
        "Number": "Plur",
        POS: ADJ,
    },
    "Afpmpry": {
        
        "Degree": "Pos",
        "Gender": "Masc",
        "Number": "Plur",
        POS: ADJ,
    },
    "Afpms-n": {"Degree": "Pos", "Gender": "Masc", "Number": "Sing", POS: ADJ},
    "Afpmsoy": {
        
        "Degree": "Pos",
        "Gender": "Masc",
        "Number": "Sing",
        POS: ADJ,
    },
    "Afpmsry": {
        
        "Degree": "Pos",
        "Gender": "Masc",
        "Number": "Sing",
        POS: ADJ,
    },
    "COLON": {POS: PUNCT},
    "COMMA": {POS: PUNCT},
    "Ccssp": {POS: CCONJ, "Polarity": "Pos"},
    "Crssp": {POS: CCONJ, "Polarity": "Pos"},
    "Csssp": {POS: SCONJ, "Polarity": "Pos"},
    "Cssspy": {POS: SCONJ, "Polarity": "Pos"},
    "DASH": {POS: PUNCT},
    "DBLQ": {POS: PUNCT},
    "Dd3-po---e": {
        
        "Number": "Plur",
        POS: DET,
        "Person": "three",
        "PronType": "Dem",
    },
    "Dd3fpr": {
        
        "Gender": "Fem",
        "Number": "Plur",
        POS: DET,
        "Person": "three",
        "PronType": "Dem",
    },
    "Dd3fpr---e": {
        
        "Gender": "Fem",
        "Number": "Plur",
        POS: DET,
        "Person": "three",
        "PronType": "Dem",
    },
    "Dd3fso---e": {
        
        "Gender": "Fem",
        "Number": "Sing",
        POS: DET,
        "Person": "three",
        "PronType": "Dem",
    },
    "Dd3fso---o": {
        
        "Gender": "Fem",
        "Number": "Sing",
        POS: DET,
        "Person": "three",
        "PronType": "Dem",
    },
    "Dd3fsr": {
        
        "Gender": "Fem",
        "Number": "Sing",
        POS: DET,
        "Person": "three",
        "PronType": "Dem",
    },
    "Dd3fsr---e": {
        
        "Gender": "Fem",
        "Number": "Sing",
        POS: DET,
        "Person": "three",
        "PronType": "Dem",
    },
    "Dd3fsr---o": {
        
        "Gender": "Fem",
        "Number": "Sing",
        POS: DET,
        "Person": "three",
        "PronType": "Dem",
    },
    "Dd3mpo": {
        
        "Gender": "Masc",
        "Number": "Plur",
        POS: DET,
        "Person": "three",
        "PronType": "Dem",
    },
    "Dd3mpr---e": {
        
        "Gender": "Masc",
        "Number": "Plur",
        POS: DET,
        "Person": "three",
        "PronType": "Dem",
    },
    "Dd3mso---e": {
        
        "Gender": "Masc",
        "Number": "Sing",
        POS: DET,
        "Person": "three",
        "PronType": "Dem",
    },
    "Dd3msr---e": {
        
        "Gender": "Masc",
        "Number": "Sing",
        POS: DET,
        "Person": "three",
        "PronType": "Dem",
    },
    "Dd3msr---o": {
        
        "Gender": "Masc",
        "Number": "Sing",
        POS: DET,
        "Person": "three",
        "PronType": "Dem",
    },
    "Dh3fsr": {
        
        "Gender": "Fem",
        "Number": "Sing",
        POS: DET,
        "Person": "three",
        
    },
    "Dh3mp": {
        "Gender": "Masc",
        "Number": "Plur",
        POS: DET,
        "Person": "three",
        
    },
    "Dh3ms": {
        "Gender": "Masc",
        "Number": "Sing",
        POS: DET,
        "Person": "three",
        
    },
    "Di3": {POS: DET, "Person": "three", "PronType": "Ind"},
    "Di3--r---e": { POS: DET, "Person": "three", "PronType": "Ind"},
    "Di3-po": {
        
        "Number": "Plur",
        POS: DET,
        "Person": "three",
        "PronType": "Ind",
    },
    "Di3-po---e": {
        
        "Number": "Plur",
        POS: DET,
        "Person": "three",
        "PronType": "Ind",
    },
    "Di3-sr": {
        
        "Number": "Sing",
        POS: DET,
        "Person": "three",
        "PronType": "Ind",
    },
    "Di3-sr---e": {
        
        "Number": "Sing",
        POS: DET,
        "Person": "three",
        "PronType": "Ind",
    },
    "Di3fp": {
        "Gender": "Fem",
        "Number": "Plur",
        POS: DET,
        "Person": "three",
        "PronType": "Ind",
    },
    "Di3fpr": {
        
        "Gender": "Fem",
        "Number": "Plur",
        POS: DET,
        "Person": "three",
        "PronType": "Ind",
    },
    "Di3fpr---e": {
        
        "Gender": "Fem",
        "Number": "Plur",
        POS: DET,
        "Person": "three",
        "PronType": "Ind",
    },
    "Di3fso---e": {
        
        "Gender": "Fem",
        "Number": "Sing",
        POS: DET,
        "Person": "three",
        "PronType": "Ind",
    },
    "Di3fsr": {
        
        "Gender": "Fem",
        "Number": "Sing",
        POS: DET,
        "Person": "three",
        "PronType": "Ind",
    },
    "Di3fsr---e": {
        
        "Gender": "Fem",
        "Number": "Sing",
        POS: DET,
        "Person": "three",
        "PronType": "Ind",
    },
    "Di3mp": {
        "Gender": "Masc",
        "Number": "Plur",
        POS: DET,
        "Person": "three",
        "PronType": "Ind",
    },
    "Di3mpr": {
        
        "Gender": "Masc",
        "Number": "Plur",
        POS: DET,
        "Person": "three",
        "PronType": "Ind",
    },
    "Di3mpr---e": {
        
        "Gender": "Masc",
        "Number": "Plur",
        POS: DET,
        "Person": "three",
        "PronType": "Ind",
    },
    "Di3ms": {
        "Gender": "Masc",
        "Number": "Sing",
        POS: DET,
        "Person": "three",
        "PronType": "Ind",
    },
    "Di3ms----e": {
        "Gender": "Masc",
        "Number": "Sing",
        POS: DET,
        "Person": "three",
        "PronType": "Ind",
    },
    "Di3mso---e": {
        
        "Gender": "Masc",
        "Number": "Sing",
        POS: DET,
        "Person": "three",
        "PronType": "Ind",
    },
    "Di3msr": {
        
        "Gender": "Masc",
        "Number": "Sing",
        POS: DET,
        "Person": "three",
        "PronType": "Ind",
    },
    "Di3msr---e": {
        
        "Gender": "Masc",
        "Number": "Sing",
        POS: DET,
        "Person": "three",
        "PronType": "Ind",
    },
    "Ds1fp-s": {
        "Gender": "Fem",
        "Number": "Plur",
        POS: DET,
        "Person": "one",
        "Poss": "Yes",
        "PronType": "Prs",
    },
    "Ds1fsos": {
        
        "Gender": "Fem",
        "Number": "Sing",
        POS: DET,
        "Person": "one",
        "Poss": "Yes",
        "PronType": "Prs",
    },
    "Ds1fsrp": {
        
        "Gender": "Fem",
        "Number": "Sing",
        POS: DET,
        "Person": "one",
        "Poss": "Yes",
        "PronType": "Prs",
    },
    "Ds1fsrs": {
        
        "Gender": "Fem",
        "Number": "Sing",
        POS: DET,
        "Person": "one",
        "Poss": "Yes",
        "PronType": "Prs",
    },
    "Ds1ms-p": {
        "Gender": "Masc",
        "Number": "Sing",
        POS: DET,
        "Person": "one",
        "Poss": "Yes",
        "PronType": "Prs",
    },
    "Ds1ms-s": {
        "Gender": "Masc",
        "Number": "Sing",
        POS: DET,
        "Person": "one",
        "Poss": "Yes",
        "PronType": "Prs",
    },
    "Ds2---s": {POS: DET, "Person": "two", "Poss": "Yes", "PronType": "Prs"},
    "Ds2fsrs": {
        
        "Gender": "Fem",
        "Number": "Sing",
        POS: DET,
        "Person": "two",
        "Poss": "Yes",
        "PronType": "Prs",
    },
    "Ds3---p": {POS: DET, "Person": "three", "Poss": "Yes", "PronType": "Prs"},
    "Ds3---s": {POS: DET, "Person": "three", "Poss": "Yes", "PronType": "Prs"},
    "Ds3fp-s": {
        "Gender": "Fem",
        "Number": "Plur",
        POS: DET,
        "Person": "three",
        "Poss": "Yes",
        "PronType": "Prs",
    },
    "Ds3fsos": {
        
        "Gender": "Fem",
        "Number": "Sing",
        POS: DET,
        "Person": "three",
        "Poss": "Yes",
        "PronType": "Prs",
    },
    "Ds3fsrs": {
        
        "Gender": "Fem",
        "Number": "Sing",
        POS: DET,
        "Person": "three",
        "Poss": "Yes",
        "PronType": "Prs",
    },
    "Ds3ms-s": {
        "Gender": "Masc",
        "Number": "Sing",
        POS: DET,
        "Person": "three",
        "Poss": "Yes",
        "PronType": "Prs",
    },
    "Dw3--r---e": { POS: DET, "Person": "three"},
    "Dw3fpr": {
        
        "Gender": "Fem",
        "Number": "Plur",
        POS: DET,
        "Person": "three",
        
    },
    "Dw3mso---e": {
        
        "Gender": "Masc",
        "Number": "Sing",
        POS: DET,
        "Person": "three",
        
    },
    "Dz3fsr---e": {
        
        "Gender": "Fem",
        "Number": "Sing",
        POS: DET,
        "Person": "three",
        "PronType": "Neg",
    },
    "Dz3msr---e": {
        
        "Gender": "Masc",
        "Number": "Sing",
        POS: DET,
        "Person": "three",
        "PronType": "Neg",
    },
    "EQUAL": {POS: SYM},
    "EXCL": {POS: PUNCT},
    "GT": {POS: SYM},
    "I": {POS: INTJ},
    "LPAR": {POS: PUNCT},
    "Mc": {"NumType": "Card", POS: NUM},
    "Mc-p-d": {"NumForm": "Digit", "NumType": "Card", "Number": "Plur", POS: NUM},
    "Mc-p-l": {"NumForm": "Word", "NumType": "Card", "Number": "Plur", POS: NUM},
    "Mcfp-l": {
        "Gender": "Fem",
        "NumForm": "Word",
        "NumType": "Card",
        "Number": "Plur",
        POS: NUM,
    },
    "Mcfp-ln": {
        "Gender": "Fem",
        "NumForm": "Word",
        "NumType": "Card",
        "Number": "Plur",
        POS: NUM,
    },
    "Mcfsrln": {
        
        "Gender": "Fem",
        "NumForm": "Word",
        "NumType": "Card",
        "Number": "Sing",
        POS: NUM,
    },
    "Mcmp-l": {
        "Gender": "Masc",
        "NumForm": "Word",
        "NumType": "Card",
        "Number": "Plur",
        POS: NUM,
    },
    "Mcmsrl": {
        
        "Gender": "Masc",
        "NumForm": "Word",
        "NumType": "Card",
        "Number": "Sing",
        POS: NUM,
    },
    "Mffprln": {
        
        "Gender": "Fem",
        "NumForm": "Word",
        "NumType": "Card",
        "Number": "Plur",
        POS: NUM,
    },
    "Mlfpo": {
        
        "Gender": "Fem",
        "NumType": "Card",
        "Number": "Plur",
        POS: NUM,
        "PronType": "Tot",
    },
    "Mlfpr": {
        
        "Gender": "Fem",
        "NumType": "Card",
        "Number": "Plur",
        POS: NUM,
        "PronType": "Tot",
    },
    "Mlmpr": {
        
        "Gender": "Masc",
        "NumType": "Card",
        "Number": "Plur",
        POS: NUM,
        "PronType": "Tot",
    },
    "Mo---l": {"NumForm": "Word", "NumType": "Ord", POS: NUM},
    "Mo-s-r": {"NumForm": "Roman", "NumType": "Ord", "Number": "Sing", POS: NUM},
    "Mofp-ln": {
        "Gender": "Fem",
        "NumForm": "Word",
        "NumType": "Ord",
        "Number": "Plur",
        POS: NUM,
    },
    "Mofprly": {
        
        "Gender": "Fem",
        "NumForm": "Word",
        "NumType": "Ord",
        "Number": "Plur",
        POS: NUM,
    },
    "Mofs-l": {
        "Gender": "Fem",
        "NumForm": "Word",
        "NumType": "Ord",
        "Number": "Sing",
        POS: NUM,
    },
    "Mofsrln": {
        
        "Gender": "Fem",
        "NumForm": "Word",
        "NumType": "Ord",
        "Number": "Sing",
        POS: NUM,
    },
    "Mofsrly": {
        
        "Gender": "Fem",
        "NumForm": "Word",
        "NumType": "Ord",
        "Number": "Sing",
        POS: NUM,
    },
    "Momprly": {
        
        "Gender": "Masc",
        "NumForm": "Word",
        "NumType": "Ord",
        "Number": "Plur",
        POS: NUM,
    },
    "Moms-l": {
        "Gender": "Masc",
        "NumForm": "Word",
        "NumType": "Ord",
        "Number": "Sing",
        POS: NUM,
    },
    "Moms-ln": {
        "Gender": "Masc",
        "NumForm": "Word",
        "NumType": "Ord",
        "Number": "Sing",
        POS: NUM,
    },
    "Momsoly": {
        
        "Gender": "Masc",
        "NumForm": "Word",
        "NumType": "Ord",
        "Number": "Sing",
        POS: NUM,
    },
    "Momsrly": {
        
        "Gender": "Masc",
        "NumForm": "Word",
        "NumType": "Ord",
        "Number": "Sing",
        POS: NUM,
    },
    "Nc": {POS: NOUN},
    "Ncf--n": {"Gender": "Fem", POS: NOUN},
    "Ncfp-n": {"Gender": "Fem", "Number": "Plur", POS: NOUN},
    "Ncfpoy": { "Gender": "Fem", "Number": "Plur", POS: NOUN},
    "Ncfpry": { "Gender": "Fem", "Number": "Plur", POS: NOUN},
    "Ncfson": { "Gender": "Fem", "Number": "Sing", POS: NOUN},
    "Ncfsoy": { "Gender": "Fem", "Number": "Sing", POS: NOUN},
    "Ncfsrn": { "Gender": "Fem", "Number": "Sing", POS: NOUN},
    "Ncfsry": { "Gender": "Fem", "Number": "Sing", POS: NOUN},
    "Ncm--n": {"Gender": "Masc", POS: NOUN},
    "Ncmp-n": {"Gender": "Masc", "Number": "Plur", POS: NOUN},
    "Ncmpoy": { "Gender": "Masc", "Number": "Plur", POS: NOUN},
    "Ncmpry": { "Gender": "Masc", "Number": "Plur", POS: NOUN},
    "Ncms-n": {"Gender": "Masc", "Number": "Sing", POS: NOUN},
    "Ncms-ny": {"Gender": "Masc", "Number": "Sing", POS: NOUN},
    "Ncmsoy": { "Gender": "Masc", "Number": "Sing", POS: NOUN},
    "Ncmsrn": { "Gender": "Masc", "Number": "Sing", POS: NOUN},
    "Ncmsry": { "Gender": "Masc", "Number": "Sing", POS: NOUN},
    "Np": {POS: PROPN},
    "Npfsoy": { "Gender": "Fem", "Number": "Sing", POS: PROPN},
    "Npfsry": { "Gender": "Fem", "Number": "Sing", POS: PROPN},
    "Npmsoy": { "Gender": "Masc", "Number": "Sing", POS: PROPN},
    "Npmsry": { "Gender": "Masc", "Number": "Sing", POS: PROPN},
    "PERCENT": {POS: SYM},
    "PERIOD": {POS: PUNCT},
    "PLUSMINUS": {POS: SYM},
    "Pd3-po": {
        
        "Number": "Plur",
        POS: PRON,
        "Person": "three",
        "PronType": "Dem",
    },
    "Pd3fpr": {
        
        "Gender": "Fem",
        "Number": "Plur",
        POS: PRON,
        "Person": "three",
        "PronType": "Dem",
    },
    "Pd3fso": {
        
        "Gender": "Fem",
        "Number": "Sing",
        POS: PRON,
        "Person": "three",
        "PronType": "Dem",
    },
    "Pd3fsr": {
        
        "Gender": "Fem",
        "Number": "Sing",
        POS: PRON,
        "Person": "three",
        "PronType": "Dem",
    },
    "Pd3mpr": {
        
        "Gender": "Masc",
        "Number": "Plur",
        POS: PRON,
        "Person": "three",
        "PronType": "Dem",
    },
    "Pd3mso": {
        
        "Gender": "Masc",
        "Number": "Sing",
        POS: PRON,
        "Person": "three",
        "PronType": "Dem",
    },
    "Pd3msr": {
        
        "Gender": "Masc",
        "Number": "Sing",
        POS: PRON,
        "Person": "three",
        "PronType": "Dem",
    },
    "Pi3--r": { POS: PRON, "Person": "three", "PronType": "Ind"},
    "Pi3-po": {
        
        "Number": "Plur",
        POS: PRON,
        "Person": "three",
        "PronType": "Ind",
    },
    "Pi3-so": {
        
        "Number": "Sing",
        POS: PRON,
        "Person": "three",
        "PronType": "Ind",
    },
    "Pi3-sr": {
        
        "Number": "Sing",
        POS: PRON,
        "Person": "three",
        "PronType": "Ind",
    },
    "Pi3fpr": {
        
        "Gender": "Fem",
        "Number": "Plur",
        POS: PRON,
        "Person": "three",
        "PronType": "Ind",
    },
    "Pi3fso": {
        
        "Gender": "Fem",
        "Number": "Sing",
        POS: PRON,
        "Person": "three",
        "PronType": "Ind",
    },
    "Pi3fsr": {
        
        "Gender": "Fem",
        "Number": "Sing",
        POS: PRON,
        "Person": "three",
        "PronType": "Ind",
    },
    "Pi3mpr": {
        
        "Gender": "Masc",
        "Number": "Plur",
        POS: PRON,
        "Person": "three",
        "PronType": "Ind",
    },
    "Pi3msr": {
        
        "Gender": "Masc",
        "Number": "Sing",
        POS: PRON,
        "Person": "three",
        "PronType": "Ind",
    },
    "Pi3msr--y": {
        
        "Gender": "Masc",
        "Number": "Sing",
        POS: PRON,
        "Person": "three",
        "PronType": "Ind",
        
    },
    "Pp1-pa--------w": {
        "Case": "Acc",
        "Number": "Plur",
        POS: PRON,
        "Person": "one",
        "PronType": "Prs",
    },
    "Pp1-pa--y-----w": {
        "Case": "Acc",
        "Number": "Plur",
        POS: PRON,
        "Person": "one",
        "PronType": "Prs",
        
    },
    "Pp1-pd--------w": {
        "Case": "Dat",
        "Number": "Plur",
        POS: PRON,
        "Person": "one",
        "PronType": "Prs",
    },
    "Pp1-pr--------s": {
        
        "Number": "Plur",
        POS: PRON,
        "Person": "one",
        "PronType": "Prs",
    },
    "Pp1-sa--------s": {
        "Case": "Acc",
        "Number": "Sing",
        POS: PRON,
        "Person": "one",
        "PronType": "Prs",
    },
    "Pp1-sa--------w": {
        "Case": "Acc",
        "Number": "Sing",
        POS: PRON,
        "Person": "one",
        "PronType": "Prs",
    },
    "Pp1-sa--y-----w": {
        "Case": "Acc",
        "Number": "Sing",
        POS: PRON,
        "Person": "one",
        "PronType": "Prs",
        
    },
    "Pp1-sd--------w": {
        "Case": "Dat",
        "Number": "Sing",
        POS: PRON,
        "Person": "one",
        "PronType": "Prs",
    },
    "Pp1-sd--y-----w": {
        "Case": "Dat",
        "Number": "Sing",
        POS: PRON,
        "Person": "one",
        "PronType": "Prs",
        
    },
    "Pp1-sn--------s": {
        "Case": "Nom",
        "Number": "Sing",
        POS: PRON,
        "Person": "one",
        "PronType": "Prs",
    },
    "Pp2-----------s": {POS: PRON, "Person": "two", "PronType": "Prs"},
    "Pp2-pa--------w": {
        "Case": "Acc",
        "Number": "Plur",
        POS: PRON,
        "Person": "two",
        "PronType": "Prs",
    },
    "Pp2-pa--y-----w": {
        "Case": "Acc",
        "Number": "Plur",
        POS: PRON,
        "Person": "two",
        "PronType": "Prs",
        
    },
    "Pp2-pd--------w": {
        "Case": "Dat",
        "Number": "Plur",
        POS: PRON,
        "Person": "two",
        "PronType": "Prs",
    },
    "Pp2-pr--------s": {
        
        "Number": "Plur",
        POS: PRON,
        "Person": "two",
        "PronType": "Prs",
    },
    "Pp2-sa--------s": {
        "Case": "Acc",
        "Number": "Sing",
        POS: PRON,
        "Person": "two",
        "PronType": "Prs",
    },
    "Pp2-sa--------w": {
        "Case": "Acc",
        "Number": "Sing",
        POS: PRON,
        "Person": "two",
        "PronType": "Prs",
    },
    "Pp2-sa--y-----w": {
        "Case": "Acc",
        "Number": "Sing",
        POS: PRON,
        "Person": "two",
        "PronType": "Prs",
        
    },
    "Pp2-sd--y-----w": {
        "Case": "Dat",
        "Number": "Sing",
        POS: PRON,
        "Person": "two",
        "PronType": "Prs",
        
    },
    "Pp2-sn--------s": {
        "Case": "Nom",
        "Number": "Sing",
        POS: PRON,
        "Person": "two",
        "PronType": "Prs",
    },
    "Pp3-pd--------w": {
        "Case": "Dat",
        "Number": "Plur",
        POS: PRON,
        "Person": "three",
        "PronType": "Prs",
    },
    "Pp3-pd--y-----w": {
        "Case": "Dat",
        "Number": "Plur",
        POS: PRON,
        "Person": "three",
        "PronType": "Prs",
        
    },
    "Pp3-po--------s": {
        
        "Number": "Plur",
        POS: PRON,
        "Person": "three",
        "PronType": "Prs",
    },
    "Pp3-sd--------w": {
        "Case": "Dat",
        "Number": "Sing",
        POS: PRON,
        "Person": "three",
        "PronType": "Prs",
    },
    "Pp3-sd--y-----w": {
        "Case": "Dat",
        "Number": "Sing",
        POS: PRON,
        "Person": "three",
        "PronType": "Prs",
        
    },
    "Pp3fpa--------w": {
        "Case": "Acc",
        "Gender": "Fem",
        "Number": "Plur",
        POS: PRON,
        "Person": "three",
        "PronType": "Prs",
    },
    "Pp3fpa--y-----w": {
        "Case": "Acc",
        "Gender": "Fem",
        "Number": "Plur",
        POS: PRON,
        "Person": "three",
        "PronType": "Prs",
        
    },
    "Pp3fpr--------s": {
        
        "Gender": "Fem",
        "Number": "Plur",
        POS: PRON,
        "Person": "three",
        "PronType": "Prs",
    },
    "Pp3fsa--------w": {
        "Case": "Acc",
        "Gender": "Fem",
        "Number": "Sing",
        POS: PRON,
        "Person": "three",
        "PronType": "Prs",
    },
    "Pp3fsa--y-----w": {
        "Case": "Acc",
        "Gender": "Fem",
        "Number": "Sing",
        POS: PRON,
        "Person": "three",
        "PronType": "Prs",
        
    },
    "Pp3fsr--------s": {
        
        "Gender": "Fem",
        "Number": "Sing",
        POS: PRON,
        "Person": "three",
        "PronType": "Prs",
    },
    "Pp3mpa--------w": {
        "Case": "Acc",
        "Gender": "Masc",
        "Number": "Plur",
        POS: PRON,
        "Person": "three",
        "PronType": "Prs",
    },
    "Pp3mpa--y-----w": {
        "Case": "Acc",
        "Gender": "Masc",
        "Number": "Plur",
        POS: PRON,
        "Person": "three",
        "PronType": "Prs",
        
    },
    "Pp3mpr--------s": {
        
        "Gender": "Masc",
        "Number": "Plur",
        POS: PRON,
        "Person": "three",
        "PronType": "Prs",
    },
    "Pp3msa--------w": {
        "Case": "Acc",
        "Gender": "Masc",
        "Number": "Sing",
        POS: PRON,
        "Person": "three",
        "PronType": "Prs",
    },
    "Pp3msa--y-----w": {
        "Case": "Acc",
        "Gender": "Masc",
        "Number": "Sing",
        POS: PRON,
        "Person": "three",
        "PronType": "Prs",
        
    },
    "Pp3mso--------s": {
        
        "Gender": "Masc",
        "Number": "Sing",
        POS: PRON,
        "Person": "three",
        "PronType": "Prs",
    },
    "Pp3msr--------s": {
        
        "Gender": "Masc",
        "Number": "Sing",
        POS: PRON,
        "Person": "three",
        "PronType": "Prs",
    },
    "Ps1mp-s": {
        "Gender": "Masc",
        "Number": "Plur",
        POS: PRON,
        "Person": "one",
        "Poss": "Yes",
        "PronType": "Prs",
    },
    "Ps3---p": {POS: PRON, "Person": "three", "Poss": "Yes", "PronType": "Prs"},
    "Ps3---s": {POS: PRON, "Person": "three", "Poss": "Yes", "PronType": "Prs"},
    "Ps3fp-s": {
        "Gender": "Fem",
        "Number": "Plur",
        POS: PRON,
        "Person": "three",
        "Poss": "Yes",
        "PronType": "Prs",
    },
    "Pw3--r": { POS: PRON, "Person": "three"},
    "Pw3-po": {
        
        "Number": "Plur",
        POS: PRON,
        "Person": "three",
        
    },
    "Pw3fso": {
        
        "Gender": "Fem",
        "Number": "Sing",
        POS: PRON,
        "Person": "three",
        
    },
    "Pw3mpr": {
        
        "Gender": "Masc",
        "Number": "Plur",
        POS: PRON,
        "Person": "three",
        
    },
    "Px3--a--------s": {
        "Case": "Acc",
        POS: PRON,
        "Person": "three",
        "PronType": "Prs",
        "Reflex": "Yes",
    },
    "Px3--a--------w": {
        "Case": "Acc",
        POS: PRON,
        "Person": "three",
        "PronType": "Prs",
        "Reflex": "Yes",
    },
    "Px3--a--y-----w": {
        "Case": "Acc",
        POS: PRON,
        "Person": "three",
        "PronType": "Prs",
        "Reflex": "Yes",
        
    },
    "Px3--d--------w": {
        "Case": "Dat",
        POS: PRON,
        "Person": "three",
        "PronType": "Prs",
        "Reflex": "Yes",
    },
    "Px3--d--y-----w": {
        "Case": "Dat",
        POS: PRON,
        "Person": "three",
        "PronType": "Prs",
        "Reflex": "Yes",
        
    },
    "Pz3-sr": {
        
        "Number": "Sing",
        POS: PRON,
        "Person": "three",
        "PronType": "Neg",
    },
    "Pz3msr": {
        
        "Gender": "Masc",
        "Number": "Sing",
        POS: PRON,
        "Person": "three",
        "PronType": "Neg",
    },
    "QUEST": {POS: PUNCT},
    "QUOT": {POS: PUNCT},
    "Qn": {POS: PART, "PartType": "Inf"},
    "Qs": {"Mood": "Sub", POS: PART},
    "Qs-y": {"Mood": "Sub", POS: PART},
    "Qz": {POS: PART, "Polarity": "Neg"},
    "Qz-y": {POS: PART, "Polarity": "Neg"},
    "RPAR": {POS: PUNCT},
    "Rc": {POS: ADV},
    "Rgp": {"Degree": "Pos", POS: ADV},
    "Rgpy": {"Degree": "Pos", POS: ADV},
    "Rgs": {"Degree": "Sup", POS: ADV},
    "Rp": {POS: ADV},
    "Rw": {POS: ADV},
    "Rz": {POS: ADV, "PronType": "Neg"},
    "SCOLON": {"AdpType": "Prep", POS: PUNCT},
    "SLASH": {"AdpType": "Prep", POS: SYM},
    "Spsa": {"AdpType": "Prep", "Case": "Acc", POS: ADP},
    "Spsay": {"AdpType": "Prep", "Case": "Acc", POS: ADP},
    "Spsd": {"AdpType": "Prep", "Case": "Dat", POS: ADP},
    "Spsg": {"AdpType": "Prep", "Case": "Gen", POS: ADP},
    "Spsgy": {"AdpType": "Prep", "Case": "Gen", POS: ADP},
    "Td-po": { "Number": "Plur", POS: DET, "PronType": "Dem"},
    "Tdfpr": {
        
        "Gender": "Fem",
        "Number": "Plur",
        POS: DET,
        "PronType": "Dem",
    },
    "Tdfso": {
        
        "Gender": "Fem",
        "Number": "Sing",
        POS: DET,
        "PronType": "Dem",
    },
    "Tdfsr": {
        
        "Gender": "Fem",
        "Number": "Sing",
        POS: DET,
        "PronType": "Dem",
    },
    "Tdmpr": {
        
        "Gender": "Masc",
        "Number": "Plur",
        POS: DET,
        "PronType": "Dem",
    },
    "Tdmso": {
        
        "Gender": "Masc",
        "Number": "Sing",
        POS: DET,
        "PronType": "Dem",
    },
    "Tdmsr": {
        
        "Gender": "Masc",
        "Number": "Sing",
        POS: DET,
        "PronType": "Dem",
    },
    "Tf-so": { "Number": "Sing", POS: DET, "PronType": "Art"},
    "Tffs-y": {
        "Gender": "Fem",
        "Number": "Sing",
        POS: DET,
        "PronType": "Art",
        
    },
    "Tfms-y": {
        "Gender": "Masc",
        "Number": "Sing",
        POS: DET,
        "PronType": "Art",
        
    },
    "Tfmsoy": {
        
        "Gender": "Masc",
        "Number": "Sing",
        POS: DET,
        "PronType": "Art",
        
    },
    "Tfmsry": {
        
        "Gender": "Masc",
        "Number": "Sing",
        POS: DET,
        "PronType": "Art",
        
    },
    "Ti-po": { "Number": "Plur", POS: DET, "PronType": "Ind"},
    "Tifp-y": {
        "Gender": "Fem",
        "Number": "Plur",
        POS: DET,
        "PronType": "Ind",
        
    },
    "Tifso": {
        
        "Gender": "Fem",
        "Number": "Sing",
        POS: DET,
        "PronType": "Ind",
    },
    "Tifsr": {
        
        "Gender": "Fem",
        "Number": "Sing",
        POS: DET,
        "PronType": "Ind",
    },
    "Timso": {
        
        "Gender": "Masc",
        "Number": "Sing",
        POS: DET,
        "PronType": "Ind",
    },
    "Timsr": {
        
        "Gender": "Masc",
        "Number": "Sing",
        POS: DET,
        "PronType": "Ind",
    },
    "Tsfp": {
        "Gender": "Fem",
        "Number": "Plur",
        POS: DET,
        "Poss": "Yes",
        "PronType": "Prs",
    },
    "Tsfs": {
        "Gender": "Fem",
        "Number": "Sing",
        POS: DET,
        "Poss": "Yes",
        "PronType": "Prs",
    },
    "Tsmp": {
        "Gender": "Masc",
        "Number": "Plur",
        POS: DET,
        "Poss": "Yes",
        "PronType": "Prs",
    },
    "Tsms": {
        "Gender": "Masc",
        "Number": "Sing",
        POS: DET,
        "Poss": "Yes",
        "PronType": "Prs",
    },
    "Va--1": {POS: AUX, "Person": "one"},
    "Va--1p": {"Number": "Plur", POS: AUX, "Person": "one"},
    "Va--1s": {"Number": "Sing", POS: AUX, "Person": "one"},
    "Va--2p": {"Number": "Plur", POS: AUX, "Person": "two"},
    "Va--2s": {"Number": "Sing", POS: AUX, "Person": "two"},
    "Va--3": {POS: AUX, "Person": "three"},
    "Va--3-----y": {POS: AUX, "Person": "three"},
    "Va--3p": {"Number": "Plur", POS: AUX, "Person": "three"},
    "Va--3p----y": {"Number": "Plur", POS: AUX, "Person": "three"},
    "Va--3s": {"Number": "Sing", POS: AUX, "Person": "three"},
    "Va--3s----y": {"Number": "Sing", POS: AUX, "Person": "three"},
    "Vag": {POS: AUX, "VerbForm": "Ger"},
    "Vaii3p": {
        "Mood": "Ind",
        "Number": "Plur",
        POS: AUX,
        "Person": "three",
        "Tense": "Imp",
        "VerbForm": "Fin",
    },
    "Vaii3s": {
        "Mood": "Ind",
        "Number": "Sing",
        POS: AUX,
        "Person": "three",
        "Tense": "Imp",
        "VerbForm": "Fin",
    },
    "Vail3s": {
        "Mood": "Ind",
        "Number": "Sing",
        POS: AUX,
        "Person": "three",
        
        "VerbForm": "Fin",
    },
    "Vaip1s": {
        "Mood": "Ind",
        "Number": "Sing",
        POS: AUX,
        "Person": "one",
        "Tense": "Pres",
        "VerbForm": "Fin",
    },
    "Vaip2s": {
        "Mood": "Ind",
        "Number": "Sing",
        POS: AUX,
        "Person": "two",
        "Tense": "Pres",
        "VerbForm": "Fin",
    },
    "Vaip3p": {
        "Mood": "Ind",
        "Number": "Plur",
        POS: AUX,
        "Person": "three",
        "Tense": "Pres",
        "VerbForm": "Fin",
    },
    "Vaip3s": {
        "Mood": "Ind",
        "Number": "Sing",
        POS: AUX,
        "Person": "three",
        "Tense": "Pres",
        "VerbForm": "Fin",
    },
    "Vanp": {POS: AUX, "Tense": "Pres", "VerbForm": "Inf"},
    "Vap--sm": {"Gender": "Masc", "Number": "Sing", POS: AUX, "VerbForm": "Part"},
    "Vasp3": {
        "Mood": "Sub",
        POS: AUX,
        "Person": "three",
        "Tense": "Pres",
        "VerbForm": "Fin",
    },
    "Vmg": {POS: VERB, "VerbForm": "Ger"},
    "Vmg-------y": {POS: VERB,  "VerbForm": "Ger"},
    "Vmii1": {
        "Mood": "Ind",
        POS: VERB,
        "Person": "one",
        "Tense": "Imp",
        "VerbForm": "Fin",
    },
    "Vmii1-----y": {
        "Mood": "Ind",
        POS: VERB,
        "Person": "one",
        "Tense": "Imp",
        
        "VerbForm": "Fin",
    },
    "Vmii2p": {
        "Mood": "Ind",
        "Number": "Plur",
        POS: VERB,
        "Person": "two",
        "Tense": "Imp",
        "VerbForm": "Fin",
    },
    "Vmii2s": {
        "Mood": "Ind",
        "Number": "Sing",
        POS: VERB,
        "Person": "two",
        "Tense": "Imp",
        "VerbForm": "Fin",
    },
    "Vmii3p": {
        "Mood": "Ind",
        "Number": "Plur",
        POS: VERB,
        "Person": "three",
        "Tense": "Imp",
        "VerbForm": "Fin",
    },
    "Vmii3p----y": {
        "Mood": "Ind",
        "Number": "Plur",
        POS: VERB,
        "Person": "three",
        "Tense": "Imp",
        
        "VerbForm": "Fin",
    },
    "Vmii3s": {
        "Mood": "Ind",
        "Number": "Sing",
        POS: VERB,
        "Person": "three",
        "Tense": "Imp",
        "VerbForm": "Fin",
    },
    "Vmil3p": {
        "Mood": "Ind",
        "Number": "Plur",
        POS: VERB,
        "Person": "three",
        
        "VerbForm": "Fin",
    },
    "Vmil3s": {
        "Mood": "Ind",
        "Number": "Sing",
        POS: VERB,
        "Person": "three",
        
        "VerbForm": "Fin",
    },
    "Vmip1p": {
        "Mood": "Ind",
        "Number": "Plur",
        POS: VERB,
        "Person": "one",
        "Tense": "Pres",
        "VerbForm": "Fin",
    },
    "Vmip1s": {
        "Mood": "Ind",
        "Number": "Sing",
        POS: VERB,
        "Person": "one",
        "Tense": "Pres",
        "VerbForm": "Fin",
    },
    "Vmip1s----y": {
        "Mood": "Ind",
        "Number": "Sing",
        POS: VERB,
        "Person": "one",
        "Tense": "Pres",
        
        "VerbForm": "Fin",
    },
    "Vmip2p": {
        "Mood": "Ind",
        "Number": "Plur",
        POS: VERB,
        "Person": "two",
        "Tense": "Pres",
        "VerbForm": "Fin",
    },
    "Vmip2s": {
        "Mood": "Ind",
        "Number": "Sing",
        POS: VERB,
        "Person": "two",
        "Tense": "Pres",
        "VerbForm": "Fin",
    },
    "Vmip3": {
        "Mood": "Ind",
        POS: VERB,
        "Person": "three",
        "Tense": "Pres",
        "VerbForm": "Fin",
    },
    "Vmip3-----y": {
        "Mood": "Ind",
        POS: VERB,
        "Person": "three",
        "Tense": "Pres",
        
        "VerbForm": "Fin",
    },
    "Vmip3p": {
        "Mood": "Ind",
        "Number": "Plur",
        POS: AUX,
        "Person": "three",
        "Tense": "Pres",
        "VerbForm": "Fin",
    },
    "Vmip3s": {
        "Mood": "Ind",
        "Number": "Sing",
        POS: VERB,
        "Person": "three",
        "Tense": "Pres",
        "VerbForm": "Fin",
    },
    "Vmip3s----y": {
        "Mood": "Ind",
        "Number": "Sing",
        POS: AUX,
        "Person": "three",
        "Tense": "Pres",
        
        "VerbForm": "Fin",
    },
    "Vmis1p": {
        "Mood": "Ind",
        "Number": "Plur",
        POS: VERB,
        "Person": "one",
        "Tense": "Past",
        "VerbForm": "Fin",
    },
    "Vmis1s": {
        "Mood": "Ind",
        "Number": "Sing",
        POS: VERB,
        "Person": "one",
        "Tense": "Past",
        "VerbForm": "Fin",
    },
    "Vmis3p": {
        "Mood": "Ind",
        "Number": "Plur",
        POS: VERB,
        "Person": "three",
        "Tense": "Past",
        "VerbForm": "Fin",
    },
    "Vmis3s": {
        "Mood": "Ind",
        "Number": "Sing",
        POS: VERB,
        "Person": "three",
        "Tense": "Past",
        "VerbForm": "Fin",
    },
    "Vmm-2p": {
        "Mood": "Imp",
        "Number": "Plur",
        POS: VERB,
        "Person": "two",
        "VerbForm": "Fin",
    },
    "Vmm-2s": {
        "Mood": "Imp",
        "Number": "Sing",
        POS: VERB,
        "Person": "two",
        "VerbForm": "Fin",
    },
    "Vmnp": {POS: VERB, "Tense": "Pres", "VerbForm": "Inf"},
    "Vmp--pf": {"Gender": "Fem", "Number": "Plur", POS: VERB, "VerbForm": "Part"},
    "Vmp--pm": {"Gender": "Masc", "Number": "Plur", POS: VERB, "VerbForm": "Part"},
    "Vmp--sf": {"Gender": "Fem", "Number": "Sing", POS: VERB, "VerbForm": "Part"},
    "Vmp--sm": {"Gender": "Masc", "Number": "Sing", POS: VERB, "VerbForm": "Part"},
    "Vmsp3": {
        "Mood": "Sub",
        POS: VERB,
        "Person": "three",
        "Tense": "Pres",
        "VerbForm": "Fin",
    },
    "Vmsp3-----y": {
        "Mood": "Sub",
        POS: VERB,
        "Person": "three",
        "Tense": "Pres",
        
        "VerbForm": "Fin",
    },
    "X": {POS: X},
    "Y": {"Abbr": "Yes", POS: X},
    "Yn": {"Abbr": "Yes", POS: NOUN},
    "Ynmsry": {
        "Abbr": "Yes",
        
        "Gender": "Masc",
        "Number": "Sing",
        POS: NOUN,
    },
}
