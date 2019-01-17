import os
import spacy
import time
import re
import operator
import datetime

from spacy.cli.ud import conll17_ud_eval
from spacy.cli.ud.ud_train import write_conllu
from spacy.lang.lex_attrs import word_shape

ud_version = '2.3'

check_parse = False
print_freq_threshold = 5  # minimum frequency an error should have to be printed
print_total_threshold = 10  # maximum number of errors printed per category

space_re = re.compile("\s+")


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


def get_long_lang(lang):
    if lang == 'en':
        return "English"
    if lang == 'fr':
        return "French"
    return "Unknown"


# TODO: remove this ?
def split_text(text):
    return [space_re.sub(" ", par.strip()) for par in text.split("\n\n")]


def get_freq_tuples(my_list, print_total_threshold):
    d = {}
    for token in my_list:
        d.setdefault(token, 0)
        d[token] += 1
    return sorted(d.items(), key=operator.itemgetter(1), reverse=True)[:print_total_threshold]


def run_single_eval(nlp, model_print_name, train_path, gold_ud, tmp_output_path, file, print_header):
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

    print_header_1 = ['date', 'train_path', 'gold_tokens', 'model', 'tokenization_time', 'tokens_per_s']
    print_string_1 = [str(datetime.date.today()), os.path.basename(train_path) + ' ' + ud_version, len(gold_ud.tokens),
                      model_print_name,
                      "%.2f" % tokenization_time, tokens_per_s]

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

            print_string_1.append(
                str({k: v for k, v in d_under_words if v > print_freq_threshold}).replace(";", "*SEMICOLON*"))
            print_string_1.append(
                str({k: v for k, v in d_under_shapes if v > print_freq_threshold}).replace(";", "*SEMICOLON*"))
            print_string_1.append(
                str({k: v for k, v in d_over_words if v > print_freq_threshold}).replace(";", "*SEMICOLON*"))
            print_string_1.append(
                str({k: v for k, v in d_over_shapes if v > print_freq_threshold}).replace(";", "*SEMICOLON*"))

    # STEP 5: print the results
    if print_header:
        file.write(';'.join(map(str, print_header_1)) + '\n')
    file.write(';'.join(map(str, print_string_1)) + '\n')


def main(models, treebanks, file):
    my_tmp_output_path = os.path.join(os.path.dirname(__file__), 'nlp_output_english.conllu')
    print_header = True

    for tb_lang, treebank_list in treebanks.items():
        print("Language", tb_lang)
        for treebank in treebank_list:
            ud_path = os.path.join(my_ud_folder, 'UD_' + get_long_lang(tb_lang) + '-' + treebank)
            train_path = os.path.join(ud_path, tb_lang + '_' + treebank.lower() + '-ud-train.txt')
            print(" Evaluating on", train_path)

            gold_path = train_path.replace('.txt', '.conllu')
            print("  Gold data from ", gold_path)

            with open(gold_path, 'r', encoding='utf-8') as gold_file:
                gold_ud = conll17_ud_eval.load_conllu(gold_file)

            for nlp, nlp_name in models[tb_lang]:
                print("   Benchmarking", nlp_name)
                try:
                    run_single_eval(nlp, nlp_name, train_path, gold_ud, my_tmp_output_path, file, print_header)
                    print_header = False
                except Exception as e:
                    print("    Ran into trouble: ", str(e))


if __name__ == "__main__":
    my_ud_folder = os.path.join('C:', os.sep, 'Users', 'Sofie', 'Documents', 'data', 'UD_2_3', 'ud-treebanks-v2.3')

    treebanks = dict()
    treebanks['en'] = ['ESL', 'EWT', 'GUM', 'LinES', 'ParTUT', 'PUD']
    treebanks['fr'] = ['FTB', 'GSD', 'ParTUT', 'PUD', 'Sequoia', 'Spoken']

    my_models = dict()
    my_models['en'] = [
        (load_english_model(), 'English + sentencizer'),
        (load_model('en_core_web_sm'), 'en_core_web_sm'),
        (load_model('en_core_web_md'), 'en_core_web_md'),
        (load_model('en_core_web_lg'), 'en_core_web_lg')]

    my_models['fr'] = [
        (load_french_model(), 'French + sentencizer'),
        (load_model('fr_core_news_sm'), 'fr_core_news_sm'),
        (load_model('fr_core_news_md'), 'fr_core_news_md')]

    fname = os.path.join(os.path.dirname(__file__), 'output.csv')
    with open(fname, 'w') as my_file:  # , 'a'
        main(my_models, treebanks, my_file)
