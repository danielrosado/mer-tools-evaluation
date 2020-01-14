from quickumls import QuickUMLS
from shutil import copyfile
import os
import time


# HELPER FUNCTIONS


def umls_to_keyphrase(concept):
    '''Converts an UMLS concept to a eHealth-KD concept'''
    keyphrase = {
        'label': 'Concept',
        'term': concept['ngram']
    }
    multiword_term = concept['ngram'].split()
    if not multiword_term:
        keyphrase['span'] = '{0} {1}'.format(concept['start'], concept['end'])
    else:
        span = []
        for token in multiword_term:
            if not span:
                span.append((concept['start'], concept['start'] + len(token)))
            else:
                span.append((span[-1][1] + 1, span[-1][1] + 1 + len(token)))
        span = map(lambda i: '{0} {1}'.format(i[0], i[1]), span)
        keyphrase['span'] = ';'.join(span)
    return keyphrase


# MAIN FUNCTIONS


def process_input(input_filepath):
    '''Extracts information from input'''
    matcher = QuickUMLS('/home/daniel/QuickUMLS')
    input_file = open(input_filepath, encoding='utf8')
    text = input_file.read()
    print('--- Processing input ---')
    start_time = time.time()
    matches = matcher.match(text, best_match=True, ignore_syntax=False)
    end_time = time.time() - start_time
    print('--- {} seconds ---'.format(end_time))
    input_file.close()
    return matches


def format_output(output):
    '''Formats the original output to eHealth-KD subtask A output'''
    output = map(lambda list: list[0], output) # only first term (preferred term)
    output = sorted(output, key=lambda t: t['start'])
    keyphrases = list(map(umls_to_keyphrase, output))
    return keyphrases


def print_output(keyphrases, keyphrases_filepath):
    '''Writes the formatted output to a file'''
    key_phrases_file = open(keyphrases_filepath, 'w', encoding='utf-8')
    for i, key_phrase in enumerate(keyphrases):
        key_phrases_file.write(
            '{0}\t{1}\t{2}\t{3}\n'.format(i, key_phrase['span'], key_phrase['label'], key_phrase['term']))
    key_phrases_file.close()


if __name__ == '__main__':
    corpus_filepath = 'corpus/input_corpus.txt'
    results_dir = 'results/quickumls/'
    input_filename = 'input_quickumls.txt'
    output_a_filename = 'output_a_quickumls.txt'
    output_b_filename = 'output_b_quickumls.txt'  # required for evaluation
    if not os.path.exists(results_dir):
        os.makedirs(results_dir)
    copyfile(corpus_filepath, results_dir + input_filename)
    output = process_input(results_dir + input_filename)
    keyphrases = format_output(output)
    print_output(keyphrases, results_dir + output_a_filename)
    open(results_dir + output_b_filename, 'w+', encoding='utf-8').close()
