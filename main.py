import discord
import shlex

import tokens
# import commands
import config


intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)


@client.event
async def on_ready():
    print(f"Bot logged in as {client.user}")


@client.event
async def on_message(message):
    if message.author != client.user:
        if message.content[0] == config.command_prefix:
            args = shlex.split(message.content[1:])
            args[0] = args[0].lower()
            try:
                await getattr(__import__("commands"), "command_" + args[0])(message, args[1:])
            except AttributeError:
                await message.channel.send(f"{client.user.name}: Error: Command \"{args[0]}\" does not exist")


client.run(tokens.discord)


def split_command(command):
    if command[0] == config.command_prefix:
        return shlex.split(command[1:])
    else:
        return None
