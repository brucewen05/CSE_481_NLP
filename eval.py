import json
import sys
import os
import pprint
import pinyin_util as pu
import beam_search as bs
import metric
import argparse


def predict(config):
    pprint.pprint(config)
    if config.model == 'bs.ngram_beam_search':
        model_func = bs.ngram_beam_search
    else:
        raise NotImplementedError()

    testset = load_data(config.test_data_dir)
    predictions = []
    for data in testset:
        (context, pinyin, label) = data
        prediction = model_func(context, pu.segment_with_hint(pinyin.replace(" ", "")))
        predictions.append(prediction)
    pprint.pprint(metric.evaluate(testset, predictions, config.k))


def load_data(filename):
    try:
        with open(filename, 'r') as f:
            data = json.load(f)
            return data
    except IOError:
        usage()
        print('IO error')
        sys.exit(2)


def usage():
    pass

def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--test_data_dir', default=os.path.join('data', 'data_lcmc_clean.sample'))
    parser.add_argument('--model', default='bs.ngram_beam_search')
    parser.add_argument('--k', default='10')
    parser.add_argument('--device_type', default='cpu')
    parser.add_argument('--num_devices', type=int, default=1)
    return parser

if __name__ == "__main__":
    parser = get_parser()
    config = parser.parse_args()
    predict(config)


