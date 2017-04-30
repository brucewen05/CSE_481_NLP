import lcmc_queries

pinyin_sentences = lcmc_queries.get_pinyin_paragraphs()
for s in pinyin_sentences:
    print(s)