import codecs

# extracts valid full pinyins
with codecs.open("data/valid_pinyins.txt", encoding='utf-8') as f:
    lines = f.readlines()
valid_pinyins = set([line.strip() for line in lines])

valid_prefixes = ["b", "p", "m", "f", "d", "t", "n", "l", "g", "k", "h", "j",
        "q", "x", "zh", "ch", "sh", "r", "z", "c", "s", "y", "w"]
invalid_single_char = ["i", "u", "v"]

# for typos: gnerate a typo lookup table:
#                                        probably by coding each key
#                                        with its coordinates, and classify
#                                        a key is likely to be a typo of another
#                                        if the distance is close ?? write to disk

typo_transpose_letter = {'a': [['q', 's', 'w', 'x', 'z'],
       [0.009771022502960917,
        0.6974766416633768,
        0.17852677983945256,
        0.06385708645874458,
        0.05036846953546519]],
 'b': [['f', 'g', 'h', 'n', 'v'],
       [0.21879116253174183,
        0.2876386795399302,
        0.14701049686995016,
        0.2631007183498323,
        0.08345894270854551]],
 'c': [['d', 'f', 's', 'v', 'x'],
       [0.23484616233583086,
        0.1854635976798656,
        0.4656701043569966,
        0.09128478055599838,
        0.02273535507130857]],
 'd': [['c', 'e', 'f', 'r', 's', 'v', 'w', 'x'],
       [0.07976359554679983,
        0.16451267612673212,
        0.06701874658991991,
        0.26682132638058786,
        0.3365847969778881,
        0.032686789089409696,
        0.044207132950432534,
        0.008404936338229965]],
 'e': [['d', 'f', 'r', 's', 'w'],
       [0.1779715238352708,
        0.07695773632513292,
        0.3447012706136794,
        0.3409254753536992,
        0.059443993872217715]],
 'f': [['b', 'c', 'd', 'e', 'g', 'r', 't', 'v'],
       [0.13069965524234436,
        0.12268505374163456,
        0.13052930440073007,
        0.13855201784627866,
        0.10824579192861489,
        0.15187183127154735,
        0.17018860271750152,
        0.04722774285134861]],
 'g': [['b', 'f', 'h', 'n', 'r', 't', 'v', 'y'],
       [0.16186764481124866,
        0.10197157267308574,
        0.07751795812318509,
        0.17892404095980438,
        0.16882164144887665,
        0.23151459575118447,
        0.03891945590707627,
        0.04046309032553874]],
 'h': [['b', 'g', 'j', 'm', 'n', 't', 'u', 'y'],
       [0.12470338885433226,
        0.11684751307392817,
        0.030674775957794827,
        0.13230584928698136,
        0.13660239131937246,
        0.2747943880019352,
        0.12051051673693183,
        0.06356117676872394]],
 'i': [['j', 'k', 'l', 'o', 'u'],
       [0.003524553380092072,
        0.050337076385492355,
        0.20665782586991926,
        0.4184436500052944,
        0.3210368943592019]],
 'j': [['h', 'i', 'k', 'm', 'n', 'u', 'y'],
       [0.23514348785871964,
        0.06172185430463576,
        0.11019867549668874,
        0.3058719646799117,
        0.17757174392935982,
        0.050154525386313466,
        0.05933774834437086]],
 'k': [['i', 'j', 'l', 'm', 'o', 'u'],
       [0.20712047967800162,
        0.02589265337455134,
        0.30396896201166,
        0.17626921720367641,
        0.173572065810494,
        0.11317662192161664]],
 'l': [['i', 'k', 'o', 'p'],
       [0.3165475960610156,
        0.11315698011199073,
        0.33761730063718864,
        0.232678123189805]],
 'm': [['h', 'j', 'k', 'n'],
       [0.24501375882591353,
        0.07389236118517886,
        0.18123253482369506,
        0.4998613451652126]],
 'n': [['b', 'g', 'h', 'j', 'm'],
       [0.24190930430005494,
        0.2923388103680767,
        0.14806722269390202,
        0.02510862508115667,
        0.29257603755680966]],
 'o': [['i', 'k', 'l', 'p'],
       [0.5419099113218143,
        0.05463046402591127,
        0.285448419072993,
        0.11801120557928144]],
 'p': [['l', 'o'], [0.6250466824349558, 0.3749533175650442]],
 'q': [['a', 's', 'w'],
       [0.17662801070472792, 0.6068986024382992, 0.21647338685697295]],
 'r': [['d', 'e', 'f', 'g', 't'],
       [0.27150976262020504,
        0.3242325737123386,
        0.07934698306004213,
        0.09362960953757347,
        0.23128107106984078]],
 's': [['a', 'c', 'd', 'e', 'q', 'w', 'x', 'z'],
       [0.15887307689425448,
        0.14228547020075988,
        0.3027996972490127,
        0.2835105625622925,
        0.0076474599641794625,
        0.06399361525145568,
        0.013537615311406369,
        0.027352502566638938]],
 't': [['f', 'g', 'h', 'r', 'y'],
       [0.14672457321891894,
        0.211876438047682,
        0.16683800851813776,
        0.38164474190322334,
        0.09291623831203799]],
 'u': [['h', 'i', 'j', 'k', 'y'],
       [0.12034001633366691,
        0.732357914351772,
        0.006533466763288359,
        0.06274658660869366,
        0.07802201594257911]],
 'v': [['b', 'c', 'd', 'f', 'g'],
       [0.1899669273328594,
        0.23008685438753748,
        0.24257410441071925,
        0.1799524000865453,
        0.15741971378233857]],
 'w': [['a', 'd', 'e', 'q', 's'],
       [0.20685383193245277,
        0.2022985876836869,
        0.25145329445175063,
        0.013875388339337108,
        0.3255188975927726]],
 'x': [['a', 'c', 'd', 's', 'z'],
       [0.32668518050997225,
        0.1560212067659682,
        0.169822435411933,
        0.3040477993772616,
        0.043423377934864935]],
 'y': [['g', 'h', 'j', 't', 'u'],
       [0.16780756797870316,
        0.1748748177727071,
        0.021296824491348166,
        0.42105596754769603,
        0.21496482220954555]],
 'z': [['a', 's', 'x'],
       [0.2814855671998529, 0.6710792425078139, 0.04743519029233315]]}

full_pinyin_candidates = {}
pinyin_prefix_candidates = {}

# constructs candidate map

with codecs.open("data/pinyin_char_dictionary.txt", encoding='utf-8') as f:
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
