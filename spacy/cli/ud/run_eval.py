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
    ud_eng = 'UD_English-ESL'
    ud_eng_path = os.path.join(ud_location, ud_eng)
    train_file = os.path.join(ud_eng_path, 'en_esl-ud-train.txt')
    if conllu:
        train_file = os.path.join(ud_eng_path, 'en_esl-ud-train.conllu')

    if get_file:
        return open(train_file, 'r', encoding='utf-8')

    with open(train_file, 'r', encoding='utf-8') as fin:
        data = fin.read()

    return data


def time_load_model(modelname):
    """ Load and time a specific model """
    start = time.time()
    model = spacy.load(modelname)
    end = time.time()
    return end - start, model


def get_english_model():
    """ Load and time a generic English model """
    start = time.time()
    from spacy.lang.en import English
    nlp = English()
    nlp.add_pipe(nlp.create_pipe('sentencizer'))
    end = time.time()
    return end - start, nlp


def split_text(text):
    return [space_re.sub(" ", par.strip()) for par in text.split("\n\n")]


def eval(nlp, text, gold_file, sys_loc):
    texts = split_text(text)
    docs = list(nlp.pipe(texts))
    with open(sys_loc, "w", encoding="utf8") as out_file:
        write_conllu(docs, out_file)
    gold_ud = conll17_ud_eval.load_conllu(gold_file)
    with open(sys_loc, "r", encoding="utf8") as sys_file:
        sys_ud = conll17_ud_eval.load_conllu(sys_file)
    scores = conll17_ud_eval.evaluate(gold_ud, sys_ud)
    return docs, scores


if __name__ == "__main__":
    time_diff, nlp = time_load_model(modelname='en_core_web_sm')
    # time_diff, nlp = get_english_model()

    print(" --> Loading model name {} took {} seconds: {}".format("en_core_web_sm", time_diff, nlp))

    output_path = os.path.join(os.path.dirname(__file__), 'nlp_output.conllu')

    docs, myscores = eval(nlp,
                          read_english_training(conllu=False, get_file=False),
                          read_english_training(conllu=True, get_file=True),
                          output_path)

    # print("docs", docs)
    for score_name, score in myscores.items():
        print(score_name)
        print(" p", score.precision)
        print(" r", score.recall)
        print(" F", score.f1)
        print(" acc", score.aligned_accuracy)
        print()
