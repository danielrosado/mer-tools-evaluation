import os
from MERToolProcessorFactory import MERToolProcessorFactory
from MERToolProcessor import MERToolProcessor

if __name__ == '__main__':
    processor_factory = MERToolProcessorFactory('corpus/input_corpus.txt')
    for subclass in MERToolProcessor.__subclasses__():
        processor = processor_factory.create_processor(subclass)
        processor.prepare_input()
        processor.process_input()
        processor.format_output()
        processor.print_output()
    os.system('./evaluation/run_evaluation.sh')
