import sqlite3
import time
from nltk import ngrams
from collections import Counter
from sys import argv, stdin


START = '<S>'
END = '</S>'
filename = argv[1]
start_time = time.time()

print("Training on")
# conn = sqlite3.connect('C:\\Users\\zjy\\sqlite\\lcmc.db3')
conn = sqlite3.connect(filename)
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

word_prev = START
while (True) :
    print("Enter pinyin_cur （e.g. \'zhong\'）:")
    pinyin_cur = stdin.readline()[:-1]
    phrases = dictionary[pinyin_cur]
    print("Possible phrases", phrases)
    suggestion = {}
    for phrase in phrases:
        try:
            suggestion[phrase] = bigram_dict[word_prev, phrase] + 1 / float(unigram_dict[word_prev]) + 1
        except KeyError:
            pass
    suggestion = sorted(suggestion, key=lambda k: suggestion[k], reverse=True)

    print("suggestions:", suggestion)
    print("Enter Selection:")
    word_prev = suggestion[int(stdin.readline()[:-1])]
    print(word_prev)
conn.close()