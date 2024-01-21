import shlex

import discord

import haj


class Bot:
    def __init__(self, database_file: str = "haj.json"):
        self.database_file = database_file
        self.database = haj.database.Database(database_file)

        self.enable_tba = False

        intents = discord.Intents.default()
        intents.message_content = True

        self.client = discord.Client(intents=intents)
        self.client.bot = self

        self.on_ready = self.client.event(self.on_ready)
        self.on_guild_join = self.client.event(self.on_guild_join)
        self.on_message = self.client.event(self.on_message)

    async def on_ready(self):
        print(f"Bot logged in as {self.client.user}")

    async def on_guild_join(self, guild: discord.Guild):
        haj.utils.update_guild_ids(self, self.database)

    async def on_message(self, message: discord.Message):
        if message.author != self.client.user:
            haj.utils.update_guild_ids(self, message.channel)
            if message.content[0] == haj.utils.get_command_prefix(self, message.channel):
                args = shlex.split(message.content[1:])
                args[0] = args[0].lower()
                if (haj.utils.is_admin(self, message.author.id) and
                        isinstance(message.channel, discord.DMChannel) and args[0] in haj.commands.admin_commands):
                    await haj.commands.get(haj.commands.admin_commands[args[0]])(message, self, args)
                elif (haj.utils.is_mod(self, message.author.id, message.guild) and
                        args[0] in haj.commands.mod_commands and
                        (self.database.data["guilds"][message.guild.id]["enforce_mod_channel"] and
                         message.channel.id == self.database.data["guilds"][message.guild.id]["mod_channel_id"])):
                    await haj.commands.get(haj.commands.mod_commands[args[0]])(message, self, args)
                elif args[0] in haj.commands.commands:
                    await haj.commands.get(haj.commands.commands[args[0]])(message, self, args)
                else:
                    await message.reply(embed=haj.utils.error(f"Command \"{args[0]}\" does not exist"))

    def start(self):
        if self.database.data["config"]["tokens"]["discord"]:
            if self.database.data["config"]["tokens"]["tba"]:
                self.enable_tba = True
            else:
                print(f"Error: No TBA token provided ({self.database_file})\n    TBA command will be unavailable")
            self.client.run(self.database.data["config"]["tokens"]["discord"])
        else:
            print(f"Error: No Discord token provided ({self.database_file})")
