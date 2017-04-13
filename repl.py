import sys

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


selected_chars = ""
typed_chars = ""
cur_predictions = dummy_list1

print_predictions(cur_predictions)

while (True) :
    c = sys.stdin.read(1)
    sys.stdin.read(1) #discard the enter char
    if not c:
        break
    elif (c >= "1" and c <= "9"):
        # right now, assume we are choosing the top 9 predictions
        # if a user hits any number between 1 to 9,
        # then the user wants to pick an item from the current predictions
        selected_chars += cur_predictions[int(c) - 1]
        typed_chars = ""
        cur_predictions = get_predictions(selected_chars, typed_chars)
    elif (c >= "a" and c <= "z"):
        typed_chars += c
        cur_predictions = get_predictions(selected_chars, typed_chars)
    print_predictions(cur_predictions)
    print(selected_chars + typed_chars)
