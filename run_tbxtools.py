from lib.Med_Tagger import Med_Tagger
from lib.TBXTools import *
from shutil import copyfile
import getopt
import sys
import time


# HELPER FUNCTIONS


def format_input_to_brat(input_filepath, brat_filepath):
    '''Formats input to BRAT'''
    tag = Med_Tagger()  # Starts a docker image in background
    input_file = open(input_filepath, encoding='utf-8')
    input_text = input_file.read()
    input_file.close()
    input_parsed = tag.parse(input_text)
    tag.write_brat(input_text, input_parsed, brat_filepath)
    del (tag)  # To kill the docker image


def get_brat_tags(brat_filepath):
    '''Returns BRAT tags from brat text file'''
    brat_file = open(brat_filepath, encoding='utf-8')
    brat_tags = []
    for line in brat_file.readlines():
        if line.startswith('#'):
            continue
        elements = line.split('\t')
        type_span = elements[1].split()
        tag = {
            'start': type_span[1],
            'end': type_span[2],
            'token': elements[2].split('\n')[0]
        }
        brat_tags.append(tag)
    return brat_tags


def format_key_phrase(key_phrase):
    span = map(lambda t: '{0} {1}'.format(t[0], t[1]), key_phrase['span'])
    key_phrase['span'] = ';'.join(span)
    key_phrase['term'] = ' '.join(key_phrase['term'])
    return key_phrase


# MAIN FUNCTIONS


def process_input(input_filepath, output_filepath, mode):
    '''Extracts information from input'''
    print('--- Processing input ---')
    start_time = time.time()
    extractor = TBXTools()
    extractor.create_project('results/tbxtools/' + mode + '/corpus.sqlite', 'spa', overwrite=True)
    extractor.load_sl_corpus(input_filepath)
    if (mode == 'linguistic'):
        extractor.start_freeling_api('es')
        extractor.tag_freeling_api()
        extractor.save_sl_tagged_corpus('results/tbxtools/' + mode + '/corpus-tagged-spa.txt')
        extractor.load_linguistic_patterns('data/patterns-forms-spa.txt')
        extractor.tagged_ngram_calculation(nmin=2, nmax=3, minfreq=1)
        extractor.linguistic_term_extraction(minfreq=1)
    elif (mode == 'statistical'):
        extractor.ngram_calculation(nmin=2, nmax=3, minfreq=1)
        extractor.load_sl_stopwords('data/stop-spa.txt')
        extractor.statistical_term_extraction(minfreq=1)
        extractor.case_normalization(verbose=False)
        extractor.nest_normalization(verbose=False)
    extractor.save_term_candidates(output_filepath)
    end_time = time.time() - start_time
    print('--- {} seconds ---'.format(end_time))


def format_output(output_filepath, input_filepath, brat_filepath):
    '''Formats the original output to eHealth-KD subtask A output'''
    format_input_to_brat(input_filepath, brat_filepath)
    brat_tags = get_brat_tags(brat_filepath)
    output_file = open(output_filepath, encoding='utf-8')
    key_phrases = []
    for ln in output_file.readlines():
        # search the extracted concepts in BRAT text in order to get the span intervals
        ln = ln.split('\t')
        freq = int(ln[0])
        candidate_tokens = ln[1].split()
        i = 0
        j = 0
        k = 0
        key_phrase = {'span': [], 'term': []}
        while i < len(brat_tags) and j < freq:
            if k == len(candidate_tokens):  # multiword term found
                key_phrase['label'] = 'Concept'
                key_phrases.append(key_phrase)
                key_phrase = {'span': [], 'term': []}
                j += 1
                k = 0
            else:
                if candidate_tokens[k] == brat_tags[i]['token']:
                    key_phrase['span'].append((brat_tags[i]['start'], brat_tags[i]['end']))
                    key_phrase['term'].append(brat_tags[i]['token'])
                    k += 1
                else:
                    if (k > 0):
                        key_phrase = {'span': [], 'term': []}
                        k = 0
            i += 1
    output_file.close()
    key_phrases.sort(key=lambda k: int(k['span'][0][0]))
    key_phrases = map(format_key_phrase, key_phrases)
    return key_phrases


def print_output(keyphrases, keyphrases_filepath):
    key_phrases_file = open(keyphrases_filepath, 'w', encoding='utf-8')
    for i, key_phrase in enumerate(keyphrases):
        key_phrases_file.write(
            '{0}\t{1}\t{2}\t{3}\n'.format(i, key_phrase['span'], key_phrase['label'], key_phrase['term']))
    key_phrases_file.close()


def main(argv):
    extraction_mode = ''
    try:
        opts, args = getopt.getopt(argv, 'hsl')
    except getopt.GetoptError:
        print('run_tbxtools.py -s <tbxtools statistical mode> -l <tbxtools linguistic mode>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('run_tbxtools.py -s <tbxtools statistical mode> -l <tbxtools linguistic mode>')
            sys.exit()
        elif opt == '-s':
            extraction_mode = 'statistical'
        elif opt == '-l':
            extraction_mode = 'linguistic'

    corpus_filepath = 'corpus/input_corpus.txt'
    results_dir = 'results/tbxtools/' + extraction_mode + '/'
    input_filename = 'input_tbxtools.txt'
    output_filename = 'candidates.txt'
    brat_filepath = 'results/tbxtools/brat.txt'
    output_a_filename = 'output_a_tbxtools.txt'
    output_b_filename = 'output_b_tbxtools.txt'  # required for evaluation
    if not os.path.exists(results_dir):
        os.makedirs(results_dir)
    copyfile(corpus_filepath, results_dir + input_filename)
    process_input(corpus_filepath, results_dir + output_filename, extraction_mode)
    key_phrases = format_output(results_dir + output_filename, results_dir + input_filename, brat_filepath)
    print_output(key_phrases, results_dir + output_a_filename)
    open(results_dir + output_b_filename, 'w+', encoding='utf-8').close()


if __name__ == '__main__':
    main(sys.argv[1:])
