import datetime
import os

import discord
import discord.ext.commands
import gspread

import haj


intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
tree = discord.app_commands.CommandTree(client)

database_file = "haj.json"
database = haj.database.Database(database_file)
enable = {
    "tba": False,
    "sheets": False
}
spreadsheet_accesser = None
sheets = {}

if database.data["config"]["tokens"]["tba"]:
    enable_tba = True
else:
    print(f"Error: No TBA token provided ({database_file})\n    TBA command will be unavailable")
if (database.data["config"]["tokens"]["google"] and
        os.path.exists(database.data["config"]["tokens"]["google"])):
    enable_sheets = True
    spreadsheet_accesser = gspread.service_account(database.data["config"]["tokens"]["google"])
    for guild in database.data["guilds"].keys():
        sheets[guild] = spreadsheet_accesser.open_by_key(
            database.data["guilds"][guild]["spreadsheet_id"]
        ).worksheet(database.data["guilds"][guild]["sheet_name"])
else:
    print(f"Error: No Google config file provided or file does not exist ({database_file})\n"
          f"    Google Sheet commands will be unavailable")

bot = discord.ext.commands.Bot(
    # command_prefix=database.data["config"]["command_prefix"],
    command_prefix='&',
    intents=intents
)


def start():
    client.run(database.data["config"]["tokens"]["discord"])


@client.event
async def on_ready():
    print(f"Bot logged in as {client.user}")
    await tree.sync(guild=None)
    print("Bot ready")


@client.event
async def on_guild_join(guild: discord.Guild):
    haj.utils.update_guild_ids(database, client, guild)


@bot.command()
async def ping(context: discord.ext.commands.Context):
    print(context.prefix + "ping")
    await context.message.channel.send(
        f"Pong ("
        f"{int((datetime.datetime.now(datetime.timezone.utc) - context.message.created_at).total_seconds() * 1000)}"
        f" ms)")
