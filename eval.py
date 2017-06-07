import json
import sys
import os
import pprint
import pinyin_util as pu
import beam_search as bs
import metric
import argparse

import eval_inference_handler as s2s
import ngram as ng

#unigram_dict, bigram_dict, dictionary = ng.load_model("model/ngrams_model")

def predict(config):
    pprint.pprint(config)
    if config.model == 'bs.ngram_beam_search':
        model_func = bs.ngram_beam_search
    elif config.model == 's2s':
        model_func = s2s.query
    else:
        raise NotImplementedError()

    source = load_data(config.test_data_source)
    target = load_data(config.test_data_target)
    predictions = []
    ground_truth = []
    index = 0
    for truth, data in zip(target, source):
        if index % 10000 == 0:
            print(index)
            pprint.pprint(metric.evaluate(ground_truth, predictions, config.k))
        index += 1
        data = data.split('|')
        (context, pinyin) = data
        context = "".join(context.split())
        pinyin = pu.segment_with_hint(metric.normalize_text(pinyin))
        context = "".join(context.split())
        prediction = model_func(context.strip(), pinyin)
        #print(prediction)
        #print(truth)
        predictions.append(prediction)
        ground_truth.append(truth)
    pprint.pprint(metric.evaluate(target, predictions, config.k))


def load_json_data(filename):
    try:
        with open(filename, 'r') as f:
            data = json.load(f)
            return data
    except IOError:
        usage()
        print('IO error')
        sys.exit(2)

def load_data(filename):
    data = []
    try:
        with open(filename, 'r', encoding="utf8") as f:
            for line in f:
                data.append(line)
        return data
    except IOError:
        usage()
        print('IO error', filename)
        sys.exit(2)


def usage():
    pass

def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--test_data_source', default=os.path.join('/data', 'test', 'mixed_abbrs.source'))
    parser.add_argument('--test_data_target', default=os.path.join('/data', 'test', 'mixed_abbrs.target'))
    parser.add_argument('--model', default='bs.ngram_beam_search')
    parser.add_argument('--k', default='10')
    parser.add_argument('--device_type', default='cpu')
    parser.add_argument('--num_devices', type=int, default=1)
    return parser

if __name__ == "__main__":
    parser = get_parser()
    config = parser.parse_args()
    predict(config)


