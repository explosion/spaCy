import os
import spacy
import time
import re

from spacy.cli.ud import conll17_ud_eval
from spacy.cli.ud.ud_train import write_conllu

# TODO: remove hardcoded path
ud_location = os.path.join('C:', os.sep, 'Users', 'Sofie', 'Documents', 'data', 'UD_2_3', 'ud-treebanks-v2.3')

space_re = re.compile("\s+")


def read_english_training(conllu=False, get_file=False):
    # English treebanks: ESL, EWT, GUM, LinES, ParTUT, PUD
    # ESL does not contain the actual texts, PUD does not contain a train/dev portion
    # EWT is the biggest one, ParTUT is the only one with fusion tokens
    english_treebank = "EWT"

    ud_eng_path = os.path.join(ud_location, 'UD_English-' + english_treebank)
    train_file = os.path.join(ud_eng_path, 'en_' + english_treebank.lower() + '-ud-train.txt')
    if conllu:
        train_file = train_file.replace('.txt', '.conllu')

    if get_file:
        return open(train_file, 'r', encoding='utf-8')

    with open(train_file, 'r', encoding='utf-8') as fin:
        data = fin.read()

    return data


def load_model(modelname):
    """ Load a specific model """
    return spacy.load(modelname)


def load_english_model():
    """ Load a generic English model """
    from spacy.lang.en import English
    nlp = English()
    nlp.add_pipe(nlp.create_pipe('sentencizer'))
    return nlp


def split_text(text):
    return [space_re.sub(" ", par.strip()) for par in text.split("\n\n")]


if __name__ == "__main__":

    # STEP 0 : loading raw text
    flat_text = read_english_training(conllu=False, get_file=False)

    # STEP 1: load model
    start = time.time()
    nlp = load_model(modelname='en_core_web_sm')
    # load_english_model()
    end_loading = time.time()
    loading_time = end_loading - start

    # STEP 2: tokenize text
    texts = split_text(flat_text)
    docs = list(nlp.pipe(texts))
    end_tokenization = time.time()
    tokenization_time = end_tokenization - end_loading

    # STEP 3: write and evaluate predicted tokenization
    output_path = os.path.join(os.path.dirname(__file__), 'nlp_output.conllu')
    with open(output_path, "w", encoding="utf8") as out_file:
        write_conllu(docs, out_file)
    gold_file = read_english_training(conllu=True, get_file=True)
    gold_ud = conll17_ud_eval.load_conllu(gold_file)
    with open(output_path, "r", encoding="utf8") as sys_file:
        sys_ud = conll17_ud_eval.load_conllu(sys_file)
    scores = conll17_ud_eval.evaluate(gold_ud, sys_ud)

    for score_name, score in scores.items():
        print(score_name)
        print(" p", score.precision)
        print(" r", score.recall)
        print(" F", score.f1)
        print(" acc", score.aligned_accuracy)
        print()

    print("word number in gold:", len(gold_ud.words))
    print("token number in gold:", len(gold_ud.tokens))
    print()
    print("Loading model took {} seconds: {}".format(loading_time, nlp))
    print("Tokenizing text took {} seconds: {}".format(tokenization_time, nlp))
    print(" which is {} tokens per second".format(len(gold_ud.tokens) / tokenization_time))
