from shutil import copyfile
import os


# HELPER FUNCTIONS


def search_line(input_file_content, prev_line, concept):
    '''Finds the line of the concept in the input file content'''
    for i, ln in enumerate(input_file_content):
        if i < prev_line:
            continue
        ln = ln.replace('.', '').replace(',', '')
        if concept.split():  # multiword concepts
            concept = concept.split()[0]
        if concept in ln.split():
            return i
    return -1


# MAIN FUNCTIONS


def format_output(output_filepath, input_filepath):
    '''Formats the original output to eHealth-KD subtask A output'''
    input_file = open(input_filepath, encoding='utf-8')
    input_file_content = input_file.readlines()
    input_file.close()
    output_file = open(output_filepath, encoding='utf-8')
    keyphrases = []
    newline_diff = 0
    for ln in output_file.readlines():
        concept = ln.split('\t')
        if not concept or concept[0].startswith('E'):  # It is not a concept
            break
        concept = [concept[0], concept[1].split(' ', 1)[1], concept[2].strip('\n')]
        keyphrase = {
            'label': 'Concept',
            'term': concept[2]
        }
        # ADR2OpenBrat counts each new line in BRAT span, so it must be subtracted
        newline_diff = search_line(input_file_content, newline_diff, concept[2])
        multiword_term = keyphrase['term'].split()
        if not multiword_term:
            span = concept[1].split()
            keyphrase['span'] = '{0} {1}'.format(int(span[0]) - newline_diff, int(span[1]) - newline_diff)
        else:
            span = []
            for token in multiword_term:
                if not span:
                    start = concept[1].split()[0]
                    span.append((int(start) - newline_diff, int(start) + len(token) - newline_diff))
                else:
                    span.append((span[-1][1] + 1, span[-1][1] + 1 + len(token)))
            span = map(lambda i: '{0} {1}'.format(i[0], i[1]), span)
            keyphrase['span'] = ';'.join(span)
        keyphrases.append(keyphrase)
    output_file.close()
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
    results_dir = 'results/adr2openbrat/'
    input_filename = 'input_adr2openbrat.txt'
    output_filename = 'data/output.ann'
    output_a_filename = 'output_a_adr2openbrat.txt'
    output_b_filename = 'output_b_adr2openbrat.txt'
    if not os.path.exists(results_dir):
        os.makedirs(results_dir)
    copyfile(corpus_filepath, results_dir + input_filename)
    keyphrases = format_output(output_filename, results_dir + input_filename)
    print_output(keyphrases, results_dir + output_a_filename)
    open(results_dir + output_b_filename, 'w+', encoding='utf-8').close()
