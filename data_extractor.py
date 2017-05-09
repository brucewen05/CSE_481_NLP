import re
import json
import codecs
import pickle
import operator
import random
import lcmc_queries as lcmc
import pinyin_util as pu
import numpy as np

random.seed(1)

# total size of lines to read from txt file
# used only for debugging purpose
MAX_LINE_NUMBER = 3

# probability to generate an abbreviation tuple
GENERATE_ABBREVIATION_TUPLE_PROBABILITY = 0.5
# probability to use abbreviation for a given
# pinyin token
GENERATE_ABBREVIATION_TOKEN_PROBABILITY = 0.8


# probability to use typo for a given pinyin token
GENERATE_TYPO_TUPLE_PROBABILITY = 0.5
# probability to generate a typo for each letter
GENERATE_TYPO_LETTER_PROBABILITY = 0.8


def print_and_log(s):
    print(s)
    summary_file.write(str(s) + "\n")


def build_parallel_paragraphs_lcmc():
    # each paragraph[0] = "^" as START symbol
    char_paragraphs = []
    pinyin_paragraphs = []
    segment_positions = []

    for tup in lcmc.get_char_paragraphs():
        segments = [len(x) for x in tup[0].split('|') if x != '']
        segment_positions.append(np.cumsum(segments))
        p = re.sub(r'\|', r'', tup[0])
        char_paragraphs.append(list(p))

    for tup in lcmc.get_pinyin_paragraphs():
        # drop tunes and add paddings
        p = re.sub(r'\|', r'', tup[0])
        p = re.sub(r'([a-z]+)[0-9] *', r' \1 ', p)
        p = re.sub(r'([^a-z ])', r' \1 ', p)
        # fix "uu"=>"v" in lcmc pinyin
        p = re.sub(r'uu', r'v', p)        
        pinyin_paragraphs.append(p.split())

    assert len(char_paragraphs) == len(pinyin_paragraphs)
    return list(zip(char_paragraphs, pinyin_paragraphs, segment_positions))


def build_parallel_paragraphs_from_txt(filename, debug=False):
    # each paragraph[0] = "^" as START symbol
    char_paragraphs = []
    pinyin_paragraphs = []
    segment_positions = []

    with codecs.open(filename, encoding='utf-8') as f:
        lines = f.readlines()

    if (debug):
        lines = lines[:MAX_LINE_NUMBER]

    lines = [x.strip() for x in lines]
    lines = sorted(list(set(lines)))
    
    for i in range(len(lines)):
        parts = lines[i].split(' ==> ')
        if len(parts) == 2:
            parts[0] = "^|" + parts[0]
            parts[1] = "^|" + parts[1]
            segments = [len(x) for x in parts[0].split('|') if x != '']
            segment_positions.append(np.cumsum(segments))
            parts[0] = re.sub(r'\|', r'', parts[0])
            parts[1] = re.sub(r'\|', r'', parts[1])
            p = re.sub(r'([^a-z ])', r' \1 ', parts[1])
            char_paragraphs.append(list(parts[0]))
            pinyin_paragraphs.append(p.split())
    return list(zip(char_paragraphs, pinyin_paragraphs, segment_positions))

    
# min_paragraph_len includes "^"
# first_n: only extract the first n triples
def extract_triples(paragraph_pairs,
        context_window=10,
        max_input_window=5,
        first_n=None,
        min_paragraph_len=6,
        add_abbr=True,
        add_typo=True,):
    # print_and_log(len(paragraph_pairs))
    # triples[i] = (context, pinyins, chars)
    triples = []
    all_valid_chars = pu.get_all_candidates_chars()

    for pp in paragraph_pairs:
        if len(pp[0]) != len(pp[1]):
            # weird encoding error in the dataset, skip
            continue
        if len(pp[0]) < min_paragraph_len:
            continue
        segment_positions = pp[2]
        # only put cursor and input window on word boundaries
        for cursor in range(1, len(pp[0])):
            if not cursor in segment_positions:
                continue
            for input_window_end in range(cursor + 1, min(cursor + max_input_window + 1, len(pp[0]))):
                if len([i for i in range(cursor, input_window_end) if not pp[0][i] in all_valid_chars]) > 0:
                    break
                if not input_window_end in segment_positions:
                    continue
                context = pp[0][max(0, cursor - context_window):cursor]
                pinyins = pp[1][cursor:input_window_end]
                #print_and_log(pinyins)
                chars = pp[0][cursor:input_window_end]

                if (len(chars) > 0):
                    triples.append((" ".join(context), " ".join(pinyins), " ".join(chars)))
                    if first_n is not None and len(triples) == first_n:
                        return triples
                    if (add_abbr and random.random() < GENERATE_ABBREVIATION_TUPLE_PROBABILITY):
                        abbreviation_pinyins = generate_abbreviation_noise(pinyins, GENERATE_ABBREVIATION_TOKEN_PROBABILITY)
                        if (abbreviation_pinyins is not None and abbreviation_pinyins != pinyins):
                            triples.append((" ".join(context), " ".join(abbreviation_pinyins), " ".join(chars)))
                    if (add_typo and random.random() < GENERATE_TYPO_TUPLE_PROBABILITY):
                        typo_pinyins = generate_typo_noise(pinyins, GENERATE_TYPO_LETTER_PROBABILITY)
                        if (typo_pinyins != pinyins):
                            triples.append((" ".join(context), " ".join(typo_pinyins), " ".join(chars)))
    print_and_log(len(triples))
    random.shuffle(triples)
    return triples

def generate_abbreviation_noise(pinyins, prob):
    """
    make a noisy copy of the original pinyin tokens
    such that each pinyin token has 'prob' probability
    of being replaced by its abbreviation.

    Note: This function guaranteens that when combining
    all the tokens in the result array and then splitting
    it again using segment_with_hint() function in pinyin_uitl.py,
    the size of the array after splitting is the same as the original
    'pinyins' array. 
    i.e. the situation where the pinyins array is
    ["tian", "an", "men"] and the result array is
    ["t", "a", "m"] is not possible since when combining
    "t" with "a", it forms a valid pinyin token "ta"; thus when
    splitting the pinyin string "tam", it will be splitted into
    ["ta", "m"], which is shorter than the original array.
    """
    results = []
    for pinyin_token in pinyins:
        abbreviation = pinyin_token[0:2]
        if (abbreviation != "zh" 
            and abbreviation != "ch" 
            and abbreviation != "sh"):
            abbreviation = pinyin_token[0]
        results.append(abbreviation)

    for i in range(0, len(results)):
        if (random.random() > prob):
            results[i] = pinyins[i]

    # print_and_log("orignal array:", pinyins)
    # print_and_log("abbreviation array:", results)
    segment_results_result = pu.segment_with_hint("".join(results))
    segment_original_result = pu.segment_with_hint("".join(pinyins))
    
    # print_and_log("segmentation result for noisy result:", segment_results_result)
    # print_and_log("segmentation result for orignal array:", segment_original_result)
    if (len(segment_results_result) == len(segment_original_result)):
        #print_and_log("returning result")
        # to make sure the result is not the same as the original array
        for i in range(0, len(results)):
            if (pinyins[i] != results[i]):
                return results
    
    return None



def generate_typo_noise(pinyins, prob):
    """
    Generate typo noise of the given pinyin tokens
    For each letter, a mutation is randomly chosen from:
        - Transposed with adjacent letter on a qwerty keyboard
        - Removed.
        - Adjacent letter is added before/after the current letter.
        - Switched with its adjacent letter (in pinyin token).
    """
    results = []
    for pinyin_token in pinyins:
        typo = list(pinyin_token)
        for i in range(len(typo)):
            transpose, possibility = pu.typo_transpose_letter[typo[i]]
            transposeLetter = transpose[np.random.choice(len(possibility), p=possibility)]
            if random.random() < prob:
                typo[i] = random.choice(
                    [transposeLetter,            # Transpose adjacent letter on keyboard
                     transposeLetter + typo[i],  # insert letter before
                     typo[i] + transposeLetter,  # insert letter after
                     "",                         # remove letter
                     typo[i+1] if i == 0 and i != len(typo) - 1    # 1st:switch with adjacent letter (left)
                     else typo[i-1] if i == len(typo) - 1          # last:switch with adjacent letter (right)
                     else random.choice([typo[i+1], typo[i-1]])])  # switch with left/right adjacent letter

        results.append(''.join(typo))
    # print_and_log("orignal array:" + pinyins)
    # print_and_log("abbreviation array:" + results)
    return results


def gen_vocab(raw_file, filename):
    with codecs.open(raw_file, encoding='utf-8') as f:
        lines = f.readlines()
    lines = [line.strip() for line in lines]
    c = {}
    for line in lines:
        tokens = list(line)
        for token in tokens:
            if not token in c:
                c[token] = 0
            c[token] = c[token] + 1

    with codecs.open(filename, 'w', encoding='utf-8') as fout:
        for k in sorted(c.keys()):
            fout.write(k + "\t" + str(c[k]) + "\n")

def gen_source_target_files(triples, filename):
    # train dev test = 7:1:2
    n = len(triples)
    train_size = int(n * .7)
    dev_size = int(n * .1)
    test_size = n - train_size - dev_size
    print_and_log("train: " + str(train_size))
    print_and_log("dev: " + str(dev_size))
    print_and_log("test: " + str(test_size))

    with codecs.open("data/train/" + filename + ".source", 'w', encoding='utf-8') as train_source:
        with codecs.open("data/train/" + filename + ".target", 'w', encoding='utf-8') as train_target:
            with codecs.open("data/dev/" + filename + ".source", 'w', encoding='utf-8') as dev_source:
                with codecs.open("data/dev/" + filename + ".target", 'w', encoding='utf-8') as dev_target:
                    with codecs.open("data/test/" + filename + ".source", 'w', encoding='utf-8') as test_source:
                        with codecs.open("data/test/" + filename + ".target", 'w', encoding='utf-8') as test_target:
                            
                            for tup in triples[:train_size]:
                                train_source.write(tup[0] + " | " + " ".join(list("".join(tup[1].split(" ")))) + "\n")
                                train_target.write(tup[2] + "\n")
                            
                            for tup in triples[train_size:train_size + dev_size]:
                                dev_source.write(tup[0] + " | " + " ".join(list("".join(tup[1].split(" ")))) + "\n")
                                dev_target.write(tup[2] + "\n")
                            
                            for tup in triples[train_size + dev_size:]:
                                test_source.write(tup[0] + " | " + " ".join(list("".join(tup[1].split(" ")))) + "\n")
                                test_target.write(tup[2] + "\n")

if __name__ == "__main__":
    summary_file = open("data/data_summary.txt", "w")

    print_and_log("Generating vocab...")

    gen_vocab("data/weibo.txt", "data/vocab/weibo")
    gen_vocab("data/nus_sms_chinese.txt", "data/vocab/sms")
    gen_vocab("data/wiki.txt", "data/vocab/wiki")

    print_and_log("Extracting sms data...")
    pp_sms = build_parallel_paragraphs_from_txt('data/nus_sms_chinese.txt')

    print_and_log("clean")
    gen_source_target_files(extract_triples(pp_sms, min_paragraph_len=4, add_abbr=False, add_typo=False), "sms_clean")
    print_and_log("abbrs")
    gen_source_target_files(extract_triples(pp_sms, min_paragraph_len=4, add_abbr=True, add_typo=False), "sms_abbrs")
    print_and_log("typos")
    gen_source_target_files(extract_triples(pp_sms, min_paragraph_len=4, add_abbr=False, add_typo=True), "sms_typos")

    print_and_log("Extracting lcmc data...")
    pp_lcmc = build_parallel_paragraphs_lcmc()
    print_and_log("clean")
    gen_source_target_files(extract_triples(pp_lcmc, min_paragraph_len=6, add_abbr=False, add_typo=False), "lcmc_clean")
    print_and_log("abbrs")
    gen_source_target_files(extract_triples(pp_lcmc, min_paragraph_len=6, add_abbr=True, add_typo=False), "lcmc_abbrs")
    print_and_log("typos")
    gen_source_target_files(extract_triples(pp_lcmc, min_paragraph_len=6, add_abbr=False, add_typo=True), "lcmc_typos")

    print_and_log("Extracting weibo data...")
    pp_weibo = build_parallel_paragraphs_from_txt('data/weibo.txt')
    print_and_log("clean")
    gen_source_target_files(extract_triples(pp_weibo, min_paragraph_len=4, add_abbr=False, add_typo=False), "weibo_clean")
    print_and_log("abbrs")
    gen_source_target_files(extract_triples(pp_weibo, min_paragraph_len=4, add_abbr=True, add_typo=False), "weibo_abbrs")
    print_and_log("typos")
    gen_source_target_files(extract_triples(pp_weibo, min_paragraph_len=4, add_abbr=False, add_typo=True), "weibo_typos")

    print_and_log("Extracting wiki data...")
    pp_wiki = build_parallel_paragraphs_from_txt('data/wiki.txt')
    print_and_log("clean")
    gen_source_target_files(extract_triples(pp_wiki, min_paragraph_len=4, add_abbr=False, add_typo=False), "wiki_clean")
    print_and_log("abbrs")
    gen_source_target_files(extract_triples(pp_wiki, min_paragraph_len=4, add_abbr=True, add_typo=False), "wiki_abbrs")
    print_and_log("typos")
    gen_source_target_files(extract_triples(pp_wiki, min_paragraph_len=4, add_abbr=False, add_typo=True), "wiki_typos")

    summary_file.close()
