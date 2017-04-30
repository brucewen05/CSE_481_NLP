import codecs

import os

cur_path = os.path.dirname(os.path.abspath(__file__))
# extracts valid full pinyins
full_path = cur_path + "/data/valid_pinyins.txt"
print(full_path)
with codecs.open(full_path, encoding='utf-8') as f:
    lines = f.readlines()
valid_pinyins = set([line.strip() for line in lines])

valid_prefixes = ["b", "p", "m", "f", "d", "t", "n", "l", "g", "k", "h", "j",
        "q", "x", "zh", "ch", "sh", "r", "z", "c", "s", "y", "w"]
invalid_single_char = ["i", "u", "v"]

full_pinyin_candidates = {}
pinyin_prefix_candidates = {}

# constructs candidate map

full_path = cur_path + "/data/pinyin_char_dictionary.txt"
print(full_path)
with codecs.open(full_path, encoding='utf-8') as f:
    lines = f.readlines()
for line in [line.strip() for line in lines]:
    tokens = line.split("=")
    full_py = tokens[0]
    for char in tokens[1].split(","):
        if full_py not in full_pinyin_candidates:
            full_pinyin_candidates[full_py] = []
        full_pinyin_candidates[full_py] += [char]
        
        if full_py[0] in valid_prefixes or full_py[:2] in valid_prefixes:
            prefix = full_py[:2] if len(full_py) > 2 and full_py[:2] in valid_prefixes \
                else full_py[0]
            if prefix not in pinyin_prefix_candidates:
                pinyin_prefix_candidates[prefix] = []
            pinyin_prefix_candidates[prefix] += [char]


def get_pinyin_candidates(pinyin_or_prefix, allow_prefix=True):
    if pinyin_or_prefix in valid_prefixes:
        return pinyin_prefix_candidates[pinyin_or_prefix]
    elif pinyin_or_prefix in valid_pinyins:
        return full_pinyin_candidates[pinyin_or_prefix]
    return None

def next_syllable(pinyin_input, allow_invalid_single=True):
    tokens = segment_with_hint(pinyin_input, allow_invalid_single)
    return tokens[0] if (len(tokens) > 0) else None

# hint - manually added pinyin boundaries. e.g. "xi'an"
def segment_with_hint(pinyin_input, allow_invalid_single=True):
    ps = pinyin_input.split("'")
    tokens = []
    for p in ps:
        res = segment_input(p, allow_invalid_single)
        if res is None:
            return None
        tokens += res
    # print(tokens)
    return tokens

# Dynamic programming - minimize the number of segmented tokens, where each token
# is either a valid prefix or a valid full pinyin, or [iuv] if allow_invalid_single.
def segment_input(pinyin_input, allow_invalid_single=True):
    n = len(pinyin_input)
    f = [float("inf") for i in range(n + 1)]
    prev = [None for i in range(n + 1)]
    f[0] = 0
    # #tokens for [0, i)
    for i in range(n + 1):
        for j in range(0, i):
            token = pinyin_input[j:i]
            if token in valid_pinyins or token in valid_prefixes or \
                    (allow_invalid_single and token in invalid_single_char):
                if f[i] > f[j] + 1: 
                    f[i] = f[j] + 1
                    prev[i] = j
    tokens = []
    p = n
    while prev[p] != None:
        token = pinyin_input[prev[p]:p]
        tokens = [token] + tokens
        p = prev[p]
    # print(f[n])
    # print(tokens)
    return tokens

def get_all_candidates_chars():
    res = set()
    for chars in full_pinyin_candidates.values():
        res = res.union(set(chars))
    return res

if __name__ == "__main__":
    # tests
    assert segment_with_hint("aaa") == ["a", "a", "a"]
    assert segment_with_hint("nihaoa") == ["ni", "hao", "a"]
    assert segment_with_hint("weidlingxmzx") == ["wei", "d", "ling", "x", "m", "z", "x"]
    assert segment_with_hint("renmingongheguo") == ["ren", "min", "gong", "he", "guo"]
    assert segment_with_hint("shanxixi'an") == ["shan", "xi", "xi", "an"]
    assert segment_with_hint("'xx'''x''") == ["x", "x", "x"]
    assert segment_with_hint("u") == ["u"]
    assert segment_with_hint("u", allow_invalid_single=False) == []
    
    assert next_syllable("nihaoa") == "ni"

    assert set(get_pinyin_candidates("diu")) == set(["铥","丢","銩","丟","颩"])
    assert set(["铥","丢","銩","丟","颩"]).issubset(set(get_pinyin_candidates("d")))
    assert not set(["丢"]).issubset(set(get_pinyin_candidates("di")))
    assert set(get_pinyin_candidates("a")) == set(["呵","吖","錒","啊","阿","嗄","锕","腌"])
    assert get_pinyin_candidates("u") is None
