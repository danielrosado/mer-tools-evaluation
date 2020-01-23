import shutil
from abc import ABC, abstractmethod
from pathlib import Path


class MERToolRunner(ABC):

    def __init__(self, config):
        self.corpus_filepath = Path(config['corpus_filepath'])
        self.input_filepath = Path(config['results_dir'] + config['input_filename'])
        self.output_a_filepath = Path(config['results_dir'] + config['output_a_filename'])
        self.output_b_filepath = Path(config['results_dir'] + config['output_b_filename'])
        self.key_phrases = []

    def prepare_input(self):
        if not self.input_filepath.parent.exists():
            self.input_filepath.parent.mkdir(parents=True)
        shutil.copyfile(self.corpus_filepath, self.input_filepath)

    def process_input(self):
        '''Extracts information from input'''
        pass

    @abstractmethod
    def format_output(self):
        '''Formats the original output to eHealth-KD subtask A output'''
        pass

    def print_output(self):
        '''Writes the formatted output to a file'''
        output_a_file = self.output_a_filepath.open('w', encoding='utf-8')
        self.output_b_filepath.open('w', encoding='utf-8') # required for evaluation
        for i, key_phrase in enumerate(self.key_phrases):
            output_a_file.write(
                '{0}\t{1}\t{2}\t{3}\n'.format(i, key_phrase['span'], key_phrase['label'], key_phrase['term']))
