#!/bin/sh

# Always run this directly from the project folder, **not** from inside the `evaluation` folder, like this:
# $ ./evaluation/run_evaluation.sh

echo "\nTask A - IxaMedTagger\n*******************"
python3 -m evaluation.score --skip-B corpus/input_corpus.txt results/ixamedtagger/input_ixamedtagger.txt

echo "\nTask A - TBXTools - Statistical\n*******************"
python3 -m evaluation.score --skip-B corpus/input_corpus.txt results/tbxtools/statistical/input_tbxtools.txt

echo "\nTask A - TBXTools - Linguistic\n*******************"
python3 -m evaluation.score --skip-B corpus/input_corpus.txt results/tbxtools/linguistic/input_tbxtools.txt

echo "\nTask A - QuickUMLS\n*******************"
python3 -m evaluation.score --skip-B corpus/input_corpus.txt results/quickumls/input_quickumls.txt

echo "\nTask A - ADR2OpenBrat\n*******************"
python3 -m evaluation.score --skip-B corpus/input_corpus.txt results/adr2openbrat/input_adr2openbrat.txt



