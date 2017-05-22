import tensorflow as tf
import string


def main():
    predictions = [[[('中', 0.9), ('终', 0.1), ('忠', 0.1)]],
                   [[('终', 0.9), ('忠', 0.1), ('中', 0.1)]],
                   [[('忠', 0.9), ('中', 0.1), ('终', 0.1)]],
                   [[('忠', 0.9), ('中', 0.1), ('终', 0.1)]]]
    dataset = [["^", "zhong", "中"],
               ["^", "zhong", "中"],
               ["^", "zhong", "中"],
               ["^", "zhong", "众"]]
    print(evaluate(dataset, predictions, '3'))

    # with tf.Session() as sess:
    #     print(evaluate_tf(dataset, predictions))


# ============== Metrics ==================
# prediction: list of phrases
def in_top_1(prediction, label):
    return in_top_k(prediction, label, 1)


def in_top_10(prediction, label):
    return in_top_k(prediction, label, 10)


def in_top_k(prediction, label, k):
    try:
        return prediction.index(label) < k
    except ValueError:
        return False


def normalize_text(s):
    """Lower text and remove punctuation and extra whitespace."""

    def white_space_fix(text):
        return ''.join(text.split())

    def remove_punc(text):
        exclude = set(string.punctuation)
        return ''.join(ch for ch in text if ch not in exclude)

    def lower(text):
        return text.lower()

    return white_space_fix(remove_punc(lower(s)))


def evaluate(target, predictions, k):
    scores = {}
    metric_fn = [in_top_1, in_top_10]

    if k != '1' and k != '10':
        in_top_k_metric = lambda pred, label: in_top_k(pred, label, int(k))
        in_top_k_metric.__name__ = "in_top_" + k
        metric_fn.append(in_top_k_metric)

    lens = {}
    for data, prediction in zip(target, predictions):
        #length_word = len(data.split()) - 1  # len of input. TODO: better way to get len of input
        sort_predictions = [[] for i in range(5)]
        for pred_per_len in prediction:
            for p in pred_per_len:
                words = p[0].split()
                try:
                    words.remove("UNK")
                except ValueError:
                    pass
                word = "".join(words)
                
                try:
                    sort_predictions[len(word) - 1].append(p)
                except IndexError:
                    pass
        prediction = sort_predictions
        length = -1
        for word in data.split():
            length += len(word)
        ground_truth = data.strip()
        ground_truth = "".join(ground_truth.split())
        if length > 3:
            print(ground_truth)
            print(prediction)
        try:
            lens[length] += 1
        except KeyError:
            lens[length] = 1
        try:
            prediction = ["".join(p[0].split()) for p in prediction[length]]
            for fn in metric_fn:
                try:
                    scores[fn.__name__ + '_len=' + str(length)] += fn(prediction, ground_truth)
                except KeyError:
                    scores[fn.__name__ + '_len=' + str(length)] = fn(prediction, ground_truth)
        except IndexError:
            for fn in metric_fn:
                try:
                    scores[fn.__name__ + '_len=' + str(length)] += 0
                except KeyError:
                    scores[fn.__name__ + '_len=' + str(length)] = 0
    
    
    scores = {fn: round(100.0 * score / lens[int(fn.split('=')[-1])], 2) for fn, score in scores.items()}
    return scores


# TODO: in_top_k targets out of range, etc
#
# ========== Tensorflow Evaluation Metrics ==================


# convert one-hot labels to targets
# e.g. labels = [[0, 0, 1, ... 0], [0, 1, 0, ..., 0]]
# return labels_argmax = [2, 1]
def one_hot_to_target_tf(labels):
    labels_argmax = tf.argmax(labels, 1)
    return labels_argmax


# logits = tf.constant([[0.1, 0.2, 0.4], [0.1, 0.2, 0.4], [0.1, 0.2, 0.4]])
# labels = tf.constant([0, 1, 2])
# correct_prediction = [False, False, True]
# accuracy = 0.33
def in_top_one_tf(logits, labels):
    correct_prediction = tf.nn.in_top_k(logits, labels, 1)
    accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))
    return accuracy


def in_top_ten_tf(logits, labels):
    correct_prediction = tf.nn.in_top_k(logits, labels, 10)
    accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))
    return accuracy


# get the rank of label in predictions
# predictions = ["中", "终", "忠"]
# labels = ["中"]
# return [0]
# predictions = ["中", "终", "忠"]
# labels = ["众"]
# return [-1]
def get_idx_tf(predictions, labels):
    mapping_strings = tf.constant(predictions)
    feats = tf.constant(labels)
    indices = tf.contrib.lookup.string_to_index(feats, mapping=mapping_strings, default_value=-1)
    return indices


# evaluate using tf functions.
def evaluate_tf(dataset, predictions):
    scores = {}
    metric_fn = [in_top_one_tf, in_top_ten_tf]
    labels = []
    logits = []
    for (context, pinyin, label), pred in zip(dataset, predictions):
        logits.append([p[1] for p in pred])
        pred = [p[0] for p in pred]
        try:
            labels.append(pred.index(label))
        except ValueError:
            labels.append(-1)
    # convert to tensors
    logits = tf.constant(logits)
    labels = tf.constant(labels)

    for fn in metric_fn:
        try:
            scores[fn.__name__] += fn(logits, labels).eval()
        except KeyError:
            scores[fn.__name__] = fn(logits, labels).eval()
    scores = {fn: 100.0 * score for fn, score in scores.items()}
    return scores


if __name__ == "__main__":
  main()
