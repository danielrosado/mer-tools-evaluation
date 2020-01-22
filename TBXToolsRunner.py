import time
from pathlib import Path
from lib.TBXTools import TBXTools
from MERToolRunner import MERToolRunner
from TBXToolsMode import TBXToolsMode


class TBXToolsRunner(MERToolRunner):

    def __init__(self, config):
        self.tool = TBXTools()
        self.mode = config['mode']
        self.results_dir = config['results_dir']
        self.output_filepath = Path(config['results_dir'] + config['output_filename'])
        super().__init__(config)

    def process_input(self):
        '''Extracts information from input'''
        super().process_input()
        print('--- Processing input ---')
        start_time = time.time()
        self.tool.create_project(self.results_dir + '/corpus.sqlite', 'spa', overwrite=True)
        self.tool.load_sl_corpus(self.input_filepath)
        if (self.mode == TBXToolsMode.LINGUISTIC):
            self.tool.start_freeling_api('es')
            self.tool.tag_freeling_api()
            self.tool.save_sl_tagged_corpus(self.results_dir + '/corpus-tagged-spa.txt')
            self.tool.load_linguistic_patterns('data/patterns-forms-spa.txt')
            self.tool.tagged_ngram_calculation(nmin=2, nmax=3, minfreq=1)
            self.tool.linguistic_term_extraction(minfreq=1)
        elif (self.mode == TBXToolsMode.STATISTICAL):
            self.tool.ngram_calculation(nmin=2, nmax=3, minfreq=1)
            self.tool.load_sl_stopwords('data/stop-spa.txt')
            self.tool.statistical_term_extraction(minfreq=1)
            self.tool.case_normalization(verbose=False)
            self.tool.nest_normalization(verbose=False)
        self.tool.save_term_candidates(self.output_filepath)
        end_time = time.time() - start_time
        print('--- {} seconds ---'.format(end_time))

    def format_output(self):
        '''Formats the original output to eHealth-KD subtask A output'''
        brat = self.get_brat()
        output_file = self.output_filepath.open(encoding='utf-8')
        lines = output_file.readlines()
        for ln in lines:
            # search the extracted concepts in BRAT text in order to get the span intervals
            ln = ln.split('\t')
            freq = int(ln[0])
            candidate_tokens = ln[1].split()
            i = 0
            j = 0
            k = 0
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
        self.key_phrases.sort(key=lambda k: int(k['span'][0][0]))
        self.key_phrases = map(__class__.__format_key_phrase, self.key_phrases)

    @staticmethod
    def __format_key_phrase(key_phrase):
        span = map(lambda t: '{0} {1}'.format(t[0], t[1]), key_phrase['span'])
        key_phrase['span'] = ';'.join(span)
        key_phrase['term'] = ' '.join(key_phrase['term'])
        return key_phrase
