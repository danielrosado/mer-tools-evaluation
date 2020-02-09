from pathlib import Path
from MERToolProcessor import MERToolProcessor


class ADR2OpenBratProcessor(MERToolProcessor):

    def __init__(self, config):
        self.__output_filepath = Path(config['output_filename'])
        super().__init__(config)

    def format_output(self):
        """Formats the original output to eHealth-KD subtask A output"""
        input_file = self._input_filepath.open(encoding='utf-8')
        output_file = self.__output_filepath.open(encoding='utf-8')
        input_file_content = input_file.readlines()
        newline_diff = 0
        for ln in output_file.readlines():
            concept = ln.split('\t')
            if not concept or concept[0].startswith('E'):  # It is not a concept
                break
            concept = [concept[0], concept[1].split(' ', 1)[1], concept[2].strip('\n')]
            key_phrase = {
                'label': 'Concept',
                'term': concept[2]
            }
            # ADR2OpenBrat counts each new line in BRAT span, so it must be subtracted
            newline_diff = self.__search_line(input_file_content, newline_diff, concept[2])
            multiword_term = key_phrase['term'].split()
            if not multiword_term:
                span = concept[1].split()
                key_phrase['span'] = '{0} {1}'.format(int(span[0]) - newline_diff, int(span[1]) - newline_diff)
            else:
                span = []
                for token in multiword_term:
                    if not span:
                        start = concept[1].split()[0]
                        span.append((int(start) - newline_diff, int(start) + len(token) - newline_diff))
                    else:
                        span.append((span[-1][1] + 1, span[-1][1] + 1 + len(token)))
                span = map(lambda interval: '{0} {1}'.format(interval[0], interval[1]), span)
                key_phrase['span'] = ';'.join(span)
            self._key_phrases.append(key_phrase)

    @staticmethod
    def __search_line(input_file_content, prev_line, concept):
        """Finds the line of the concept in the input file content"""
        for i, line in enumerate(input_file_content):
            if i < prev_line:
                continue
            line = line.replace('.', '').replace(',', '')
            if concept.split():  # multiword concepts
                concept = concept.split()[0]
            if concept in line.split():
                return i
        return -1
