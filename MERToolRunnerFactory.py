from IxaMedTaggerRunner import IXAMedTaggerRunner
from TBXToolsRunner import TBXToolsRunner
from TBXToolsMode import TBXToolsMode
from QuickUMLSRunner import QuickUMLSRunner
from ADR2OpenBratRunner import ADR2OpenBratRunner


class MERToolRunnerFactory:

    @staticmethod
    def create_runner(runner_class):
        if runner_class == IXAMedTaggerRunner:
            ixamedtagger_runner_config = {
                'corpus_filepath': 'corpus/input_corpus.txt',
                'results_dir': 'results/ixamedtagger/',
                'input_filename': 'input_ixamedtagger.txt',
                'input_formatted_filename': 'input_formatted.txt',
                'output_filename': 'input_formatted.txt-tagged',
                'output_a_filename': 'output_a_ixamedtagger.txt',
                'output_b_filename': 'output_b_ixamedtagger.txt',
            }
            return IXAMedTaggerRunner(ixamedtagger_runner_config)

        if runner_class == TBXToolsRunner:
            mode = TBXToolsMode.LINGUISTIC.value
            tbxtools_runner_config = {
                'corpus_filepath': 'corpus/input_corpus.txt',
                'results_dir': 'results/tbxtools/' + mode + '/',
                'input_filename': 'input_tbxtools.txt',
                'output_filename': 'candidates.txt',
                'output_a_filename': 'output_a_tbxtools.txt',
                'output_b_filename': 'output_b_tbxtools.txt',
                'mode': mode
            }
            return TBXToolsRunner(tbxtools_runner_config)

        if runner_class == QuickUMLSRunner:
            quickumls_runner_config = {
                'corpus_filepath': 'corpus/input_corpus.txt',
                'results_dir': 'results/quickumls/',
                'input_filename': 'input_quickumls.txt',
                'output_a_filename': 'output_a_quickumls.txt',
                'output_b_filename': 'output_b_quickumls.txt',
            }
            return QuickUMLSRunner(quickumls_runner_config)

        if runner_class == ADR2OpenBratRunner:
            adr2openbrat_runner_config = {
                'corpus_filepath': 'corpus/input_corpus.txt',
                'results_dir': 'results/adr2openbrat/',
                'input_filename': 'input_adr2openbrat.txt',
                'output_filename': 'data/output.ann',
                'output_a_filename': 'output_a_adr2openbrat.txt',
                'output_b_filename': 'output_b_adr2openbrat.txt'
            }
            return ADR2OpenBratRunner(adr2openbrat_runner_config)
