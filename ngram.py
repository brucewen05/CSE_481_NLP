import sqlite3
import time
import operator
from nltk import ngrams
from collections import Counter

from sys import argv, stdin


START = '<S>'
END = '</s>'
filename = argv[1]
start_time = time.time()

print("Training on", filename)
#conn = sqlite3.connect('C:\\Users\\zjy\\sqlite\\lcmc.db3')
conn = sqlite3.connect(filename)
c = conn.cursor()
c.execute('')
c.execute('SELECT p.characters, s.characters FROM pinyin_full_sentences as p JOIN full_sentences as s '
          'where p.sentence_id = s.sentence_id and p.file_id = s.file_id and p.text_id = s.text_id')
conn.row_factory = sqlite3.Row
rows = c.fetchall()

unigrams = []
bigrams = []
for r in rows:
    unigrams.extend(list(r[1]))
    unigrams.append(START)
    bigrams.extend(ngrams(sequence=list(r[1]), n=2, left_pad_symbol=START, right_pad_symbol=END, pad_left=True, pad_right=True))
bigram_dict = Counter(bigrams)
unigram_dict = Counter(unigrams)

c.execute('SELECT p.char_num, p.character, w.characters FROM words as w JOIN pinyin_characters as p '
          'where p.sentence_id = w.sentence_id and p.file_id = w.file_id and p.text_id = w.text_id and p.word_num = w.word_num')
conn.row_factory = sqlite3.Row
rows = c.fetchall()

dictionary = {}
for index, pinyin, phrase in rows:
    try:
        dictionary[pinyin].add(list(phrase)[index - 1])
    except KeyError:
        dictionary[pinyin] = set(list(phrase)[index - 1])
print("Finish training: ", time.time() - start_time)


while (True) :
    print("Enter word_prev (e.g. \'中\'):")
    word_prev = stdin.readline()[:-1]
    print("Enter pinyin_cur （e.g. \'wen2\'）:")
    pinyin_cur = stdin.readline()[:-1]
    phrases = dictionary[pinyin_cur]
    print("possible phrases", phrases)
    suggestion = {}
    prob = float('-inf')
    for word in phrases:
        try:
            prob_cur = bigram_dict[word_prev, word] / float(unigram_dict[word_prev])
            if prob_cur != 0:
                suggestion[word] = prob_cur
        except KeyError:
            prob_cur = 0
    sorted_suggestion = sorted(suggestion.items(), key=operator.itemgetter(1))
    print("top suggestions:", suggestion)
    print()
conn.close()