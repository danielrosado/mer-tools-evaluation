import time
from quickumls import QuickUMLS
from MERToolProcessor import MERToolProcessor


class QuickUMLSProcessor(MERToolProcessor):

    def __init__(self, config):
        self.__quickumls = QuickUMLS('/home/daniel/QuickUMLS')
        self.__matches = None
        super().__init__(config)

    def process_input(self):
        """Extracts information from input"""
        input_file = self.input_filepath.open(encoding='utf8')
        text = input_file.read()
        print('--- QuickUMLS: Processing input ---')
        start_time = time.time()
        self.__matches = self.__quickumls.match(text, best_match=True, ignore_syntax=False)
        end_time = time.time() - start_time
        print('--- {} seconds ---'.format(end_time))

    def format_output(self):
        """Formats the original output to eHealth-KD subtask A output"""
        umls_concepts = map(lambda match_list: match_list[0], self.__matches)  # Only first term (preferred term)
        ordered_concepts = sorted(umls_concepts, key=lambda umls_concept: umls_concept['start'])  # Order by start
        # Converts an UMLS concept to a eHealth-KD keyphrase
        for concept in ordered_concepts:
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
                span = map(lambda tup: '{0} {1}'.format(tup[0], tup[1]), span)
                keyphrase['span'] = ';'.join(span)
            self.key_phrases.append(keyphrase)
