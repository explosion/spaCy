import spacy
import time
import re
import plac
import operator
import datetime
from pathlib import Path
import xml.etree.ElementTree as ET

import conll17_ud_eval
from ud_train import write_conllu
from spacy.lang.lex_attrs import word_shape
from spacy.util import get_lang_class

# All languages in spaCy - in UD format (note that Norwegian is 'no' instead of 'nb')
ALL_LANGUAGES = ("af, ar, bg, bn, ca, cs, da, de, el, en, es, et, fa, fi, fr,"
                 "ga, he, hi, hr, hu, id, is, it, ja, kn, ko, lt, lv, mr, no,"
                 "nl, pl, pt, ro, ru, si, sk, sl, sq, sr, sv, ta, te, th, tl,"
                 "tr, tt, uk, ur, vi, zh")

# Non-parsing tasks that will be evaluated (works for default models)
EVAL_NO_PARSE = ['Tokens', 'Words', 'Lemmas', 'Sentences', 'Feats']

# Tasks that will be evaluated if check_parse=True (does not work for default models)
EVAL_PARSE = ['Tokens', 'Words', 'Lemmas', 'Sentences', 'Feats', 'UPOS', 'XPOS', 'AllTags', 'UAS', 'LAS']

# Minimum frequency an error should have to be printed
PRINT_FREQ = 20

# Maximum number of errors printed per category
PRINT_TOTAL = 10

space_re = re.compile("\s+")


def load_model(modelname, add_sentencizer=False):
    """ Load a specific spaCy model """
    loading_start = time.time()
    nlp = spacy.load(modelname)
    if add_sentencizer:
        nlp.add_pipe(nlp.create_pipe('sentencizer'))
    loading_end = time.time()
    loading_time = loading_end - loading_start
    if add_sentencizer:
        return nlp, loading_time, modelname + '_sentencizer'
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


def split_text(text):
    return [space_re.sub(" ", par.strip()) for par in text.split("\n\n")]


def get_freq_tuples(my_list, print_total_threshold):
    """ Turn a list of errors into frequency-sorted tuples thresholded by a certain total number """
    d = {}
    for token in my_list:
        d.setdefault(token, 0)
        d[token] += 1
    return sorted(d.items(), key=operator.itemgetter(1), reverse=True)[:print_total_threshold]


def _contains_blinded_text(stats_xml):
    """ Heuristic to determine whether the treebank has blinded texts or not """
    tree = ET.parse(stats_xml)
    root = tree.getroot()
    total_tokens = int(root.find('size/total/tokens').text)
    unique_forms = int(root.find('forms').get('unique'))

    # assume the corpus is largely blinded when there are less than 1% unique tokens
    return (unique_forms / total_tokens) < 0.01


def fetch_all_treebanks(ud_dir, languages, corpus, best_per_language):
    """" Fetch the txt files for all treebanks for a given set of languages """
    all_treebanks = dict()
    treebank_size = dict()
    for l in languages:
        all_treebanks[l] = []
        treebank_size[l] = 0

    for treebank_dir in ud_dir.iterdir():
        if treebank_dir.is_dir():
            for txt_path in treebank_dir.iterdir():
                if txt_path.name.endswith('-ud-' + corpus + '.txt'):
                    file_lang = txt_path.name.split('_')[0]
                    if file_lang in languages:
                        gold_path = treebank_dir / txt_path.name.replace('.txt', '.conllu')
                        stats_xml = treebank_dir / "stats.xml"
                        # ignore treebanks where the texts are not publicly available
                        if not _contains_blinded_text(stats_xml):
                            if not best_per_language:
                                all_treebanks[file_lang].append(txt_path)
                            # check the tokens in the gold annotation to keep only the biggest treebank per language
                            else:
                                with gold_path.open(mode='r', encoding='utf-8') as gold_file:
                                    gold_ud = conll17_ud_eval.load_conllu(gold_file)
                                    gold_tokens = len(gold_ud.tokens)
                                if treebank_size[file_lang] < gold_tokens:
                                    all_treebanks[file_lang] = [txt_path]
                                    treebank_size[file_lang] = gold_tokens

    return all_treebanks


def run_single_eval(nlp, loading_time, print_name, text_path, gold_ud, tmp_output_path, out_file, print_header,
                    check_parse, print_freq_tasks):
    """" Run an evaluation of a model nlp on a certain specified treebank """
    with text_path.open(mode='r', encoding='utf-8') as f:
        flat_text = f.read()

    # STEP 1: tokenize text
    tokenization_start = time.time()
    texts = split_text(flat_text)
    docs = list(nlp.pipe(texts))
    tokenization_end = time.time()
    tokenization_time = tokenization_end - tokenization_start

    # STEP 2: record stats and timings
    tokens_per_s = int(len(gold_ud.tokens) / tokenization_time)

    print_header_1 = ['date', 'text_path', 'gold_tokens', 'model', 'loading_time', 'tokenization_time', 'tokens_per_s']
    print_string_1 = [str(datetime.date.today()), text_path.name, len(gold_ud.tokens),
                      print_name, "%.2f" % loading_time, "%.2f" % tokenization_time, tokens_per_s]

    # STEP 3: evaluate predicted tokens and features
    with tmp_output_path.open(mode="w", encoding="utf8") as tmp_out_file:
        write_conllu(docs, tmp_out_file)
    with tmp_output_path.open(mode="r", encoding="utf8") as sys_file:
        sys_ud = conll17_ud_eval.load_conllu(sys_file, check_parse=check_parse)
    tmp_output_path.unlink()
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
        print_string_1.append("-" if score.undersegmented is None else "%.4f" % score.under_perc)
        print_string_1.append("-" if score.oversegmented is None else "%.4f" % score.over_perc)

        print_header_1.extend([score_name + '_p', score_name + '_r', score_name + '_F', score_name + '_acc',
                               score_name + '_under', score_name + '_over'])

        if score_name in print_freq_tasks:
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
        out_file.write(';'.join(map(str, print_header_1)) + '\n')
    out_file.write(';'.join(map(str, print_string_1)) + '\n')


def run_all_evals(models, treebanks, out_file, check_parse, print_freq_tasks):
    """" Run an evaluation for each language with its specified models and treebanks """
    print_header = True

    for tb_lang, treebank_list in treebanks.items():
        print()
        print("Language", tb_lang)
        for text_path in treebank_list:
            print(" Evaluating on", text_path)

            gold_path = text_path.parent / (text_path.stem + '.conllu')
            print("  Gold data from ", gold_path)

            # nested try blocks to ensure the code can continue with the next iteration after a failure
            try:
                with gold_path.open(mode='r', encoding='utf-8') as gold_file:
                    gold_ud = conll17_ud_eval.load_conllu(gold_file)

                for nlp, nlp_loading_time, nlp_name in models[tb_lang]:
                    try:
                        print("   Benchmarking", nlp_name)
                        tmp_output_path = text_path.parent / str('tmp_' + nlp_name + '.conllu')
                        run_single_eval(nlp, nlp_loading_time, nlp_name, text_path, gold_ud, tmp_output_path, out_file,
                                        print_header, check_parse, print_freq_tasks)
                        print_header = False
                    except Exception as e:
                        print("    Ran into trouble: ", str(e))
            except Exception as e:
                print("   Ran into trouble: ", str(e))


@plac.annotations(
    out_path=("Path to output CSV file", "positional", None, Path),
    ud_dir=("Path to Universal Dependencies corpus", "positional", None, Path),
    check_parse=("Set flag to evaluate parsing performance", "flag", "p", bool),
    langs=("Enumeration of languages to evaluate (default: all)", "option", "l", str),
    exclude_trained_models=("Set flag to exclude trained models", "flag", "t", bool),
    exclude_multi=("Set flag to exclude the multi-language model as default baseline", "flag", "m", bool),
    hide_freq=("Set flag to avoid printing out more detailed high-freq tokenization errors", "flag", "f", bool),
    corpus=("Whether to run on train, dev or test", "option", "c", str),
    best_per_language=("Set flag to only keep the largest treebank for each language", "flag", "b", bool)
)
def main(out_path, ud_dir, check_parse=False, langs=ALL_LANGUAGES, exclude_trained_models=False, exclude_multi=False,
         hide_freq=False, corpus='train', best_per_language=False):
    """"
    Assemble all treebanks and models to run evaluations with.
    When setting check_parse to True, the default models will not be evaluated as they don't have parsing functionality
    """
    languages = [lang.strip() for lang in langs.split(",")]

    print_freq_tasks = []
    if not hide_freq:
        print_freq_tasks = ['Tokens']

    # fetching all relevant treebank from the directory
    treebanks = fetch_all_treebanks(ud_dir, languages, corpus, best_per_language)

    print()
    print("Loading all relevant models for", languages)
    models = dict()

    # multi-lang model
    multi = None
    if not exclude_multi and not check_parse:
        multi = load_model('xx_ent_wiki_sm', add_sentencizer=True)

    # initialize all models with the multi-lang model
    for lang in languages:
        models[lang] = [multi] if multi else []
        # add default models if we don't want to evaluate parsing info
        if not check_parse:
            # Norwegian is 'nb' in spaCy but 'no' in the UD corpora
            if lang == 'no':
                models['no'].append(load_default_model_sentencizer('nb'))
            else:
                models[lang].append(load_default_model_sentencizer(lang))

    # language-specific trained models
    if not exclude_trained_models:
        if 'de' in models:
            models['de'].append(load_model('de_core_news_sm'))
            models['de'].append(load_model('de_core_news_md'))
        if 'el' in models:
            models['el'].append(load_model('el_core_news_sm'))
            models['el'].append(load_model('el_core_news_md'))
        if 'en' in models:
            models['en'].append(load_model('en_core_web_sm'))
            models['en'].append(load_model('en_core_web_md'))
            models['en'].append(load_model('en_core_web_lg'))
        if 'es' in models:
            models['es'].append(load_model('es_core_news_sm'))
            models['es'].append(load_model('es_core_news_md'))
        if 'fr' in models:
            models['fr'].append(load_model('fr_core_news_sm'))
            models['fr'].append(load_model('fr_core_news_md'))
        if 'it' in models:
            models['it'].append(load_model('it_core_news_sm'))
        if 'nl' in models:
            models['nl'].append(load_model('nl_core_news_sm'))
        if 'pt' in models:
            models['pt'].append(load_model('pt_core_news_sm'))

    with out_path.open(mode='w', encoding='utf-8') as out_file:
        run_all_evals(models, treebanks, out_file, check_parse, print_freq_tasks)


if __name__ == "__main__":
    plac.call(main)
