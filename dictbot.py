from collections import defaultdict
import os
import re
import discord

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
    print('\nDone parsing')

def parse_defs(defs_str):
    fields = defs_str.split('/')
    defs = []
    cur_def = []
    for field in fields:
        if field == '' or field == '(P)':
            continue
        elif re.search('^(\([^\) ]+\) )*\([0-9]+\) ', field):
            if cur_def:
                defs.append('; '.join(cur_def))
            field = re.sub('\([0-9]+\) ', '', field)
            cur_def = [field]
        else:
            cur_def.append(field)
    if cur_def:
        defs.append('; '.join(cur_def))
    return defs

def format_entry(entry):
    (reading, word, defs, is_common) = entry
    response = reading
    if word:
        response += f' 【{word}】'
    if is_common:
        response += ' *common word*'
    response += '\n'
    meanings = parse_defs(defs)
    for index, meaning in enumerate(meanings, start=1):
        response += f'  {index}. {meaning}\n'
    return response

def do_query(query):
    if query not in words:
        response = f'No definition found for {query}'
    else:
        entries = words[query]
        first = True
        response = ''
        for entry in entries:
            if not first:
                response += '\n'
            response += format_entry(entry)
            first = False
    return response

# print(do_query('水'))
# quit()

token = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    content = message.content
    if content.startswith('!def '):
        r = do_query(content[5:])
        await message.channel.send(r)

client.run(token)
