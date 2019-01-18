import os
import spacy
import time
import re
import operator
import datetime

from spacy.cli.ud import conll17_ud_eval
from spacy.cli.ud.ud_train import write_conllu
from spacy.lang.lex_attrs import word_shape
from spacy.util import get_lang_class

# Non-parsing tasks that will be evaluated (works for default models)
EVAL_NO_PARSE = ['Tokens', 'Words', 'Lemmas', 'Sentences', 'Feats']

# Tasks that will be evaluated if check_parse=True and there are no default models in the list
EVAL_PARSE = ['Tokens', 'Words', 'Lemmas', 'Sentences', 'Feats', 'UPOS', 'XPOS', 'AllTags', 'UAS', 'LAS']

# Tasks for which to print high-freq error cases. Includes verbose output!
PRINT_ERROR_EXAMPLES = []  # ['Tokens']

# Minimum frequency an error should have to be printed
PRINT_FREQ = 5

# Maximum number of errors printed per category
PRINT_TOTAL = 10

space_re = re.compile("\s+")


def load_model(modelname):
    """ Load a specific spaCy model """
    loading_start = time.time()
    nlp = spacy.load(modelname)
    loading_end = time.time()
    loading_time = loading_end - loading_start
    return nlp, loading_time, modelname


def load_default_model_sentencizer(lang):
    """ Load a generic spaCy model and add the sentencizer for sentence tokenization"""
    loading_start = time.time()
    lang_class = get_lang_class(lang)
    nlp = lang_class()
    nlp.add_pipe(nlp.create_pipe('sentencizer'))
    loading_end = time.time()
    loading_time = loading_end - loading_start
    return nlp, loading_time, lang + "_default_" + 'sentencizer'


def get_long_lang(lang):
    """" Helper method to compile the UD path for a certain treebank """
    if lang == 'en':
        return "English"
    if lang == 'fr':
        return "French"
    return "Unknown"


def split_text(text):
    return [space_re.sub(" ", par.strip()) for par in text.split("\n\n")]


def get_freq_tuples(my_list, print_total_threshold):
    """ Turn a list of errors into frequency-sorted tuples thresholded by a certain total number """
    d = {}
    for token in my_list:
        d.setdefault(token, 0)
        d[token] += 1
    return sorted(d.items(), key=operator.itemgetter(1), reverse=True)[:print_total_threshold]


def run_single_eval(nlp, loading_time, print_name, train_path, gold_ud, tmp_output_path, file, print_header):
    """" Run an evaluation of a model nlp on a certain specified treebank """
    with open(train_path, 'r', encoding='utf-8') as fin:
        flat_text = fin.read()

    # STEP 1: tokenize text
    tokenization_start = time.time()
    texts = split_text(flat_text)
    docs = list(nlp.pipe(texts))
    tokenization_end = time.time()
    tokenization_time = tokenization_end - tokenization_start

    # STEP 2: record stats and timings
    tokens_per_s = int(len(gold_ud.tokens) / tokenization_time)

    print_header_1 = ['date', 'train_path', 'gold_tokens', 'model', 'loading_time', 'tokenization_time', 'tokens_per_s']
    print_string_1 = [str(datetime.date.today()), os.path.basename(train_path), len(gold_ud.tokens),
                      print_name, "%.2f" % loading_time, "%.2f" % tokenization_time, tokens_per_s]

    # STEP 3: evaluate predicted tokens and features
    with open(tmp_output_path, "w", encoding="utf8") as out_file:
        write_conllu(docs, out_file)
    with open(tmp_output_path, "r", encoding="utf8") as sys_file:
        sys_ud = conll17_ud_eval.load_conllu(sys_file, check_parse=check_parse)
    os.remove(tmp_output_path)
    scores = conll17_ud_eval.evaluate(gold_ud, sys_ud, check_parse=check_parse)

    # STEP 4: format the scoring results
    eval_headers = EVAL_PARSE
    if not check_parse:
        eval_headers = EVAL_NO_PARSE

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

        if score_name in PRINT_ERROR_EXAMPLES:
            print_header_1.extend([score_name + '_word_under_ex', score_name + '_shape_under_ex',
                                   score_name + '_word_over_ex', score_name + '_shape_over_ex'])

            d_under_words = get_freq_tuples(score.undersegmented, PRINT_TOTAL)
            d_under_shapes = get_freq_tuples([word_shape(x) for x in score.undersegmented], PRINT_TOTAL)
            d_over_words = get_freq_tuples(score.oversegmented, PRINT_TOTAL)
            d_over_shapes = get_freq_tuples([word_shape(x) for x in score.oversegmented], PRINT_TOTAL)

            # saving to CSV with ; seperator so blinding ; in the example output
            print_string_1.append(
                str({k: v for k, v in d_under_words if v > PRINT_FREQ}).replace(";", "*SEMICOLON*"))
            print_string_1.append(
                str({k: v for k, v in d_under_shapes if v > PRINT_FREQ}).replace(";", "*SEMICOLON*"))
            print_string_1.append(
                str({k: v for k, v in d_over_words if v > PRINT_FREQ}).replace(";", "*SEMICOLON*"))
            print_string_1.append(
                str({k: v for k, v in d_over_shapes if v > PRINT_FREQ}).replace(";", "*SEMICOLON*"))

    # STEP 5: print the formatted results to CSV
    if print_header:
        file.write(';'.join(map(str, print_header_1)) + '\n')
    file.write(';'.join(map(str, print_string_1)) + '\n')


def main(models, treebanks, file):
    """" Run an evaluation for each language with its specified models and treebanks """
    my_tmp_output_path = os.path.join(os.path.dirname(__file__), 'tmp_nlp_output.conllu')
    print_header = True

    for tb_lang, treebank_list in treebanks.items():
        print()
        print("Language", tb_lang)
        for treebank in treebank_list:
            ud_path = os.path.join(my_ud_folder, 'UD_' + get_long_lang(tb_lang) + '-' + treebank)
            train_path = os.path.join(ud_path, tb_lang + '_' + treebank.lower() + '-ud-train.txt')
            print(" Evaluating on", train_path)

            gold_path = train_path.replace('.txt', '.conllu')
            print("  Gold data from ", gold_path)

            try:
                with open(gold_path, 'r', encoding='utf-8') as gold_file:
                    gold_ud = conll17_ud_eval.load_conllu(gold_file)

                for nlp, nlp_loading_time, nlp_name in models[tb_lang]:
                    print("   Benchmarking", nlp_name)

                    run_single_eval(nlp, nlp_loading_time, nlp_name, train_path, gold_ud, my_tmp_output_path, file,
                                    print_header)
                    print_header = False
            except Exception as e:
                print("   Ran into trouble: ", str(e))


if __name__ == "__main__":
    """" Hardcoded setting for a quick batch run """
    my_ud_folder = os.path.join('C:', os.sep, 'Users', 'Sofie', 'Documents', 'data', 'UD_2_3', 'ud-treebanks-v2.3')

    my_treebanks = dict()
    # Note: 'PUD' doesn't have training data
    # Note: 'FTB' and 'ESL' have blinded text
    my_treebanks['en'] = ['EWT', 'GUM', 'LinES', 'ParTUT']  # 'ESL', 'PUD'
    my_treebanks['fr'] = ['GSD', 'ParTUT', 'Sequoia', 'Spoken']  # 'FTB', 'PUD'

    # When set to True, remove the default models from the list as they don't have parsing functionality
    check_parse = False

    print("Loading all models")
    my_models = dict()
    my_models['en'] = [
        load_default_model_sentencizer('en'),
        load_model('en_core_web_sm')]  # ,
    # (load_model('en_core_web_md'), 'en_core_web_md'),
    # (load_model('en_core_web_lg'), 'en_core_web_lg')]

    my_models['fr'] = [
        load_default_model_sentencizer('fr')]  # ,
    # (load_model('fr_core_news_sm'), 'fr_core_news_sm'),
    # (load_model('fr_core_news_md'), 'fr_core_news_md')]

    fname = os.path.join(os.path.dirname(__file__), 'output.csv')
    with open(fname, 'w', encoding='utf-8') as my_file:  # , 'a'
        main(my_models, my_treebanks, my_file)
