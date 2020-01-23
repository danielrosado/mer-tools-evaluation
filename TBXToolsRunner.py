import time
from pathlib import Path
from lib.TBXTools import TBXTools
from MERToolRunner import MERToolRunner
from TBXToolsMode import TBXToolsMode
from Brat import Brat


class TBXToolsRunner(MERToolRunner):

    def __init__(self, config):
        self.tbxtools = TBXTools()
        self.mode = config['mode']
        self.results_dir = config['results_dir']
        self.output_filepath = Path(config['results_dir'] + config['output_filename'])
        self.brat = Brat()
        super().__init__(config)

    def process_input(self):
        '''Extracts information from input'''
        print('--- TBXTools - {}: Processing input ---'.format(self.mode.value))
        start_time = time.time()
        self.tbxtools.create_project(self.results_dir + 'corpus.sqlite', 'spa', overwrite=True)
        self.tbxtools.load_sl_corpus(self.input_filepath)
        if (self.mode == TBXToolsMode.LINGUISTIC):
            self.tbxtools.start_freeling_api('es')
            self.tbxtools.tag_freeling_api()
            self.tbxtools.save_sl_tagged_corpus(self.results_dir + 'corpus-tagged-spa.txt')
            self.tbxtools.load_linguistic_patterns('data/patterns-forms-spa.txt')
            self.tbxtools.tagged_ngram_calculation(nmin=2, nmax=3, minfreq=1)
            self.tbxtools.linguistic_term_extraction(minfreq=1)
        elif (self.mode == TBXToolsMode.STATISTICAL):
            self.tbxtools.ngram_calculation(nmin=2, nmax=3, minfreq=1)
            self.tbxtools.load_sl_stopwords('data/stop-spa.txt')
            self.tbxtools.statistical_term_extraction(minfreq=1)
            self.tbxtools.case_normalization(verbose=False)
            self.tbxtools.nest_normalization(verbose=False)
        self.tbxtools.save_term_candidates(self.output_filepath)
        end_time = time.time() - start_time
        print('--- {} seconds ---'.format(end_time))

    def format_output(self):
        '''Formats the original output to eHealth-KD subtask A output'''
        # Search the extracted concepts in BRAT text in order to get the span
        brat = self.brat.convert_to_brat(self.input_filepath, 'results/brat.txt')
        output_file = self.output_filepath.open(encoding='utf-8')
        for ln in output_file.readlines():
            ln = ln.split('\t')
            freq = int(ln[0])
            candidate_tokens = ln[1].split()
            i = 0 # brat index
            j = 0 # frequency index
            k = 0 # candidate tokens index
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
                        if (k > 0):
                            key_phrase = {'span': [], 'term': []}
                            k = 0
                i += 1
        self.key_phrases.sort(key=lambda key_phrase: int(key_phrase['span'][0][0])) # Order by start
        # Format span and term
        for key_phrase in self.key_phrases:
            span = map(lambda interval: '{0} {1}'.format(interval[0], interval[1]), key_phrase['span'])
            key_phrase['span'] = ';'.join(span)
            key_phrase['term'] = ' '.join(key_phrase['term'])
