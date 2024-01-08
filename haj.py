import discord
import shlex

import database
import templates
from commands import commands, mod_commands, admin_commands
import tokens

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)


@client.event
async def on_ready():
    print(f"Bot logged in as {client.user}")


@client.event
async def on_guild_join(guild: discord.Guild):
    database.update_guild_ids(client)


@client.event
async def on_message(message: discord.Message):
    if message.author != client.user:
        if (not isinstance(message.channel, discord.DMChannel) and
                str(message.guild.id) not in database.database.data["guilds"]):
            database.update_guild_ids(client)
        if (not isinstance(message.channel, discord.DMChannel) and
                database.database.data["guilds"][str(message.guild.id)]["command_prefix"]):
            command_prefix = database.database.data["guilds"][str(message.guild.id)]["command_prefix"]
        else:
            command_prefix = database.database.data["config"]["command_prefix"]
        if message.content[0] == command_prefix:
            args = shlex.split(message.content[1:])
            args[0] = args[0].lower()
            if (database.is_admin(message.author.id) and
                    isinstance(message.channel, discord.DMChannel) and args[0] in admin_commands):
                await getattr(__import__("commands"), admin_commands[args[0]])(message, client, args)
            elif args[0] in commands:
                await getattr(__import__("commands"), commands[args[0]])(message, client, args)
            else:
                await message.reply(embed=templates.error(f"Command \"{args[0]}\" does not exist"))


client.run(tokens.discord)
