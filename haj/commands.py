import datetime
import inspect
import json
import urllib.error
import urllib.request

import discord

import haj


async def command_tba(message: discord.Message, client: discord.Client, args: list[str]):
    """
    Gets information on a team from The Blue Alliance
    Usage: `tba <frc_team_number>`
    """

    if client.bot.enable_tba:
        if len(args) == 2:
            try:
                data = json.loads(urllib.request.urlopen(urllib.request.Request(
                    f"https://www.thebluealliance.com/api/v3/team/frc{str(int(args[1]))}",
                    headers={
                        "x-tba-auth-key": client.bot.database.data["config"]["tokens"]["tba"],
                        "user-agent": "FRC/8230"
                    }
                )).read())
                districts = json.loads(urllib.request.urlopen(urllib.request.Request(
                    f"https://www.thebluealliance.com/api/v3/team/frc{str(int(args[1]))}/districts",
                    headers={
                        "x-tba-auth-key": client.bot.database.data["config"]["tokens"]["tba"],
                        "user-agent": "FRC/8230"
                    }
                )).read())

                if districts:
                    data["districts"] = districts[0]
                else:
                    data["districts"] = {}
                del districts

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
            except urllib.error.HTTPError:
                await message.reply(embed=haj.utils.error(
                    f"FRC team {args[0]} does not exist or is not in the TBA database"))
            except ValueError:
                await message.reply(embed=haj.utils.error(f"Please enter a valid number"))
        elif len(args) == 1:
            await message.reply(embed=haj.utils.error("Missing argument \"frc_team_number\""))
        else:
            await message.reply(embed=haj.utils.error("Too many arguments for command \"tba\""))
    else:
        await message.channel.send(
            embed=haj.utils.error("Command `tba` is unavailable right now, please contact a bot admin"))


async def command_ping(message: discord.Message, client: discord.Client, args: list[str]):
    """
    Pong!
    Usage: `ping`
    """

    if len(args) == 1:
        await message.channel.send(
            f"Pong ({int((datetime.datetime.now(datetime.timezone.utc) - message.created_at).total_seconds() * 1000)} "
            f"ms)")
    else:
        await message.reply(embed=haj.utils.error("Too many arguments for command \"ping\""))


async def command_me(message: discord.Message, client: discord.Client, args: list[str]):
    """
    Returns info about the sender of the message
    Usage: `me`
    """

    if len(args) == 1:
        if isinstance(message.channel, discord.DMChannel):
            embed = discord.Embed(title="User Info")

            embed.add_field(name="Username", value=message.author.name)
            embed.add_field(name="Display Name", value=message.author.display_name)
            embed.add_field(name="User ID", value=message.author.id)
            embed.add_field(name="Is Haj Admin", value=haj.utils.is_admin(client.bot.database, message.author.id))
            embed.set_thumbnail(url=message.author.display_avatar.url)

            await message.channel.send(embed=embed)
        else:
            await message.reply(embed=haj.utils.error(f"Command \"me\" can only be run in DMs"))
    else:
        await message.reply(embed=haj.utils.error("Too many arguments for command \"me\""))


async def admin_command_update_guilds(message: discord.Message, client: discord.Client, args: list[str]):
    haj.utils.update_guild_ids(client.bot.database, client)
    await message.channel.send(embed=discord.Embed(description="Done updating guild IDs"))


async def admin_command_help(message: discord.Message, client: discord.Client, args: list[str]):
    await base_help(message, args, admin_commands)


async def mod_command_help(message: discord.Message, client: discord.Client, args: list[str]):
    await base_help(message, args, mod_commands)


async def command_help(message: discord.Message, client: discord.Client, args: list[str]):
    await base_help(message, args, commands)


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
