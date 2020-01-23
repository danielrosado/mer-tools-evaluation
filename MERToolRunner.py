import shutil
from abc import ABC, abstractmethod
from pathlib import Path


class MERToolRunner(ABC):

    def __init__(self, config):
        self._corpus_filepath = Path(config['corpus_filepath'])
        self._input_filepath = Path(config['results_dir'] + config['input_filename'])
        self._output_a_filepath = Path(config['results_dir'] + config['output_a_filename'])
        self._output_b_filepath = Path(config['results_dir'] + config['output_b_filename'])
        self._key_phrases = []

    def prepare_input(self):
        '''Formats the corpus input to the proper tool's input'''
        if not self._input_filepath.parent.exists():
            self._input_filepath.parent.mkdir(parents=True)
        shutil.copyfile(self._corpus_filepath, self._input_filepath)

    def process_input(self):
        '''Extracts information from input'''
        pass

    @abstractmethod
    def format_output(self):
        '''Formats the original output to eHealth-KD subtask A output'''
        pass

    def print_output(self):
        '''Writes the formatted output to a file'''
        output_a_file = self._output_a_filepath.open('w', encoding='utf-8')
        self._output_b_filepath.open('w', encoding='utf-8') # required for evaluation
        for i, key_phrase in enumerate(self._key_phrases):
            output_a_file.write(
                '{0}\t{1}\t{2}\t{3}\n'.format(i, key_phrase['span'], key_phrase['label'], key_phrase['term']))
