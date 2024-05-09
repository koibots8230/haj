import discord.ext.commands

import haj


class Admin(discord.ext.commands.Cog):
    def __init__(self, bot: haj.Bot):
        self.bot = bot

        @discord.ext.commands.check(self.is_admin)
        def update_guilds(context: discord.ext.commands.Context):
            self.update_guilds(self, context)

        self.update_guilds = update_guilds

    async def is_admin(self, context: discord.ext.commands.Context):
        return context.author.id in self.bot.database.data["admins"]

    @discord.ext.commands.dm_only()
    @discord.ext.commands.command()
    async def update_guilds(self, context: discord.ext.commands.Context):
        haj.utils.update_guild_ids(self.bot)
        await context.send(embed=discord.Embed(description="Done updating guild IDs"))
