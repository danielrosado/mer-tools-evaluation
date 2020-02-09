from IxaMedTaggerProcessor import IxaMedTaggerProcessor
from TBXToolsProcessor import TBXToolsProcessor
from TBXToolsMode import TBXToolsMode
from QuickUMLSProcessor import QuickUMLSProcessor
from ADR2OpenBratProcessor import ADR2OpenBratProcessor


class MERToolProcessorFactory:
    
    def __init__(self, corpus_filepath):
        self.corpus_filepath = corpus_filepath

    def create_processor(self, processor_class):
        if processor_class == IxaMedTaggerProcessor:
            config = {
                'corpus_filepath': self.corpus_filepath,
                'results_dir': 'results/ixamedtagger/',
                'input_filename': 'input_ixamedtagger.txt',
                'input_formatted_filename': 'input_formatted.txt',
                'output_filename': 'input_formatted.txt-tagged',
                'output_a_filename': 'output_a_ixamedtagger.txt',
                'output_b_filename': 'output_b_ixamedtagger.txt',
            }
            return IxaMedTaggerProcessor(config)

        if processor_class == TBXToolsProcessor:
            mode = TBXToolsMode.STATISTICAL
            # mode = TBXToolsMode.LINGUISTIC
            config = {
                'corpus_filepath': self.corpus_filepath,
                'results_dir': 'results/tbxtools/' + str(mode.value) + '/',
                'input_filename': 'input_tbxtools.txt',
                'output_filename': 'candidates.txt',
                'output_a_filename': 'output_a_tbxtools.txt',
                'output_b_filename': 'output_b_tbxtools.txt',
                'mode': mode
            }
            return TBXToolsProcessor(config)

        if processor_class == QuickUMLSProcessor:
            config = {
                'corpus_filepath': self.corpus_filepath,
                'results_dir': 'results/quickumls/',
                'input_filename': 'input_quickumls.txt',
                'output_a_filename': 'output_a_quickumls.txt',
                'output_b_filename': 'output_b_quickumls.txt',
            }
            return QuickUMLSProcessor(config)

        if processor_class == ADR2OpenBratProcessor:
            config = {
                'corpus_filepath': self.corpus_filepath,
                'results_dir': 'results/adr2openbrat/',
                'input_filename': 'input_adr2openbrat.txt',
                'output_filename': 'data/output.ann',
                'output_a_filename': 'output_a_adr2openbrat.txt',
                'output_b_filename': 'output_b_adr2openbrat.txt'
            }
            return ADR2OpenBratProcessor(config)

        raise Exception('The given class is not valid')