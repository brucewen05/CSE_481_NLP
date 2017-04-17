import sys
import re


import ngram as ng
import pinyin_util as pu
import beam_search as bs


dummy_list1 = [u"\u54C8", u"\u563F", u"\u5475", u"\u597D", 
               u"\u4E0D", u"\u54E6", u"\u5662", u"\u77E5", u"\u9053"]

dummy_list2 = [u"\u54C8\u54C8", u"\u563F\u563F", 
               u"\u5475\u5475", u"\u597D\u597D\u597D\u597D\u597D\u597D\u597D", 
               u"\u4E0D\u4E0D", u"\u54E6\u54E6", 
               u"\u5662\u5662", u"\u77E5\u77E5", u"\u9053\u9053\u9053"]

cur_list = 1
def get_predictions(selected_chars, typed_chars):
    global cur_list
    if (cur_list == 1):
        cur_list = 2
        return dummy_list1
    else:
        cur_list = 1
        return dummy_list2

# helper function to print out the choice nicely
def print_predictions(predictions):
    for i in range(0, len(predictions)):
        print("{num: ^{length}}".format(num = i + 1, length = int(round(len(predictions[i]) * 2))), end=" ")
    print()

    for i in range(0, len(predictions)):
        print(predictions[i], end = " ")

    print()


training_result = ng.load_model("model/ngrams_model")

selected_chars = ""
cur_predictions = dummy_list1

print_predictions(cur_predictions)

#regular expression to judge if a string only contains alphabet
alphabet = re.compile("^[a-z]+$")
#regular expression to judge if a string only contains numeric value
num = re.compile("^[0-9]+$")

while (True) :
    c = sys.stdin.readline()[:-1]
    if not c:
        break

    if (num.match(c)):
        selected_chars += cur_predictions[int(c) - 1]
    else:
        # input only contains alphabetic value, assume it is pinyin string
        if (alphabet.match(c)) :
            tokens = pu.segment_with_hint(c)
            if selected_chars == "":
                cur_predictions = bs.beam_search(ng.START, tokens, len(tokens), 9, ng.predict, training_result)
            else:
                cur_predictions = bs.beam_search(selected_chars[-1], tokens, len(tokens), 9, ng.predict, training_result)
        # input contains none-alphabetic value, assume it is punctuations
        else:
            selected_chars += c
    # print(cur_predictions)
    print_predictions(cur_predictions)
    print(selected_chars)

"""
while (True) :
    c = sys.stdin.readline()[:-1]
    if not c:
        break

    if (num.match(c)):
        selected_chars += cur_predictions[int(c) - 1]
        cur_predictions = ng.predict(selected_chars[-1], "", training_result)
    else:
        # input only contains alphabetic value, assume it is pinyin string
        if (alphabet.match(c)) :
            tokens = pu.segment_with_hint(c)
            if selected_chars == "":
                cur_predictions = ng.predict(ng.START, tokens[0], training_result)
            else:
                cur_predictions = ng.predict(selected_chars[-1], tokens[0], training_result)
        # input contains none-alphabetic value, assume it is punctuations
        else:
            selected_chars += c
            cur_predictions = ng.predict(selected_chars[-1], "", training_result)

    print_predictions(cur_predictions)
    print(selected_chars)
"""
