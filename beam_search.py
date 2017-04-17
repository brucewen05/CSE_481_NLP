import math
import heapq
import ngram as ng

def ngram_beam_search(prev_context, pinyin_syllables, top_k=10, beam_width=100):
    def predict_fn_ngram(prev_words, cur_pinyin):
        if len(prev_words) == 0:
            last_word = ng.START if prev_context == "" else prev_context[-1]
        else:
            last_word = prev_words[-1]
        return ng.predict(last_word, cur_pinyin)
    return beam_search(pinyin_syllables, predict_fn_ngram, top_k, beam_width)


# returns a list of [k * (predtion, log_prob)] for length 1..n
# predict_fn: function(prev_words_string, cur_pinyin)
def beam_search(pinyin_syllables, predict_fn, top_k, beam_width):    
    assert top_k < beam_width

    def truncate_dict(d, keep_n):
        temp = d
        d = {}
        for key in heapq.nlargest(keep_n, temp, key=temp.get):
            d[key] = temp[key]
        return d

    n = len(pinyin_syllables)
    # one list of dict(chars, log_prob) per length
    phrase_prob = [{} for i in range(n + 1)]
    phrase_prob[0][""] = 0.

    results = [[] for i in range(n)]
    for i in range(1, n + 1):
        for prev_words, prev_prob in phrase_prob[i - 1].items():
            predictions = predict_fn(prev_words, pinyin_syllables[i - 1])
            for word, prob in predictions.items():
                new_words = prev_words + word
                if new_words not in phrase_prob[i] or \
                        phrase_prob[i][new_words] < prev_prob + math.log(prob):
                    phrase_prob[i][new_words] = prev_prob + math.log(prob)

        phrase_prob[i] = truncate_dict(phrase_prob[i], beam_width)
        best_predictions = heapq.nlargest(top_k, phrase_prob[i], key=phrase_prob[i].get)
        results[i - 1] = [(words, phrase_prob[i][words]) for words in best_predictions]
    
    return results


if __name__ == "__main__":
    pys = ["wo", "ai", "bei", "jing", "tian", "an", "men"]
    res = ngram_beam_search("", pys, top_k=5)
    for i in range(len(res)):
        for j in range(len(res[i])):
            print(res[i][j][0] + " " + str(res[i][j][1] / len(res[i][j][0])))
