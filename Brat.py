from pathlib import Path
from lib.Med_Tagger import Med_Tagger


class Brat:

    @staticmethod
    def convert_to_brat(input_filename, brat_filename):
        """Converts input to BRAT and returns the BRAT tags"""
        input_filepath = Path(input_filename)
        brat_filepath = Path(brat_filename)
        if not brat_filepath.exists():
            tagger = Med_Tagger()  # Starts a docker image in background
            input_file = input_filepath.open(encoding='utf-8')
            input_text = input_file.read()
            input_parsed = tagger.parse(input_text)
            tagger.write_brat(input_text, input_parsed, brat_filepath)
            del tagger  # To kill the docker image
        brat_file = brat_filepath.open(encoding='utf-8')
        brat = []
        for line in brat_file.readlines():
            if line.startswith('#'):
                continue
            elements = line.split('\t')
            type_span = elements[1].split()
            brat_line = {
                'start': type_span[1],
                'end': type_span[2],
                'token': elements[2].split('\n')[0]
            }
            brat.append(brat_line)
        return brat
