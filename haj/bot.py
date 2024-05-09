import os

import discord
import discord.ext.commands
import gspread

import haj


class Bot:
    def __init__(self, database_file: str = "haj.json"):
        self.database_file = database_file
        self.database = haj.Database(database_file)

        self.enable_tba = False
        self.enable_sheets = False
        self.spreadsheet_accesser = None
        self.sheets = {}

        intents = discord.Intents.default()
        intents.message_content = True

        self.bot = discord.ext.commands.Bot(
            # command_prefix=database.data["config"]["command_prefix"],
            command_prefix='&',
            intents=intents
        )

        self.on_ready = self.bot.event(self.on_ready)
        # self.on_guild_join = self.client.event(self.on_guild_join)
        # self.on_message = self.bot.event(self.on_message)

        if self.database.data["config"]["tokens"]["tba"]:
            self.enable_tba = True
        else:
            print(f"Error: No TBA token provided ({self.database_file})\n    TBA command will be unavailable")
        if (self.database.data["config"]["tokens"]["google"] and
                os.path.exists(self.database.data["config"]["tokens"]["google"])):
            self.enable_sheets = True
            self.spreadsheet_accesser = gspread.service_account(self.database.data["config"]["tokens"]["google"])
            for guild in self.database.data["guilds"].keys():
                self.sheets[guild] = self.spreadsheet_accesser.open_by_key(
                    self.database.data["guilds"][guild]["spreadsheet_id"]
                ).worksheet(self.database.data["guilds"][guild]["sheet_name"])
        else:
            print(f"Error: No Google config file provided or file does not exist ({self.database_file})\n"
                  f"    Google Sheet commands will be unavailable")

    async def on_ready(self):
        print(f"Bot logged in as {self.bot.user}")
        await self.bot.add_cog(haj.commands.Admin(self))
        await self.bot.add_cog(haj.commands.Misc(self))
        await self.bot.add_cog(haj.commands.Mod(self))
        print(f"Bot ready with command prefix {self.bot.command_prefix}")
        print("Available commands:\n" + '\n'.join([command.name for command in self.bot.commands]))

    async def on_message(self, message: discord.Message):
        await self.bot.process_commands(message)

    """
    async def on_guild_join(self, guild: discord.Guild):
        haj.utils.update_guild_ids(self.database, self.client)
    
    async def on_message(self, message: discord.Message):
        if message.author != self.client.user:
            haj.utils.update_guild_ids(self, message.channel)
            if message.content[0] == haj.utils.get_command_prefix(self, message.channel):
                args = shlex.split(message.content[1:])
                args[0] = args[0].lower()
                if (haj.utils.is_admin(self, message.author) and
                        isinstance(message.channel, discord.DMChannel) and args[0] in haj.commands.admin_commands):
                    await haj.commands.get(haj.commands.admin_commands[args[0]])(message, self, args)
                elif (await haj.utils.is_mod(self, message.author, message.guild) and
                        args[0] in haj.commands.mod_commands and
                        (not self.database.data["guilds"][message.guild.id]["mod_channel_id"] or
                         (self.database.data["guilds"][message.guild.id]["mod_channel_id"] and
                          message.channel.id == self.database.data["guilds"][message.guild.id]["mod_channel_id"]))):
                    await haj.commands.get(haj.commands.mod_commands[args[0]])(message, self, args)
                elif args[0] in haj.commands.commands:
                    await haj.commands.get(haj.commands.commands[args[0]])(message, self, args)
                elif args[0] in haj.commands.hidden_commands:
                    await haj.commands.get(haj.commands.hidden_commands[args[0]])(message, self, args)
                else:
                    await message.reply(embed=haj.utils.error(f"Command \"{args[0]}\" does not exist"))
    """

    def start(self):
        if self.database.data["config"]["tokens"]["discord"]:
            self.bot.run(self.database.data["config"]["tokens"]["discord"])
        else:
            print(f"Error: No Discord token provided ({self.database_file})")
