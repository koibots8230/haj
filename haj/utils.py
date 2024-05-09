import discord
import discord.ext.commands

import haj


def update_guild_ids(
        bot: haj.Bot,
        channel: discord.TextChannel or discord.StageChannel or discord.VoiceChannel or discord.Thread or
                 discord.DMChannel or discord.GroupChannel or discord.PartialMessageable or None = None
) -> None:
    if channel is not None and not isinstance(channel, discord.DMChannel):
        if channel.guild.id not in bot.database.data["guilds"]:
            bot.database.data["guilds"][channel.guild.id] = bot.database.guild_structure.copy()
        bot.database.save()
    else:
        for guild in bot.bot.guilds:
            if guild.id not in bot.database.data["guilds"]:
                bot.database.data["guilds"][guild.id] = bot.database.guild_structure.copy()
            bot.database.save()


# def get_command_prefix(
#         bot: haj.bot.Bot,
#         channel: discord.TextChannel or discord.StageChannel or discord.VoiceChannel or discord.Thread or
#                  discord.DMChannel or discord.GroupChannel or discord.PartialMessageable
# ) -> str:
#     if (not isinstance(channel, discord.DMChannel) and
#             bot.database.data["guilds"][channel.guild.id]["command_prefix"]):
#         return bot.database.data["guilds"][channel.guild.id]["command_prefix"]
#     else:
#         return bot.database.data["config"]["command_prefix"]


def is_admin(bot: haj.Bot, user: discord.User) -> bool:
    return user.id in bot.database.data["admins"]


async def is_mod(bot: haj.bot.Bot, user: discord.User, guild: discord.Guild) -> bool:
    if guild is None:
        return False
    if (user.id in bot.database.data["guilds"][guild.id]["mod_user_ids"] or
            (await guild.fetch_member(user.id)).guild_permissions.administrator):
        return True
    for role_id in bot.database.data["guilds"][guild.id]["mod_role_ids"]:
        if user in guild.get_role(role_id).members:
            return True
    return False


async def is_sheets_available(bot: haj.bot.Bot, message: discord.Message) -> bool:
    if (bot.database.data["guilds"][message.guild.id]["spreadsheet_id"] and
            bot.database.data["guilds"][message.guild.id]["sheet_name"] and
            bot.database.data["config"]["tokens"]["google"]):
        return True
    if not bot.database.data["config"]["tokens"]["google"]:
        await message.reply(embed=haj.utils.error(
            "Google Sheets API is unavailable right now, please contact a bot admin"))
        return False
    else:
        if not bot.database.data["guilds"][message.guild.id]["spreadsheet_id"]:
            await message.reply(embed=haj.utils.error("`Spreadsheet ID` is not set in config"))
        if not bot.database.data["guilds"][message.guild.id]["sheet_name"]:
            await message.reply(embed=haj.utils.error("`Sheet Name` is not set in config"))
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
