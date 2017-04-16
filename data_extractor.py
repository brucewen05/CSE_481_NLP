import re
import json
import lcmc_queries as lcmc

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

    
def extract_triples(paragraph_pairs, context_window=10, max_input_window=5, first_n=None, min_paragraph_len=6):
    # triples[i] = (context, pinyins, chars)
    triples = []
    for pp in paragraph_pairs:
        if len(pp[0]) != len(pp[1]):
            # weird encoding error in the dataset, skip
            continue
        if len(pp[0]) < min_paragraph_len:
            continue

        # TODO: Consider only putting cursor and input window on word boundaries
        for cursor in range(1, len(pp[0])):
            for input_window_end in range(cursor + 1, min(cursor + max_input_window + 1, len(pp[0]))):
                if len([i for i in range(cursor, input_window_end) if re.match(r'[^a-z]', pp[1][i])]) > 0:
                    break
                context = pp[0][max(0, cursor - context_window):cursor]
                pinyins = pp[1][cursor:input_window_end]
                chars = pp[0][cursor:input_window_end]

                if (len(chars) > 0):
                    triples.append((" ".join(context), " ".join(pinyins), " ".join(chars)))
                    if first_n is not None and len(triples) == first_n:
                        return triples
    return triples


if __name__ == "__main__":    
    with open('data/data_lcmc_clean.json', 'w') as outfile:
        data = json.dumps(extract_triples(build_parallel_paragraphs_lcmc()), indent=4, sort_keys=True)
        outfile.write(data)
    