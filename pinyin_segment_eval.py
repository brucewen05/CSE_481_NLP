import lcmc_queries as lcmc
import pinyin_util
import re
import json
from random import shuffle


def load_data2(filename):
    try:
        with open(filename, encoding='utf8') as f:
            data = json.load(f)
            return data
    except IOError:
        pass

data = load_data2("data\sms_clean.data")[0]
shuffle(data)
with open("data/train_sms_clean.sample", 'w', encoding="utf-8") as trainoutfile:
    train = json.dumps(list(data), indent=4, sort_keys=True)
    trainoutfile.write(train)
# with open("data/test_lcmc_clean.sample", 'w') as testoutfile:
#     test = json.dumps(list(data[split_pos + 1:]), indent=4, sort_keys=True)
#     testoutfile.write(test)

# correct = total = 0
# for tup in lcmc.get_pinyin_paragraphs():
#     total += 1
#     # drop tunes and add paddings
#     p = re.sub(r'([a-z]+)[0-9] *', r' \1 ', tup[0])
#     p = re.sub(r'([^a-z ])', '', p)
#     # fix "uu"=>"v" in lcmc pinyin
#     p = re.sub(r'uu', r'v', p)
#     expected = p.split()
#     segmented = pinyin_util.segment_with_hint(''.join(p.split()))
#     if expected == segmented:
#         correct += 1
#     else:
#         pass
#
# print(correct / float(total))


