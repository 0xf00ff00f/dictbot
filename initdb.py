from collections import defaultdict
import os
import re
import sqlite3

words = defaultdict(list)
with open('edict.utf') as f:
    print('Parsing dictionary', flush=True, end='')
    entry_re = re.compile('^([^ ]+) \[([^\]]+)\] /(.*)/$')
    entry_no_kanji_re = re.compile('^([^ ]+) /(.*)/$')
    line_no = 0
    for line in f:
        m = entry_re.search(line)
        if m is not None:
            kanji = m.group(1)
            reading = m.group(2)
            defs = m.group(3)
            is_common = line.find('/(P)/') != -1
            entry = (reading, kanji, defs, is_common)
            words[kanji].append(entry)
            words[reading].append(entry)
        else:
            m = entry_no_kanji_re.search(line)
            if m is not None:
                reading = m.group(1)
                defs = m.group(2)
                is_common = line.find('/(P)/') != -1
                entry = (reading, '', defs, is_common)
                words[reading].append(entry)
        line_no += 1
        if (line_no % 1000) == 0:
            print('.', flush=True, end='')
    print(f'\nDone parsing line_no={line_no}\n')

print('Creating database...\n')

SCHEMA = '''
CREATE TABLE keys (
    id INTEGER PRIMARY KEY,
    key TEXT);

CREATE TABLE definitions (
    key_id INTEGER,
    reading TEXT,
    kanji TEXT,
    defs TEXT,
    is_common BOOLEAN);
'''

con = sqlite3.connect('dict.db')
with con:
    con.executescript(SCHEMA)
    for key, values in words.items():
        cursor = con.execute('INSERT INTO keys (key) VALUES(?)', (key,))
        cursor.execute('select last_insert_rowid()')
        key_id = cursor.fetchone()[0]
        data = [{'key_id': key_id,
                 'reading': value[0],
                 'kanji': value[1],
                 'defs': value[2],
                 'is_common': value[3]} for value in values]
        con.executemany('''INSERT INTO definitions
                           (key_id, reading, kanji, defs, is_common)
                           VALUES (:key_id, :reading, :kanji, :defs, :is_common)''',
                        data)
con.close()
