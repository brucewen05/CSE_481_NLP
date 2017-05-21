import sqlite3

connection = sqlite3.connect('/data/lcmc.db3')
cursor = connection.cursor()

def get_char_paragraphs():
    return cursor.execute('''
        SELECT "^|" || group_concat(w.characters, "|") FROM words w
        GROUP BY file_id, paragraph_num
    ''')

def get_pinyin_paragraphs():
    return cursor.execute('''
        SELECT "^|" || group_concat(w.characters, "|") FROM pinyin_words w
        GROUP BY file_id, paragraph_num
    ''')    

def get_all_chars():
    return cursor.execute('''
        SELECT DISTINCT character FROM characters WHERE is_cjk="Y" and character != "·" ORDER BY character
    ''')
