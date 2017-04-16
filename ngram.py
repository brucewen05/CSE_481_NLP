import sqlite3
import time
import operator
import pickle
from nltk import ngrams
from collections import Counter

from sys import argv, stdin, exit

"""
To train a model, do `python3 -t training_filename`
To load an existing model, do `python3 -l model_file`
"""

START = '<S>'
END = '</S>'

# This function trains a model based on the
# training file, and writes the training result:
# [unigram_dict, bigram_dict, dictionary] to disk
# as a list format as well as return the result
# to the caller function
def train(training_filename, output_filename):
    start_time = time.time()

    print("Training on ", training_filename)
    conn = sqlite3.connect(training_filename)
    c = conn.cursor()
    rows = c.execute('SELECT p.characters, s.characters FROM pinyin_full_sentences as p JOIN full_sentences as s '
              'where p.sentence_id = s.sentence_id and p.file_id = s.file_id and p.text_id = s.text_id')

    unigrams = [START]
    bigrams = []
    for r in rows:
        unigrams.extend(list(r[1]))
        bigrams.extend(ngrams(sequence=list(r[1]), n=2, left_pad_symbol=START, right_pad_symbol=END, pad_left=True, pad_right=True))
    bigram_dict = Counter(bigrams)
    unigram_dict = Counter(unigrams)

    rows = c.execute('SELECT p.char_num, p.character, w.characters as tup FROM words as w JOIN pinyin_characters as p '
              'where p.sentence_id = w.sentence_id and p.file_id = w.file_id and p.text_id = w.text_id and p.word_num = w.word_num')

    dictionary = {}
    for index, pinyin, phrase in rows:
        try:
            dictionary[pinyin[:-1]].add(list(phrase)[index - 1])
        except KeyError:
            dictionary[pinyin[:-1]] = set(list(phrase)[index - 1])
    print("Finish training: ", time.time() - start_time)
    conn.close()
    training_result = [unigram_dict, bigram_dict, dictionary]

    print("Writing trained model to ", output_filename)
    with open(output_filename, 'wb') as f:
        pickle.dump(training_result, f, pickle.HIGHEST_PROTOCOL)
    print("Done writing to", output_filename)
    return training_result

def load_model(model_file):
    print("Loading model from", model_file, "...")
    with open(model_file, 'rb') as f:
        model = pickle.load(f)
        print("Done loading")
        return model

def predict(word_prev, pinyin_cur, training_result):
    # bad style...
    unigram_dict = training_result[0]
    bigram_dict = training_result[1]
    dictionary = training_result[2]

    phrases = dictionary[pinyin_cur]
    suggestion = {}
    for phrase in phrases:
        try:
            suggestion[phrase] = bigram_dict[word_prev, phrase] + 1 / float(unigram_dict[word_prev]) + 1
        except KeyError:
            pass
    suggestion = sorted(suggestion, key=lambda k: suggestion[k], reverse=True)
    return suggestion


if __name__ == "__main__":
    if len(argv) != 3:
        print("Usage: python3", argv[0], "[-t|-l] [training_filename|model_file]")
        exit(1)

    training_result = None
    if argv[1] == "-t":
        training_result = train(argv[2], "model/ngrams_model")
    elif argv[1] == "-l":
        training_result = load_model(argv[2])
    else:
        print("Illegal flag", argv[1])
        exit(1)

    word_prev = START
    while (True) :
        print("Enter pinyin_cur （e.g. \'zhong\'）:")
        pinyin_cur = stdin.readline()[:-1]
        if  not pinyin_cur:
            break

        suggestion = predict(word_prev, pinyin_cur, training_result)
        print("suggestions:", suggestion)
        print("Enter Selection:")
        selection = stdin.readline()[:-1]
        if not selection:
            break
        word_prev = suggestion[int(selection)]
        print(word_prev)


