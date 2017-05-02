import sys
import re
import pprint


import pinyin_util as pu
import beam_search as bs


dummy_list1 = [u"\u54C8", u"\u563F", u"\u5475", u"\u597D", 
               u"\u4E0D", u"\u54E6", u"\u5662", u"\u77E5", u"\u9053"]

dummy_list2 = [u"\u54C8\u54C8", u"\u563F\u563F", 
               u"\u5475\u5475", u"\u597D\u597D\u597D\u597D\u597D\u597D\u597D", 
               u"\u4E0D\u4E0D", u"\u54E6\u54E6", 
               u"\u5662\u5662", u"\u77E5\u77E5", u"\u9053\u9053\u9053"]

# predictions_list: results from beam search
def sort_and_merge_predictions(predictions_list, max_items=10, cutoff=3):
    flat_list = []
    for sublist in predictions_list:
        if len(sublist[0][0]) > cutoff:
            flat_list.append(sublist[0])
        else:
            flat_list.extend(sublist)
            # pprint.pprint(flat_list)
    ranked = sorted(flat_list, key=lambda x: x[1] / len(x[0]), reverse=True)[:max_items]
    return [x[0] for x in ranked]

# helper function to print out the choice nicely
def print_predictions(predictions):
    for i in range(0, len(predictions)):
        print("{num: ^{length}}".format(num = i + 1, length = int(round(len(predictions[i]) * 2))), end=" ")
    print()

    for i in range(0, len(predictions)):
        print(predictions[i], end = " ")

    print()




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

    if (c == " ") :
        selected_chars = selected_chars[:-1]
        print(selected_chars)
        continue

    if (num.match(c)):
        selected_chars += cur_predictions[int(c) - 1]
    else:
        # input only contains alphabetic value, assume it is pinyin string
        if (alphabet.match(c)) :
            predictions_list = bs.ngram_beam_search(selected_chars, pu.segment_with_hint(c))
            cur_predictions = sort_and_merge_predictions(predictions_list)
        # input contains none-alphabetic value, assume it is punctuations
        else:
            selected_chars += c
    # print(cur_predictions)
    print_predictions(cur_predictions)
    print(selected_chars)
