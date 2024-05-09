import datetime

import discord.ext.commands

import haj


class Misc(discord.ext.commands.Cog):
    def __init__(self, bot: haj.Bot):
        self.bot = bot
        # self.bot.tree.add_command(self.ping)
        # self.bot.tree.add_command(self.ping)

        @discord.ext.commands.check(lambda _: self.bot.enable_tba)
        async def tba(self, context: discord.ext.commands.Context, team: int):
            self.tba(self, context, team)
        self.tba = tba

    @discord.ext.commands.command()
    async def ping(self, context: discord.ext.commands.Context):
        """
        Pong!
        Usage: `ping`
        """

        await context.send(
            f"Pong ("
            f"{int((datetime.datetime.now(datetime.timezone.utc) - context.message.created_at).total_seconds() * 1000)}"
            f" ms)"
        )

    @discord.ext.commands.command()
    async def me(self, context: discord.ext.commands.Context):
        """
        Returns info about the sender of the message
        Usage: `me`
        """

        embed = discord.Embed(title="User Info")
        embed.add_field(name="Username", value=context.author.name)
        embed.add_field(name="Display Name", value=context.author.display_name)
        embed.add_field(name="User ID", value=context.author.id)
        if isinstance(context.channel, discord.DMChannel):
            embed.add_field(name="Is Haj Admin", value=haj.utils.is_admin(self.bot, context.author))
        else:
            embed.add_field(name="Is Haj Mod", value=await haj.utils.is_mod(self.bot, context.author, context.guild))
        embed.set_thumbnail(url=context.author.display_avatar.url)
        await context.send(embed=embed)

    @discord.ext.commands.command()
    @discord.ext.commands.cooldown(1, 3, discord.ext.commands.BucketType.channel)
    async def tba(self, context: discord.ext.commands.Context, team: int):
        try:
            data = haj.api.tba(f"/team/frc{team}",
                               self.bot.database.data["config"]["tokens"]["tba"])
            districts = haj.api.tba(f"/team/frc{team}/districts",
                                    self.bot.database.data["config"]["tokens"]["tba"])
            if districts:
                data["districts"] = districts[0]
            else:
                data["districts"] = {}
            del districts
            embed = discord.Embed(
                title=f"FIRST® Robotics Competition Team {team}",
                url=f"https://www.thebluealliance.com/team/{team}",
                color=0x3f51b5
            )
            embed.set_thumbnail(url=f"https://frcavatars.herokuapp.com/get_image?team={team}")
            embed.add_field(name="Name", value=data["nickname"])
            embed.add_field(name="Rookie Year", value=data["rookie_year"])
            embed.add_field(name="Location",
                            value=f"{data['city']}, {data['state_prov']}, {data['postal_code']}, {data['country']}")
            if data["website"]:
                embed.add_field(name="Website", value=data["website"])
            if data["districts"] and data["districts"]["display_name"]:
                embed.add_field(name="District",
                                value=f"{data['districts']['display_name']} [{data['districts']['abbreviation']}]")
            await context.channel.send(embed=embed)
        except ValueError:
            await context.reply(embed=haj.utils.error(f"Please enter a valid number"))
