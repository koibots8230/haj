import discord

import haj


def update_guild_ids(
        bot: haj.bot.Bot,
        channel: discord.TextChannel or discord.StageChannel or discord.VoiceChannel or discord.Thread or
                 discord.DMChannel or discord.GroupChannel or discord.PartialMessageable or None = None
) -> None:
    if channel and not isinstance(channel, discord.DMChannel):
        if channel.guild.id not in bot.database.data["guilds"]:
            bot.database.data["guilds"][channel.guild.id] = bot.database.guild_structure.copy()
        bot.database.save()
    else:
        for guild in bot.client.guilds:
            if guild.id not in bot.database.data["guilds"]:
                bot.database.data["guilds"][guild.id] = bot.database.guild_structure.copy()
            bot.database.save()


def get_command_prefix(
        bot: haj.bot.Bot,
        channel: discord.TextChannel or discord.StageChannel or discord.VoiceChannel or discord.Thread or
                 discord.DMChannel or discord.GroupChannel or discord.PartialMessageable
) -> str:
    if (not isinstance(channel, discord.DMChannel) and
            bot.database.data["guilds"][channel.guild.id]["command_prefix"]):
        return bot.database.data["guilds"][channel.guild.id]["command_prefix"]
    else:
        return bot.database.data["config"]["command_prefix"]


def is_admin(bot: haj.bot.Bot, user_id: int) -> bool:
    if user_id in bot.database.data["admins"]:
        return True
    return False


def is_mod(bot: haj.bot.Bot, user_id: int, guild: discord.Guild) -> bool:
    if guild is None:
        return False
    if user_id in bot.database.data["guilds"][guild.id]["mod_user_ids"]:
        return True
    for role_id in bot.database.data["guilds"][guild.id]["mod_role_ids"]:
        if user_id in [user.id for user in guild.get_role(role_id).members]:
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
