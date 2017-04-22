import re
import json
import codecs
import pickle
import lcmc_queries as lcmc
import pinyin_util as pu

def build_parallel_paragraphs_lcmc():
    # each paragraph[0] = "^" as START symbol
    char_paragraphs = []
    pinyin_paragraphs = []

    for tup in lcmc.get_char_paragraphs():
        char_paragraphs.append(list(tup[0]))

    for tup in lcmc.get_pinyin_paragraphs():
        # drop tunes and add paddings
        p = re.sub(r'([a-z]+)[0-9] *', r' \1 ', tup[0])
        p = re.sub(r'([^a-z ])', r' \1 ', p)
        # fix "uu"=>"v" in lcmc pinyin
        p = re.sub(r'uu', r'v', p)        
        pinyin_paragraphs.append(p.split())

    assert len(char_paragraphs) == len(pinyin_paragraphs)
    return list(zip(char_paragraphs, pinyin_paragraphs))


def build_parallel_paragraphs_from_txt(filename):
    # each paragraph[0] = "^" as START symbol
    char_paragraphs = []
    pinyin_paragraphs = []

    with codecs.open(filename, encoding='utf-8') as f:
        lines = f.readlines()
    lines = [x.strip() for x in lines]
    lines = list(set(lines))
    
    for i in range(len(lines)):
        parts = lines[i].split('==>')
        p = re.sub(r'([^a-z ])', r' \1 ', "^" + parts[1])
        char_paragraphs.append(list("^" + parts[0]))
        pinyin_paragraphs.append(p.split())
    return list(zip(char_paragraphs, pinyin_paragraphs))

    
# min_paragraph_len includes "^"
# first_n: only extract the first n triples
def extract_triples(paragraph_pairs, context_window=10, max_input_window=5, first_n=None, min_paragraph_len=6):
    # triples[i] = (context, pinyins, chars)
    triples = []
    all_valid_chars = pu.get_all_candidates_chars()

    for pp in paragraph_pairs:
        if len(pp[0]) != len(pp[1]):
            # print(''.join(pp[0]) + " ==> " + ' '.join(pp[1]))
            # weird encoding error in the dataset, skip
            continue
        if len(pp[0]) < min_paragraph_len:
            continue

        # TODO: Consider only putting cursor and input window on word boundaries
        for cursor in range(1, len(pp[0])):
            for input_window_end in range(cursor + 1, min(cursor + max_input_window + 1, len(pp[0]))):
                if len([i for i in range(cursor, input_window_end) if not pp[0][i] in all_valid_chars]) > 0:
                    break
                context = pp[0][max(0, cursor - context_window):cursor]
                pinyins = pp[1][cursor:input_window_end]
                chars = pp[0][cursor:input_window_end]

                if (len(chars) > 0):
                    triples.append((" ".join(context), " ".join(pinyins), " ".join(chars)))
                    if first_n is not None and len(triples) == first_n:
                        return triples
    # print(len(triples))
    return triples


if __name__ == "__main__":
    print("Extracting sms data...")
    # 61 MB
    with open('data/sms_clean.data', 'wb') as outfile:
        data = extract_triples(build_parallel_paragraphs_from_txt('data/nus_sms_chinese.txt'), min_paragraph_len=4)        
        pickle.dump(data, outfile, pickle.HIGHEST_PROTOCOL)
    with open('data/sms_clean.sample', 'w') as outfile:
        sample = json.dumps(data[:100], indent=4, sort_keys=True)
        outfile.write(sample)

    print("Extracting lcmc data...")
    # 323 MB
    with open('data/lcmc_clean.data', 'wb') as outfile:
        data = extract_triples(build_parallel_paragraphs_lcmc())
        pickle.dump(data, outfile, pickle.HIGHEST_PROTOCOL)
    with open('data/lcmc_clean.sample', 'w') as outfile:
        sample = json.dumps(data[:100], indent=4, sort_keys=True)
        outfile.write(sample)

    print("Extracting weibo data...")
    with open('data/weibo_clean.data', 'wb') as outfile:
        data = extract_triples(build_parallel_paragraphs_from_txt('data/weibo.txt'), min_paragraph_len=4, first_n=1000000)
        pickle.dump(data, outfile, pickle.HIGHEST_PROTOCOL)
    with open('data/weibo_clean.sample', 'w') as outfile:
        sample = json.dumps(data[:100], indent=4, sort_keys=True)
        outfile.write(sample)