import time
from pathlib import Path
from lib.TBXTools import TBXTools
from MERToolProcessor import MERToolProcessor
from TBXToolsMode import TBXToolsMode
from Brat import Brat


class TBXToolsProcessor(MERToolProcessor):

    def __init__(self, config):
        self.__tbxtools = TBXTools()
        self.__mode = config['mode']
        self.__results_dir = config['results_dir']
        self.__output_filepath = Path(config['results_dir'] + config['output_filename'])
        super().__init__(config)

    def process_input(self):
        """Extracts information from input"""
        print('--- TBXTools - {}: Processing input ---'.format(self.__mode.value))
        start_time = time.time()
        self.__tbxtools.create_project(self.__results_dir + 'corpus.sqlite', 'spa', overwrite=True)
        self.__tbxtools.load_sl_corpus(self.input_filepath)
        if self.__mode == TBXToolsMode.LINGUISTIC:
            self.__tbxtools.start_freeling_api('es')
            self.__tbxtools.tag_freeling_api()
            self.__tbxtools.save_sl_tagged_corpus(self.__results_dir + 'corpus-tagged-spa.txt')
            self.__tbxtools.load_linguistic_patterns('data/patterns-forms-spa.txt')
            self.__tbxtools.tagged_ngram_calculation(nmin=2, nmax=3, minfreq=1)
            self.__tbxtools.linguistic_term_extraction(minfreq=1)
        elif self.__mode == TBXToolsMode.STATISTICAL:
            self.__tbxtools.ngram_calculation(nmin=2, nmax=3, minfreq=1)
            self.__tbxtools.load_sl_stopwords('data/stop-spa.txt')
            self.__tbxtools.statistical_term_extraction(minfreq=1)
            self.__tbxtools.case_normalization(verbose=False)
            self.__tbxtools.nest_normalization(verbose=False)
        self.__tbxtools.save_term_candidates(self.__output_filepath)
        end_time = time.time() - start_time
        print('--- {} seconds ---'.format(end_time))

    def format_output(self):
        """Formats the original output to eHealth-KD subtask A output"""
        # Search the extracted concepts in BRAT text in order to get the span
        brat = Brat.convert_to_brat(self.input_filepath, 'results/brat.txt')
        output_file = self.__output_filepath.open(encoding='utf-8')
        for ln in output_file.readlines():
            ln = ln.split('\t')
            freq = int(ln[0])
            candidate_tokens = ln[1].split()
            i = 0  # brat index
            j = 0  # frequency index
            k = 0  # candidate tokens index
            key_phrase = {'span': [], 'term': []}
            while i < len(brat) and j < freq:
                if k == len(candidate_tokens):  # multiword term found
                    key_phrase['label'] = 'Concept'
                    self.key_phrases.append(key_phrase)
                    key_phrase = {'span': [], 'term': []}
                    j += 1
                    k = 0
                else:
                    if candidate_tokens[k] == brat[i]['token']:
                        key_phrase['span'].append((brat[i]['start'], brat[i]['end']))
                        key_phrase['term'].append(brat[i]['token'])
                        k += 1
                    else:
                        if k > 0:
                            key_phrase = {'span': [], 'term': []}
                            k = 0
                i += 1
        self.key_phrases.sort(key=lambda kp: int(kp['span'][0][0]))  # Order by start
        # Format span and term
        for key_phrase in self.key_phrases:
            span = map(lambda interval: '{0} {1}'.format(interval[0], interval[1]), key_phrase['span'])
            key_phrase['span'] = ';'.join(span)
            key_phrase['term'] = ' '.join(key_phrase['term'])
