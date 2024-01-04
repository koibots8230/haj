import urllib.request
import json

import tokens


async def command_tba(message, args):
    """
    Gets information on a team from The Blue Alliance
    """
    request = urllib.request.Request(f"https://www.thebluealliance.com/api/v3/team/frc{args[0]}")
    request.add_header("X-TBA-Auth-Key", tokens.tba)
    request.add_header("User-Agent", "FRC/8230 Haj")
    response = urllib.request.urlopen(request)

    data = json.loads(response.read())

    await message.channel.send(
        f"{data['nickname']} (#{data['team_number']})\n"
        f"\n"
        f"{data['city']}, {data['state_prov']}, {data['country']}\n"
        f"{data['name']}\n"
        f"\n"
        f"{data['rookie_year']}"
    )


async def command_ping(message, args):
    """
    Pong!
    """
    await message.channel.send("Pong")


commands = dir()
for item in range(len(commands) - 1, -1, -1):
    if commands[item][0:8] != "command_":
        commands.pop(item)
    else:
        commands[item] = commands[item][8:]


async def command_help(message, args):
    """
    Lists the functions that Haj has available
    """
    await message.channel.send("Available commands: ".join([f"{str(command)}, " for command in commands])[:-2])
