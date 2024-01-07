import inspect
import urllib.request
import urllib.error
import json
import datetime

import discord

import database
import config
import templates
import tokens


async def command_tba(message: discord.Message, args: list[str]):
    """
    Gets information on a team from The Blue Alliance
    Usage: `tba <frc_team_number>`
    """

    if len(args) == 2:
        try:
            request = urllib.request.Request(f"https://www.thebluealliance.com/api/v3/team/frc{str(int(args[1]))}")
            request.add_header("X-TBA-Auth-Key", tokens.tba)
            request.add_header("User-Agent", "FRC/8230 Haj")
            data = json.loads(urllib.request.urlopen(urllib.request.Request(
                f"https://www.thebluealliance.com/api/v3/team/frc{str(int(args[1]))}",
                headers={"x-tba-auth-key": tokens.tba, "user-agent": "FRC/8230"}
            )).read())

            request = urllib.request.Request(
                f"https://www.thebluealliance.com/api/v3/team/frc{str(int(args[1]))}/districts")
            request.add_header("X-TBA-Auth-Key", tokens.tba)
            request.add_header("User-Agent", "FRC/8230 Haj")
            response = urllib.request.urlopen(request)
            districts = json.loads(response.read())
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
            await message.reply(embed=templates.error(
                f"FRC team {args[0]} does not exist or is not in the TBA database"))
    elif len(args) == 1:
        await message.reply(embed=templates.error("Missing argument \"frc_team_number\""))
    else:
        await message.reply(embed=templates.error("Too many arguments for command \"tba\""))


async def command_ping(message: discord.Message, args: list[str]):
    """
    Pong!
    Usage: `ping`
    """

    if len(args) == 1:
        await message.channel.send(
            f"Pong ({int((datetime.datetime.now(datetime.timezone.utc) - message.created_at).total_seconds() * 1000)} "
            f"ms)")
    else:
        await message.reply(embed=templates.error("Too many arguments for command \"ping\""))


async def command_me(message: discord.Message, args: list[str]):
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
            embed.add_field(name="Is Haj Admin", value=database.is_admin(message.author.id))
            embed.set_thumbnail(url=message.author.display_avatar.url)

            await message.channel.send(embed=embed)
        else:
            await message.reply(embed=templates.error(f"Command \"me\" can only be run in DMs"))
    else:
        await message.reply(embed=templates.error("Too many arguments for command \"me\""))


commands = dir()
for item in range(len(commands) - 1, -1, -1):
    if commands[item][0:8] != "command_":
        commands.pop(item)
    else:
        commands[item] = commands[item][8:]
commands.append("help")
commands.sort()


async def command_help(message: discord.Message, args: list[str]):
    """
    Lists the functions that Haj has available
    Usage: `help [command]`
    """

    if len(args) == 1:
        embed = discord.Embed(
            title="Available Commands",
            description="".join([f"`{str(command)}`\n" for command in commands])[:-1]
        )
    elif len(args) == 2:
        if args[1] in commands:
            embed = discord.Embed(
                title=args[1].capitalize(),
                description=inspect.getdoc(globals()["command_" + args[1]])
            )
        else:
            embed = templates.error(f"Command \"{args[1]}\" does not exist")
    else:
        embed = templates.error(f"Too many arguments for command \"help\"")

    await message.channel.send(embed=embed)


async def admin_command_update_guilds(message: discord.Message, client: discord.Client, args: list[str]):
    database.update_guild_ids(client)
    await message.channel.send(embed=templates.info("Done updating guild IDs"))


async def admin_command_test_admin(message: discord.Message, client: discord.Client, args: list[str]):
    await message.channel.send(":shark:")


admin_commands = dir()
for item in range(len(admin_commands) - 1, -1, -1):
    if admin_commands[item][0:14] != "admin_command_":
        admin_commands.pop(item)
    else:
        admin_commands[item] = admin_commands[item][14:]
admin_commands.sort()
