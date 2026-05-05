import sqlite3
import re
import sys

def fetch_definitions(key):
    def entry_factory(cursor, row):
        return { 'reading': row[0], 'word': row[1], 'defs': row[2], 'is_common': bool(row[3]) }
    connection = sqlite3.connect('dict.db')
    connection.row_factory = entry_factory
    cursor = connection.cursor()
    cursor.execute('''SELECT definitions.reading,
                             definitions.kanji,
                             definitions.defs,
                             definitions.is_common
                      FROM keys, definitions
                      WHERE keys.id = definitions.key_id
                      AND keys.key = ?''',
                    (key,));
    entries = cursor.fetchall()
    cursor.close()
    connection.close()
    return entries

def parse_defs(defs_str):
    fields = defs_str.split('/')
    defs = []
    cur_def = []
    for field in fields:
        if field == '' or field == '(P)':
            continue
        elif re.search(r'^(\([^\) ]+\) )*\([0-9]+\) ', field):
            if cur_def:
                defs.append('; '.join(cur_def))
            field = re.sub(r'\([0-9]+\) ', '', field)
            cur_def = [field]
        else:
            cur_def.append(field)
    if cur_def:
        defs.append('; '.join(cur_def))
    return defs

def format_entry(entry):
    response = entry['reading']
    word = entry['word']
    if word:
        response += f' 【{word}】'
    if entry['is_common']:
        response += ' *common word*'
    response += '\n'
    meanings = parse_defs(entry['defs'])
    for index, meaning in enumerate(meanings, start=1):
        response += f'{index}. {meaning}\n'
    return response

def query(key):
    entries = fetch_definitions(key)
    if not entries:
        response = f'No definition found for {key}'
    else:
        first = True
        response = ''
        for entry in entries:
            if not first:
                response += '\n'
            response += format_entry(entry)
            first = False
    return response

def main(argv):
    args = sys.argv[1:]
    if len(argv) == 1:
        print('Usage: edict word')
    else:
        key = argv[1]
        print(query(key))

if __name__ == '__main__':
    main(sys.argv)
