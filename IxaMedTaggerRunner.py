import os
import time
from pathlib import Path
from MERToolRunner import MERToolRunner


class IXAMedTaggerRunner(MERToolRunner):

    def __init__(self, config):
        self.input_formatted_filepath = config['results_dir'] + config['input_formatted_filename']
        self.output_filepath = Path(config['results_dir'] + config['output_filename'])
        self.tool = 'lib/perceptron.jar'
        super().__init__(config)

    def process_input(self):
        '''Extracts information from input'''
        super().process_input()
        self.__format_input()
        print('--- Processing input ---')
        start_time = time.time()
        os.system('java -jar {0} {1}'.format(self.tool, self.input_formatted_filepath))
        end_time = time.time() - start_time
        print('--- {} seconds ---'.format(end_time))

    def format_output(self):
        '''Formats the original output to eHealth-KD subtask A output'''
        file_index = 0
        file_line = 1
        output_file = self.output_filepath.open(encoding='utf-8')
        for i, token_tagged in enumerate(output_file.readlines()):
            token_tagged = token_tagged.split()
            if not token_tagged:
                break
            token = token_tagged[0]
            tag = token_tagged[1]
            if tag != 'O':  # Recognized concept
                multiword_tags = [
                    'I-Grp_Enfermedad',
                    'B-Estructura_Corporal',
                    'I-Estructura_Corporal',
                    'B-Calificador',
                    'I-Calificador'
                ]
                if self.key_phrases != [] and self.key_phrases[-1]['n'] == (i - 1) and tag in multiword_tags:
                    self.key_phrases[-1]['n'] = i
                    self.key_phrases[-1]['span'].append((file_index, file_index + len(token)))
                    self.key_phrases[-1]['term'] += ' ' + token
                else:
                    key_phrase = {
                        'n': i,
                        'span': [(file_index, file_index + len(token))],
                        'label': 'Concept',
                        'term': token,
                        'tag': tag
                    }
                    self.key_phrases.append(key_phrase)
            if token == '.':
                file_line += 1
            file_index += self.__increment_file_index(file_line, token)
        for key_phrase in self.key_phrases:
            span = list(map(lambda i: '{0} {1}'.format(i[0], i[1]), key_phrase['span']))
            key_phrase['span'] = ';'.join(span)

    def __format_input(self):
        '''Formats the corpus input to IxaMedTagger input'''
        input_file = self.input_filepath.open(encoding='utf-8')
        input_formatted_file = Path(self.input_formatted_filepath).open('w', encoding='utf8')
        for line in input_file.readlines():
            for token in line.split():
                if token.endswith('.') or token.endswith(','):
                    input_formatted_file.write('{0}\n{1}\n'.format(token[:-1], token[-1]))
                else:
                    input_formatted_file.write('{}\n'.format(token))

    def __increment_file_index(self, line, token):
        '''Increments the index of the input file'''
        if token == '.' or token == ',':
            return 1
        inc = len(token) + 1
        # duplicated spaces on:
        if (line == 18 and token == 'está') or (line == 23 and token == 'llama') or (
                line == 23 and token == 'coronarias') or (line == 40 and token == 'prevenir'):
            inc += 1
        return inc
