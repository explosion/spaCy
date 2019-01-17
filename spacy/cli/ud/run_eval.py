import os
import spacy
import time
import re
import operator
import datetime

from spacy.cli.ud import conll17_ud_eval
from spacy.cli.ud.ud_train import write_conllu
from spacy.lang.lex_attrs import word_shape

# TODO: remove hardcoded path
ud_location = os.path.join('C:', os.sep, 'Users', 'Sofie', 'Documents', 'data', 'UD_2_3', 'ud-treebanks-v2.3')
ud_version = '2.3'
ud_folder = 'UD_English-'
ud_lang = 'en_'

space_re = re.compile("\s+")


def get_training_path(treebank, conllu=False):
    ud_path = os.path.join(ud_location, ud_folder + treebank)
    train_file = os.path.join(ud_path, ud_lang + treebank.lower() + '-ud-train.txt')
    if conllu:
        train_file = train_file.replace('.txt', '.conllu')
    return train_file


def load_model(modelname):
    """ Load a specific model """
    return spacy.load(modelname)


def load_english_model():
    """ Load a generic English model """
    from spacy.lang.en import English
    nlp = English()
    nlp.add_pipe(nlp.create_pipe('sentencizer'))
    return nlp


def load_french_model():
    """ Load a generic French model """
    from spacy.lang.fr import French
    nlp = French()
    nlp.add_pipe(nlp.create_pipe('sentencizer'))
    return nlp


def split_text(text):
    return [space_re.sub(" ", par.strip()) for par in text.split("\n\n")]


def get_freq_tuples(my_list, print_total_threshold):
    d = {}
    for token in my_list:
        d.setdefault(token, 0)
        d[token] += 1
    return sorted(d.items(), key=operator.itemgetter(1), reverse=True)[:print_total_threshold]


def run_single_eval(nlp, model_print_name, train_path, gold_ud, tmp_output_path):
    with open(train_path, 'r', encoding='utf-8') as fin:
        flat_text = fin.read()

    # STEP 2: tokenize text
    tokenization_start = time.time()
    texts = split_text(flat_text)
    docs = list(nlp.pipe(texts))
    tokenization_end = time.time()
    tokenization_time = tokenization_end - tokenization_start

    # STEP 3: record stats and timings
    tokens_per_s = int(len(gold_ud.tokens) / tokenization_time)

    print_header_1 = ['date', 'train_path', 'gold_tokens', 'model', 'loading_time', 'tokenization_time', 'tokens_per_s']
    print_string_1 = [str(datetime.date.today()), os.path.basename(train_path) + ' ' + ud_version, len(gold_ud.tokens), model_print_name,
                      "%.2f" % loading_time, "%.2f" % tokenization_time, tokens_per_s]

    # STEP 4: evaluate predicted tokens and features
    # TODO Sofie: do we need a tmp file ?!
    with open(tmp_output_path, "w", encoding="utf8") as out_file:
        write_conllu(docs, out_file)
    with open(tmp_output_path, "r", encoding="utf8") as sys_file:
        sys_ud = conll17_ud_eval.load_conllu(sys_file, check_parse=check_parse)
    scores = conll17_ud_eval.evaluate(gold_ud, sys_ud, check_parse=check_parse)

    # fixed order for normalized printing. don't print the last few columns if we don't have a parse
    eval_headers = ['Tokens', 'Words', 'Lemmas', 'Sentences', 'Feats', 'UPOS', 'XPOS', 'AllTags', 'UAS', 'LAS']
    if not check_parse:
        eval_headers = ['Tokens', 'Words', 'Lemmas', 'Sentences', 'Feats']
    for score_name in eval_headers:
        score = scores[score_name]
        print_string_1.extend(["%.2f" % score.precision,
                               "%.2f" % score.recall,
                               "%.2f" % score.f1])
        print_string_1.append("-" if score.aligned_accuracy is None else "%.2f" % score.aligned_accuracy)
        print_string_1.append("-" if score.undersegmented is None else len(score.undersegmented))
        print_string_1.append("-" if score.oversegmented is None else len(score.oversegmented))

        print_header_1.extend([score_name + '_p', score_name + '_r', score_name + '_F', score_name + '_acc',
                               score_name + '_under', score_name + '_over'])

        if score_name == "Tokens":
            print_header_1.extend([score_name + '_word_under_ex', score_name + '_shape_under_ex',
                                   score_name + '_word_over_ex', score_name + '_shape_over_ex'])

            d_under_words = get_freq_tuples(score.undersegmented, print_total_threshold)
            d_under_shapes = get_freq_tuples([word_shape(x) for x in score.undersegmented], print_total_threshold)
            d_over_words = get_freq_tuples(score.oversegmented, print_total_threshold)
            d_over_shapes = get_freq_tuples([word_shape(x) for x in score.oversegmented], print_total_threshold)

            print_string_1.append(str({k: v for k, v in d_under_words if v > print_freq_threshold}).replace(";", "*SEMICOLON*"))
            print_string_1.append(str({k: v for k, v in d_under_shapes if v > print_freq_threshold}).replace(";", "*SEMICOLON*"))
            print_string_1.append(str({k: v for k, v in d_over_words if v > print_freq_threshold}).replace(";", "*SEMICOLON*"))
            print_string_1.append(str({k: v for k, v in d_over_shapes if v > print_freq_threshold}).replace(";", "*SEMICOLON*"))

    # STEP 5: print the results
    fname = os.path.join(os.path.dirname(__file__), 'output.csv')
    with open(fname, 'w') as file:       # , 'a'
        file.write(';'.join(map(str, print_header_1)) + '\n')
        file.write(';'.join(map(str, print_string_1)) + '\n')



def main(nlp_list, ud_folder, treebank_list):
    pass


if __name__ == "__main__":
    # RUN PARAMETERS
    run_eval = True
    # my_model = 'en_core_web_sm'
    # my_model = 'en_core_web_md'
    # my_model = 'en_core_web_lg'
    my_model = 'English'
    # my_model = 'French'

    check_parse = False
    print_freq_threshold = 5  # minimum frequency an error should have to be printed
    print_total_threshold = 10  # maximum number of errors printed per category

    # STEP 0 : loading raw text
    # English treebanks: ESL, EWT, GUM, LinES, ParTUT, PUD
    # ESL does not contain the actual texts, PUD does not contain a train/dev portion
    # EWT is the biggest one, ParTUT is the only one with fusion tokens
    my_treebank = "EWT"
    my_train_path = get_training_path(my_treebank, conllu=False)

    # STEP 1: load model
    start = time.time()
    # my_nlp = load_model(modelname=my_model)
    my_nlp = load_english_model()
    # my_nlp = load_french_model()
    end = time.time()
    loading_time = end - start

    gold_file = open(get_training_path(my_treebank, conllu=True), 'r', encoding='utf-8')
    my_gold_ud = conll17_ud_eval.load_conllu(gold_file)

    my_tmp_output_path = os.path.join(os.path.dirname(__file__), 'nlp_output_english.conllu')

    run_single_eval(my_nlp, my_model, my_train_path, my_gold_ud, my_tmp_output_path)


