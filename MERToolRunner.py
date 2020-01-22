import shutil
from abc import ABC, abstractmethod
from pathlib import Path

from lib.Med_Tagger import Med_Tagger


class MERToolRunner(ABC):

    def __init__(self, config):
        self.corpus_filepath = Path(config['corpus_filepath'])
        self.input_filepath = Path(config['results_dir'] + config['input_filename'])
        self.output_a_filepath = Path(config['results_dir'] + config['output_a_filename'])
        self.output_b_filepath = Path(config['results_dir'] + config['output_b_filename'])
        self.key_phrases = []

    def process_input(self):
        '''Extracts information from input'''
        if not self.input_filepath.parent.exists():
            self.input_filepath.parent.mkdir(parents=True)
        shutil.copyfile(self.corpus_filepath, self.input_filepath)

    @abstractmethod
    def format_output(self):
        '''Formats the original output to eHealth-KD subtask A output'''
        pass

    def print_output(self):
        '''Writes the formatted output to a file'''
        output_a_file = self.output_a_filepath.open('w', encoding='utf-8')
        self.output_b_filepath.open('w', encoding='utf-8')
        for i, key_phrase in enumerate(self.key_phrases):
            output_a_file.write(
                '{0}\t{1}\t{2}\t{3}\n'.format(i, key_phrase['span'], key_phrase['label'], key_phrase['term']))

    def get_brat(self):
        '''Returns BRAT tags from brat text file'''
        brat_filepath = Path('results/brat.txt')
        if not brat_filepath.exists():
            self.__convert_input_to_brat(brat_filepath)
        brat_file = brat_filepath.open(encoding='utf-8')
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

    def __convert_input_to_brat(self, brat_filepath):
        '''Formats input to BRAT'''
        tag = Med_Tagger()  # Starts a docker image in background
        input_file = self.input_filepath.open(encoding='utf-8')
        input_text = input_file.read()
        input_parsed = tag.parse(input_text)
        tag.write_brat(input_text, input_parsed, brat_filepath)
        del (tag)  # To kill the docker image
