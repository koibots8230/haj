import typing

import discord.ext.commands

import haj


class Mod(discord.ext.commands.Cog):
    def __init__(self, bot: haj.Bot):
        self.bot = bot

        @discord.ext.commands.check(self.is_mod)
        async def config(context: discord.ext.commands.Context):
            await self.config(self, context)
        self.config = config

    async def is_mod(self, context: discord.ext.commands.Context):
        if (context.author.id in self.bot.database.data["guilds"][context.guild.id]["mod_user_ids"] or
                (await context.guild.fetch_member(context.author.id)).guild_permissions.administrator):
            return True
        for role_id in self.bot.database.data["guilds"][context.guild.id]["mod_role_ids"]:
            if context.author in context.guild.get_role(role_id).members:
                return True

    @config.command(name="help")
    async def help_(context: discord.ext.commands.Context):
        await context.send(embed=discord.Embed(
            title="Available Subcommands",
            description="`add <list> <item>`\n`del <list> <item>`\n`help`\n`list [list]`\n`set <item> <value>`\n"
                        "`unset <item>`\n"
        ))
    self.help = help_

    @discord.ext.commands.guild_only()
    @discord.ext.commands.group(invoke_without_command=True)
    async def config(self, context: discord.ext.commands.Context):
        if context.invoked_subcommand is None:
            await self.help(context)

    @config.command(name="list")
    async def list_(
            context: discord.ext.commands.Context,
            list__: typing.Optional[typing.Literal["mod_role_ids", "mod_user_ids"]]
    ):
        if list__ is None:
            await context.send(embed=discord.Embed(description="".join([
                f"`{key}: {str(value)}`\n" if not isinstance(value, list) else f"`{key}: [...]`\n" if value else
                f"`{key}: []`\n" for key, value in self.bot.database.data["guilds"][context.guild.id].items()
            ])))
        else:
            await context.send(embed=discord.Embed(description="".join([
                f"`{item}`\n" for item in self.bot.database.data["guilds"][context.guild.id][list__]
            ])))
    self.list = list_

    @config.command(name="add")
    async def add(
            context: discord.ext.commands.Context,
            list__: typing.Literal["mod_role_ids", "mod_user_ids"],
            item: int
    ):
        if item not in self.bot.database.data["guilds"][context.guild.id][list__]:
            self.bot.database.data["guilds"][context.guild.id][list__].append(item)
            await context.send(embed=discord.Embed(description="Config updated successfully"))
        else:
            raise ValueError(f"Item `{item}` already exists in list `{list__}")
    self.add = add

    @config.command(name="del")
    async def del_(
            context: discord.ext.commands.Context,
            list__: typing.Literal["mod_role_ids", "mod_user_ids"],
            item: int
    ):
        if item in self.bot.database.data["guilds"][context.guild.id][list__]:
            self.bot.database.data["guilds"][context.guild.id][list__].remove(item)
            await context.send(embed=discord.Embed(description="Config updated successfully"))
        else:
            raise ValueError(f"Item `{item}` does not exists in list `{list__}")
    self.del_ = del_

    @typing.overload
    @config.command(name="set")
    async def set_(
            context: discord.ext.commands.Context,
            item: typing.Literal[
                "command_prefix",
                "sheet_name",
                "spreadsheet_id"
            ],
            value: str
    ):
        self.bot.database.data["guilds"][context.guild.id][item] = value
        await context.send(embed=discord.Embed(description="Config updated successfully"))
    self.set = set_

    @typing.overload
    @config.command(name="unset")
    async def unset(
            context: discord.ext.commands.Context,
            item: typing.Literal[
                "mod_channel_id",
                "task_channel_id"
            ]
    ):
        self.bot.database.data["guilds"][context.guild.id][item] = None
        await context.send(embed=discord.Embed(description="Config updated successfully"))
    self.unset = unset
