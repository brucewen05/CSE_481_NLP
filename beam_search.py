
import ngram as ng
import heapq as hq
import math

BEAM_WIDTH = 20

# for bigram, prev_words should either be a single hanzi
# or ng.START symbol
"""
prev_words: string of previous handzi
tokens: list of segmentated pinyin
length: the length of output phrase
k: number of best choices to return
"""
def beam_search(prev_words, tokens, length, k, predict_fn, training_result):
    # make sure the maximum length is no larger than the token length
    if len(tokens) < length:
        length = len(tokens)

    prev_level = [(0, None, prev_words)]

    # map used to back-construct the result phrase
    # it has the format: {"curr_word": list of(prev_word, log_prob)}
    back_map = {}

    for i in range(0, length):
        next_level = []
        # print("tokens:", tokens, "---------------")
        # print("before prev_level:", prev_level, "----------------")
        for j in range(0, len(prev_level)):
            print("prev word:", prev_level[j][2], "; cur token:" ,tokens[i], "!!!!!!")
            predictions = predict_fn(prev_level[j][2], tokens[i], training_result)
            top_k_predictions = hq.nlargest(BEAM_WIDTH, predictions, key=predictions.get)
            # manually do top k sort to save space
            # print("top k predictions:", top_k_predictions, "!!!!!!!!!")
            for p in top_k_predictions:
                if (len(next_level) < BEAM_WIDTH):
                                           #(log(prob),                prev_word,        curr_word)
                    hq.heappush(next_level, (math.log(predictions[p]), prev_level[j][2], p))
                else:
                    hq.heappushpop(next_level, (math.log(predictions[p]), prev_level[j][2], p))

        for log_prob, prev_word, curr_word in next_level:
            entry = back_map.setdefault(curr_word, [])
            # print("curr_word:", curr_word)
            entry.append((prev_word, log_prob)) # in case the same word is mapped more than one time
            # print(entry, "============")
        prev_level = next_level

    results = []
    for log_prob, prev_word, curr_word in prev_level:
        total_sum = 0.0
        phrase = ""
        cur = curr_word
        for i in range(0, length):
            # print("inside last for loop, cur is:", cur)
            curr_tuple_list = back_map[cur]
            curr_tuple = curr_tuple_list[0]
            if len(curr_tuple_list) > 1:
                curr_tuple = curr_tuple_list.pop()
            phrase = cur + phrase
            total_sum += curr_tuple[1]
            cur = curr_tuple[0]
        # print("done with one phrase===============")
        results.append((total_sum, phrase))

    results = sorted(results, key = lambda x: x[0], reverse=True)
    return list(map(lambda x: x[1], results))[: k]



