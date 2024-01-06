import discord
import shlex

import config
import database
import templates
from commands import commands, admin_commands
import tokens

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)


# guilds = {}


@client.event
async def on_ready():
    print(f"Bot logged in as {client.user}")


@client.event
async def on_guild_join(guild: discord.Guild):
    database.update_guild_ids(client)


@client.event
async def on_guild_join(guild: discord.Guild):
    database.update_guild_ids(client)


@client.event
async def on_message(message: discord.Message):
    if message.author != client.user:
        if message.content[0] == config.command_prefix:
            args = shlex.split(message.content[1:])
            args[0] = args[0].lower()
            if args[0] in commands:
                await getattr(__import__("commands"), "command_" + args[0])(message, args)
            elif (database.is_admin(message.author.id) and
                  isinstance(message.channel, discord.DMChannel) and args[0] in admin_commands):
                await getattr(__import__("commands"), "admin_command_" + args[0])(message, client, args)
            else:
                await message.reply(embed=templates.error(f"Command \"{args[0]}\" does not exist"))


client.run(tokens.discord)
