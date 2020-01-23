import time
from quickumls import QuickUMLS
from MERToolRunner import MERToolRunner


class QuickUMLSRunner(MERToolRunner):

    def __init__(self, config):
        self.quickumls = QuickUMLS('/home/daniel/QuickUMLS')
        self.matches = None
        super().__init__(config)

    def process_input(self):
        '''Extracts information from input'''
        input_file = self.input_filepath.open(encoding='utf8')
        text = input_file.read()
        print('--- QuickUMLS: Processing input ---')
        start_time = time.time()
        self.matches = self.quickumls.match(text, best_match=True, ignore_syntax=False)
        end_time = time.time() - start_time
        print('--- {} seconds ---'.format(end_time))

    def format_output(self):
        '''Formats the original output to eHealth-KD subtask A output'''
        terms = map(lambda list: list[0], self.matches)  # only first term (preferred term)
        ordered_terms = sorted(terms, key=lambda t: t['start'])
        self.key_phrases = list(map(__class__.__umls_to_keyphrase, ordered_terms))

    @staticmethod
    def __umls_to_keyphrase(concept):
        '''Converts an UMLS concept to a eHealth-KD keyphrase'''
        keyphrase = {
            'label': 'Concept',
            'term': concept['ngram']
        }
        multiword_term = concept['ngram'].split()
        if not multiword_term:
            keyphrase['span'] = '{0} {1}'.format(concept['start'], concept['end'])
        else:
            span = []
            for token in multiword_term:
                if not span:
                    span.append((concept['start'], concept['start'] + len(token)))
                else:
                    span.append((span[-1][1] + 1, span[-1][1] + 1 + len(token)))
            span = map(lambda interval: '{0} {1}'.format(interval[0], interval[1]), span)
            keyphrase['span'] = ';'.join(span)
        return keyphrase
