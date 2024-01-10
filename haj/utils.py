import discord

import haj


def update_guild_ids(
        client: discord.Client,
        channel: discord.TextChannel or discord.StageChannel or discord.VoiceChannel or discord.Thread or
                 discord.DMChannel or discord.GroupChannel or discord.PartialMessageable or None
) -> None:
    if channel and not isinstance(channel, discord.DMChannel):
        if str(channel.guild.id) not in client.bot.database.data["guilds"]:
            client.bot.database.data["guilds"][str(channel.guild.id)] = client.bot.database.guild_structure.copy()
        client.bot.database.save()
    else:
        for guild in client.guilds:
            if str(guild.id) not in client.bot.database.data["guilds"]:
                client.bot.database.data["guilds"][str(guild.id)] = client.bot.database.guild_structure.copy()
            client.bot.database.save()


def get_command_prefix(
        client: discord.Client,
        channel: discord.TextChannel or discord.StageChannel or discord.VoiceChannel or discord.Thread or
                 discord.DMChannel or discord.GroupChannel or discord.PartialMessageable
) -> str:
    if (not isinstance(channel, discord.DMChannel) and
            client.bot.database.data["guilds"][str(channel.guild.id)]["command_prefix"]):
        return client.bot.database.data["guilds"][str(channel.guild.id)]["command_prefix"]
    else:
        return client.bot.database.data["config"]["command_prefix"]


def is_admin(database: haj.database.Database, user_id: int) -> bool:
    if str(user_id) in database.data["admins"]:
        return True
    return False


def error(description=None) -> discord.Embed:
    if description is not None:
        embed = discord.Embed(
            description=f"Error: {description}",
            color=0xdc4e49
        )
    else:
        embed = discord.Embed(
            description=f"Error",
            color=0xdc4e49
        )

    return embed
