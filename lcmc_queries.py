import sqlite3

connection = sqlite3.connect('data/lcmc.db3')
cursor = connection.cursor()

def get_char_paragraphs():
    return cursor.execute('''
        SELECT "^" || group_concat(characters, "") FROM full_sentences
        GROUP BY file_id, paragraph_num
    ''')

def get_pinyin_paragraphs():
    return cursor.execute('''
        SELECT "^" || group_concat(characters, "") FROM pinyin_full_sentences
        GROUP BY file_id, paragraph_num
    ''')    

def get_all_chars():
    return cursor.execute('''
        SELECT DISTINCT character FROM characters WHERE is_cjk="Y" and character != "·" ORDER BY character
    ''')

def get_all_pinyin_without_tones():
    return cursor.execute('''
        SELECT DISTINCT substr(character, 0, length(character)) FROM pinyin_characters
    ''')

def get_full_pinyin_candidates():
    return cursor.execute('''
        SELECT substr(pc.character, 0, length(pc.character)) as py , group_concat(DISTINCT c.character)
        FROM characters c JOIN pinyin_characters pc USING (file_id, sentence_id, word_num, char_num)
        WHERE c.is_cjk="Y" and py!=""
        GROUP BY py
    ''')
