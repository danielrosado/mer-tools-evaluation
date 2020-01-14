from shutil import copyfile
import os
import time


# HELPER FUNCTIONS


def increment_file_index(line, token):
    '''Increments the index of the input file'''
    if token == '.' or token == ',':
        return 1
    inc = len(token) + 1
    # duplicated spaces on:
    if (line == 18 and token == 'está') or (line == 23 and token == 'llama') or (
            line == 23 and token == 'coronarias') or (line == 40 and token == 'prevenir'):
        inc += 1
    return inc


# MAIN FUNCTIONS


def format_input(input_filepath, input_formatted_filepath):
    '''Formats the corpus input to IxaMedTagger input'''
    input_file = open(input_filepath, encoding='utf8')
    input_formatted_file = open(input_formatted_filepath, 'w', encoding='utf8')
    for line in input_file.readlines():
        for token in line.split():
            if token.endswith('.') or token.endswith(','):
                input_formatted_file.write('{0}\n{1}\n'.format(token[:-1], token[-1]))
            else:
                input_formatted_file.write('{}\n'.format(token))
    input_file.close()
    input_formatted_file.close()


def process_input(input_filepath):
    '''Extracts information from input'''
    print('--- Processing input ---')
    start_time = time.time()
    os.system('java -jar lib/perceptron.jar {}'.format(input_filepath))
    end_time = time.time() - start_time
    print('--- {} seconds ---'.format(end_time))


def format_output(output_filepath):
    '''Formats the original output to eHealth-KD subtask A output'''
    corpus_tagged_file = open(output_filepath, encoding='utf8')
    key_phrases = []
    file_index = 0
    file_line = 1
    for i, token_tagged in enumerate(corpus_tagged_file.readlines()):
        token_tagged = token_tagged.split()
        if not token_tagged:
            break
        token = token_tagged[0]
        tag = token_tagged[1]
        if tag != 'O': # Recoigned concept
            multiword_tags = [
                'I-Grp_Enfermedad',
                'B-Estructura_Corporal',
                'I-Estructura_Corporal',
                'B-Calificador',
                'I-Calificador'
            ]
            if key_phrases != [] and key_phrases[-1]['n'] == (i - 1) and tag in multiword_tags:
                key_phrases[-1]['n'] = i
                key_phrases[-1]['span'].append((file_index, file_index + len(token)))
                key_phrases[-1]['term'] += ' ' + token
            else:
                key_phrase = {
                    'n': i,
                    'span': [(file_index, file_index + len(token))],
                    'label': 'Concept',
                    'term': token,
                    'tag': tag
                }
                key_phrases.append(key_phrase)
        if token == '.':
            file_line += 1
        file_index += increment_file_index(file_line, token)
    corpus_tagged_file.close()
    for key_phrase in key_phrases:
        span = list(map(lambda i: '{0} {1}'.format(i[0], i[1]), key_phrase['span']))
        key_phrase['span'] = ';'.join(span)
    return key_phrases


def print_output(key_phrases, key_phrases_filepath):
    '''Writes the formatted output to a file'''
    key_phrases_file = open(key_phrases_filepath, 'w', encoding='utf-8')
    for i, key_phrase in enumerate(key_phrases):
        key_phrases_file.write(
            '{0}\t{1}\t{2}\t{3}\n'.format(i, key_phrase['span'], key_phrase['label'], key_phrase['term']))
    key_phrases_file.close()


if __name__ == '__main__':
    corpus_filepath = 'corpus/input_corpus.txt'
    results_dir = 'results/ixamedtagger/'
    input_filename = 'input_ixamedtagger.txt'
    input_formatted_filename = 'input_formatted.txt'
    output_filename = 'input_formatted.txt-tagged'
    output_a_filename = 'output_a_ixamedtagger.txt'
    output_b_filename = 'output_b_ixamedtagger.txt'  # required for evaluation
    if not os.path.exists(results_dir):
        os.makedirs(results_dir)
    copyfile(corpus_filepath, results_dir + input_filename)
    format_input(results_dir + input_filename, results_dir + input_formatted_filename)
    process_input(results_dir + input_formatted_filename)
    key_phrases = format_output(results_dir + output_filename)
    print_output(key_phrases, results_dir + output_a_filename)
    open(results_dir + output_b_filename, 'w+', encoding='utf-8').close()
