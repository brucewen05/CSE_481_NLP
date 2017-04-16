
with open("data/valid_pinyins.txt") as f:
    lines = f.readlines()
valid_pinyins = set([line.strip() for line in lines])

valid_prefixes = ["b", "p", "m", "f", "d", "t", "n", "l", "g", "k", "h", "j",
        "q", "x", "zh", "ch", "sh", "r", "z", "c", "s", "y", "w"]
invalid_single_char = ["i", "u", "v"]

# Does not handle errors (caller should check if appropriate). e.g. "u" as input
# hint - manually added pinyin boundaries. e.g. "xi'an"
def segment_with_hint(pinyin_input, allow_invalid=True):
    ps = pinyin_input.split("'")
    tokens = []
    for p in ps:
        res = segment_input(p, allow_invalid)
        if res is None:
            return None
        tokens += res
    # print(tokens)
    return tokens

# Dynamic programming - minimize the number of segmented tokens, where each token
# is either a valid prefix or a valid full pinyin.
def segment_input(pinyin_input, allow_invalid=True):
    n = len(pinyin_input)
    f = [float("inf") for i in range(n + 1)]
    prev = [None for i in range(n + 1)]
    f[0] = 0
    # #tokens for [0, i)
    for i in range(n + 1):
        for j in range(0, i):
            token = pinyin_input[j:i]
            if token in valid_pinyins or token in valid_prefixes or \
                    (allow_invalid and token in invalid_single_char):
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


if __name__ == "__main__":
    # tests
    assert segment_with_hint("aaa") == ["a", "a", "a"]
    assert segment_with_hint("nihaoa") == ["ni", "hao", "a"]
    assert segment_with_hint("weidlingxmzx") == ["wei", "d", "ling", "x", "m", "z", "x"]
    assert segment_with_hint("renmingongheguo") == ["ren", "min", "gong", "he", "guo"]
    assert segment_with_hint("shanxixi'an") == ["shan", "xi", "xi", "an"]
    assert segment_with_hint("'xx'''x''") == ["x", "x", "x"]
    assert segment_with_hint("u") == ["u"]
    assert segment_with_hint("u", allow_invalid=False) == []
    