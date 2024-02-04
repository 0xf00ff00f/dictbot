import os
import discord
import edict

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
        r = edict.query(content[5:])
        await message.channel.send(r)

client.run(token)
