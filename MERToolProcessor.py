import shutil
from abc import ABC, abstractmethod
from pathlib import Path


class MERToolProcessor(ABC):

    def __init__(self, config):
        self.__corpus_filepath = Path(config['corpus_filepath'])
        self.__input_filepath = Path(config['results_dir'] + config['input_filename'])
        self.__key_phrases = []
        self.__output_a_filepath = Path(config['results_dir'] + config['output_a_filename'])
        self.__output_b_filepath = Path(config['results_dir'] + config['output_b_filename'])

    def prepare_input(self):
        """Formats the corpus input to the proper tool's input"""
        if not self.__input_filepath.parent.exists():
            self.__input_filepath.parent.mkdir(parents=True)
        shutil.copyfile(self.__corpus_filepath, self.__input_filepath)

    def process_input(self):
        """Extracts information from input"""
        pass

    @abstractmethod
    def format_output(self):
        """Formats the original output to eHealth-KD subtask A output"""
        pass

    def print_output(self):
        """Writes the formatted output to a file"""
        output_a_file = self.__output_a_filepath.open('w', encoding='utf-8')
        self.__output_b_filepath.open('w', encoding='utf-8')  # required for evaluation
        for i, key_phrase in enumerate(self.__key_phrases):
            output_a_file.write(
                '{0}\t{1}\t{2}\t{3}\n'.format(i, key_phrase['span'], key_phrase['label'], key_phrase['term']))

    @property
    def _input_filepath(self):
        return self.__input_filepath

    @property
    def _key_phrases(self):
        return self.__key_phrases
