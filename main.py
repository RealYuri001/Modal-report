import discord
from discord.ext import commands
from keep_alive import keep_alive
import os

client = commands.Bot(command_prefix=commands.when_mentioned_or('>'), case_insensitive=True)

@client.event
async def on_ready():
    print('Logging in as {0.user}'.format(client))

for file in os.listdir('./commands'):
    if file.endswith('.py'):
        client.load_extension("commands."+ file[:-3])

keep_alive()
client.run("OTQzNzExNDI2Njk3MTM0MTMw.Yg3BwQ.aSWPb_o7pG27ktEZhNr7m6qQSH8")