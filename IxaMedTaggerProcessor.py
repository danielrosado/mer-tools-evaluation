import os
import time
from pathlib import Path
from MERToolProcessor import MERToolProcessor
from Brat import Brat


class IxaMedTaggerProcessor(MERToolProcessor):

    def __init__(self, config):
        self.__input_formatted_filepath = config['results_dir'] + config['input_formatted_filename']
        self.__output_filepath = Path(config['results_dir'] + config['output_filename'])
        self.__ixamedtagger = 'lib/perceptron.jar'
        super().__init__(config)

    def prepare_input(self):
        """Formats the corpus input to the proper tool's input"""
        super().prepare_input()
        input_file = self.input_filepath.open(encoding='utf-8')
        input_formatted_file = Path(self.__input_formatted_filepath).open('w', encoding='utf8')
        for line in input_file.readlines():
            for token in line.split():
                if token.endswith('.') or token.endswith(','):
                    input_formatted_file.write('{0}\n{1}\n'.format(token[:-1], token[-1]))
                else:
                    input_formatted_file.write('{}\n'.format(token))

    def process_input(self):
        """Extracts information from input"""
        print('--- IxaMedTagger: processing input ---')
        start_time = time.time()
        os.system('java -jar {0} {1}'.format(self.__ixamedtagger, self.__input_formatted_filepath))
        end_time = time.time() - start_time
        print('--- {} seconds ---'.format(end_time))

    def format_output(self):
        """Formats the original output to eHealth-KD subtask A output"""
        brat = Brat.convert_to_brat(self.input_filepath, 'results/brat.txt')
        output_file = self.__output_filepath.open(encoding='utf-8')
        # Assign BRAT span to each token from output
        terms = []
        i = 0
        multiword = False
        for token_tagged in output_file.readlines():
            token_tagged = token_tagged.split()
            if not token_tagged:
                break
            token = token_tagged[0]
            tag = token_tagged[1]
            term = {
                'token': token,
                'tag': tag
            }
            if token == brat[i]['token']:
                term['start'] = brat[i]['start']
                term['end'] = brat[i]['end']
                terms.append(term)
                i += 1
            elif ' ' in brat[i]['token'] and token in brat[i]['token']:
                multiword = True
                term['start'] = str(int(brat[i]['start']) + brat[i]['token'].index(token))
                term['end'] = str(int(term['start']) + len(token))
                terms.append(term)
            elif any([char in token for char in ['(', ')', ':', '/']]):
                multiword = True
                term['start'] = brat[i]['start']
                while brat[i]['token'] in token:
                    i += 1
                term['end'] = brat[i]['end'],
                terms.append(term)
            elif multiword:
                i += 1
                if token != brat[i]['token']:
                    raise Exception('Tokens does not match: {0} {1}'.format(token, brat[i]['token']))
                term['start'] = brat[i]['start']
                term['end'] = brat[i]['end']
                terms.append(term)
                multiword = False
                i += 1
            else:
                raise Exception('Tokens does not match: {0} {1}'.format(token, brat[i]['token']))
        # Generate key phrases from previous terms
        multiword_tags = [
            'I-Grp_Enfermedad',
            'B-Estructura_Corporal',
            'I-Estructura_Corporal',
            'B-Calificador',
            'I-Calificador'
        ]
        for term in terms:
            if term['tag'] == 'O':
                continue
            if self.key_phrases != [] and int(self.key_phrases[-1]['span'][-1][1]) == (int(term['start']) - 1) \
                    and term['tag'] in multiword_tags:
                self.key_phrases[-1]['span'].append((term['start'], term['end']))
                self.key_phrases[-1]['term'] += ' ' + term['token']
            else:
                key_phrase = {
                    'span': [(term['start'], term['end'])],
                    'label': 'Concept',
                    'term': term['token'],
                }
                self.key_phrases.append(key_phrase)
        # Format span
        for key_phrase in self.key_phrases:
            span = map(lambda interval: '{0} {1}'.format(interval[0], interval[1]), key_phrase['span'])
            key_phrase['span'] = ';'.join(span)
