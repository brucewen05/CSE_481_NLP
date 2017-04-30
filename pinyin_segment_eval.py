import lcmc_queries as lcmc
import pinyin_util
import re

correct = total = 0
for tup in lcmc.get_pinyin_paragraphs():
    total += 1
    # drop tunes and add paddings
    p = re.sub(r'([a-z]+)[0-9] *', r' \1 ', tup[0])
    p = re.sub(r'([^a-z ])', '', p)
    # fix "uu"=>"v" in lcmc pinyin
    p = re.sub(r'uu', r'v', p)
    expected = p.split()
    segmented = pinyin_util.segment_with_hint(''.join(p.split()))
    if expected == segmented:
        correct += 1
    else:
        pass

print(correct / float(total))


