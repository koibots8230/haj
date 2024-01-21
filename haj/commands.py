import datetime
import inspect

import discord

import haj


async def command_tba(message: discord.Message, bot: haj.bot.Bot, args: list[str]):
    """
    Gets information on a team from The Blue Alliance
    Usage: `tba <frc_team_number>`
    """

    if bot.enable_tba:
        if len(args) == 2:
            try:
                try:
                    data = haj.api.tba(f"/team/frc{str(int(args[1]))}",
                                       bot.database.data["config"]["tokens"]["tba"])
                    districts = haj.api.tba(f"/team/frc{str(int(args[1]))}/districts",
                                            bot.database.data["config"]["tokens"]["tba"])
                    if districts:
                        data["districts"] = districts[0]
                    else:
                        data["districts"] = {}
                    del districts
                except ValueError:
                    await message.reply(embed=haj.utils.error(
                        f"FRC team `{args[0]}` does not exist or is not in the TBA database"))
                    return
                embed = discord.Embed(
                    title=f"FIRST® Robotics Competition Team {args[1]}",
                    url=f"https://www.thebluealliance.com/team/{args[1]}",
                    color=0x3f51b5
                )
                embed.set_thumbnail(url=f"https://frcavatars.herokuapp.com/get_image?team={args[1]}")
                embed.add_field(name="Name", value=data["nickname"])
                embed.add_field(name="Rookie Year", value=data["rookie_year"])
                embed.add_field(name="Location",
                                value=f"{data['city']}, {data['state_prov']}, {data['postal_code']}, {data['country']}")
                if data["website"]:
                    embed.add_field(name="Website", value=data["website"])
                if data["districts"] and data["districts"]["display_name"]:
                    embed.add_field(name="District",
                                    value=f"{data['districts']['display_name']} [{data['districts']['abbreviation']}]")
                await message.channel.send(embed=embed)
            except ValueError:
                await message.reply(embed=haj.utils.error(f"Please enter a valid number"))
        elif len(args) == 1:
            await message.reply(embed=haj.utils.error("Missing argument `frc_team_number`"))
        else:
            await message.reply(embed=haj.utils.error("Too many arguments for command `tba`"))
    else:
        await message.channel.send(
            embed=haj.utils.error("Command `tba` is unavailable right now, please contact a bot admin"))


async def command_ping(message: discord.Message, bot: haj.bot.Bot, args: list[str]):
    """
    Pong!
    Usage: `ping`
    """

    if len(args) == 1:
        await message.channel.send(
            f"Pong ({int((datetime.datetime.now(datetime.timezone.utc) - message.created_at).total_seconds() * 1000)} "
            f"ms)")
    else:
        await message.reply(embed=haj.utils.error("Too many arguments for command `ping`"))


async def command_me(message: discord.Message, bot: haj.bot.Bot, args: list[str]):
    """
    Returns info about the sender of the message
    Usage: `me`
    """

    if len(args) == 1:
        embed = discord.Embed(title="User Info")
        embed.add_field(name="Username", value=message.author.name)
        embed.add_field(name="Display Name", value=message.author.display_name)
        embed.add_field(name="User ID", value=message.author.id)
        if isinstance(message.channel, discord.DMChannel):
            embed.add_field(name="Is Haj Admin", value=haj.utils.is_admin(bot, message.author))
        else:
            embed.add_field(name="Is Haj Mod", value=await haj.utils.is_mod(bot, message.author, message.guild))
        embed.set_thumbnail(url=message.author.display_avatar.url)
        await message.channel.send(embed=embed)
    else:
        await message.reply(embed=haj.utils.error("Too many arguments for command `me`"))


async def admin_command_update_guilds(message: discord.Message, bot: haj.bot.Bot, args: list[str]):
    haj.utils.update_guild_ids(bot)
    await message.channel.send(embed=discord.Embed(description="Done updating guild IDs"))


async def admin_command_help(message: discord.Message, bot: haj.bot.Bot, args: list[str]):
    await base_help(message, args, admin_commands)


async def mod_command_help(message: discord.Message, bot: haj.bot.Bot, args: list[str]):
    await base_help(message, args, mod_commands)


async def mod_command_config(message: discord.Message, bot: haj.bot.Bot, args: list[str or None]):
    if len(args) <= 1 or args[1].lower() == "help":
        await message.channel.send(embed=discord.Embed(
            title="Available Subcommands",
            description="`add <list> <item>`\n`del <list> <item>`\n`help`\n`list [list]`\n`set <item> <value>`\n"
                        "`unset <item>`\n"
        ))
    elif args[1].lower() == "list":
        if len(args) <= 2:
            await message.channel.send(embed=discord.Embed(description="".join([
                f"`{key}: {str(value)}`\n" if not isinstance(value, list) else f"`{key}: [...]`\n" if value else
                f"`{key}: []`\n" for key, value in bot.database.data["guilds"][message.guild.id].items()
            ])))
        elif len(args) == 3:
            if (args[2] in bot.database.data["guilds"][message.guild.id] and
                    isinstance(bot.database.data["guilds"][message.guild.id][args[2]], list)):
                await message.channel.send(embed=discord.Embed(description="".join([
                    f"`{item}`\n" for item in bot.database.data["guilds"][message.guild.id][args[2]]
                ])))
            else:
                await message.reply(embed=haj.utils.error(f"Unknown list \"{args[3]}\""))
                return
        else:
            await message.reply(embed=haj.utils.error("Too many arguments for subcommand `list`\n`list [list]`"))
            return
    elif args[1].lower() == "add":
        if len(args) <= 3:
            await message.reply(embed=haj.utils.error("Missing arguments\n`add <list> <item>`"))
            return
        elif len(args) == 4:
            if (args[2] in bot.database.data["guilds"][message.guild.id] and
                    isinstance(bot.database.data["guilds"][message.guild.id][args[2]], list)):
                if args[3] not in bot.database.data["guilds"][message.guild.id][args[2]]:
                    try:
                        bot.database.data["guilds"][message.guild.id][args[2]].append(int(args[3]))
                        bot.database.save()
                    except ValueError:
                        await message.reply(embed=haj.utils.error(f"Please enter a valid number"))
                        return
                    await message.channel.send(embed=discord.Embed(description="Config updated successfully"))
            else:
                await message.reply(embed=haj.utils.error(f"Unknown list `{args[2]}`"))
                return
        else:
            await message.reply(embed=haj.utils.error("Too many arguments for subcommand `add`\n`add <list> <item>`"))
            return
    elif args[1].lower() == "del":
        if len(args) <= 3:
            await message.reply(embed=haj.utils.error("Missing arguments\n`del <list> <item>`"))
            return
        elif len(args) == 4:
            if (args[2] in bot.database.data["guilds"][message.guild.id] and
                    isinstance(bot.database.data["guilds"][message.guild.id][args[2]], list)):
                if int(args[3]) in bot.database.data["guilds"][message.guild.id][args[2]]:
                    try:
                        bot.database.data["guilds"][message.guild.id][args[2]].remove(int(args[3]))
                        bot.database.save()
                    except ValueError:
                        await message.reply(embed=haj.utils.error(f"Please enter a valid number"))
                        return
                else:
                    await message.reply(
                        embed=haj.utils.error(f"Item `{args[3]}` does not exist in list `{args[2]}`"))
                    return
                await message.channel.send(embed=discord.Embed(description="Config updated successfully"))
            else:
                await message.reply(embed=haj.utils.error(f"Unknown list `{args[2]}`"))
                return
        else:
            await message.reply(embed=haj.utils.error("Too many arguments for subcommand `del`\n`del <list> <item>`"))
            return
    elif args[1].lower() == "set":
        if len(args) <= 3:
            await message.reply(embed=haj.utils.error("Missing arguments\n`set <item> <value>`"))
            return
        elif len(args) == 4:
            if (args[2] in bot.database.data["guilds"][message.guild.id] and
                    not isinstance(bot.database.data["guilds"][message.guild.id][args[2]], list)):
                if args[2] == "command_prefix":
                    if len(args[3]) != 1:
                        await message.reply(embed=haj.utils.error(f"`command_prefix` can only be 1 character"))
                        return
                    elif args[3][0] == ' ':
                        await message.reply(embed=haj.utils.error(f"`command_prefix` cannot be a space"))
                        return
                    else:
                        bot.database.data["guilds"][message.guild.id]["command_prefix"] = args[3][0]
                        bot.database.save()
                        await message.channel.send(embed=discord.Embed(description="Config updated successfully"))
                else:
                    try:
                        bot.database.data["guilds"][message.guild.id][args[2]] = int(args[3])
                        bot.database.save()
                    except ValueError:
                        await message.reply(embed=haj.utils.error(f"Please enter a valid number"))
                        return
            else:
                await message.reply(embed=haj.utils.error(f"Unknown item `{args[2]}`"))
                return
        else:
            await message.reply(embed=haj.utils.error("Too many arguments for subcommand `set`\n`set <item> <value>`"))
            return
    elif args[1].lower() == "unset":
        if len(args) <= 2:
            await message.reply(embed=haj.utils.error("Missing arguments\n`unset <item>`"))
            return
        elif len(args) == 3:
            if (args[2] in bot.database.data["guilds"][message.guild.id] and
                    not isinstance(bot.database.data["guilds"][message.guild.id][args[2]], list)):
                bot.database.data["guilds"][message.guild.id][args[2]] = None
                bot.database.save()
                await message.channel.send(embed=discord.Embed(description="Config updated successfully"))
            else:
                await message.reply(embed=haj.utils.error(f"Unknown item `{args[2]}`"))
                return
        else:
            await message.reply(embed=haj.utils.error("Too many arguments for subcommand `unset`\n`unset <item>`"))
            return
    else:
        await message.reply(embed=haj.utils.error("Unknown subcommand"))
        return


async def command_help(message: discord.Message, bot: haj.bot.Bot, args: list[str]):
    await base_help(message, args, commands)


async def hidden_command_gay(message: discord.Message, bot: haj.bot.Bot, args: list[str]):
    await message.add_reaction('🏳️‍🌈')


all_commands = dir()
commands = {}

for item in all_commands:
    if item[:8] == "command_":
        commands[item[8:]] = item
commands["help"] = "command_help"

mod_commands = commands.copy()
for item in all_commands:
    if item[:12] == "mod_command_":
        mod_commands[item[12:]] = item
mod_commands["help"] = "mod_command_help"

admin_commands = commands.copy()
for item in all_commands:
    if item[:14] == "admin_command_":
        admin_commands[item[14:]] = item
admin_commands["help"] = "admin_command_help"

hidden_commands = {}
for item in all_commands:
    if item[:15] == "hidden_command_":
        hidden_commands[item[15:]] = item
print(hidden_commands)


async def base_help(message: discord.Message, args: list[str], command_list: dict):
    """
    Lists the functions that Haj has available
    Usage: `help [command]`
    """

    if len(args) == 1:
        embed = discord.Embed(
            title="Available Commands",
            description="".join([f"`{str(command)}`\n" for command in command_list])[:-1]
        )
    elif len(args) == 2:
        if args[1] in command_list:
            embed = discord.Embed(
                title=args[1].capitalize(),
                description=inspect.getdoc(globals()[command_list[args[1]] + args[1]])
            )
        else:
            embed = haj.utils.error(f"Command \"{args[1]}\" does not exist")
    else:
        embed = haj.utils.error(f"Too many arguments for command \"help\"")
    await message.channel.send(embed=embed)


def get(command: str):
    return globals()[command]
