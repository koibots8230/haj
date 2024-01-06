import discord


colors = {
    "error": 0xdc4e49,
    "warning": 0xe6b44e
}


def error(description=None):
    if description is not None:
        embed = discord.Embed(
            description=f"Error: {description}",
            color=colors["error"]
        )
    else:
        embed = discord.Embed(
            description=f"Error",
            color=colors["error"]
        )

    return embed


def info(description, title=None, say_info=False):
    if say_info:
        return discord.Embed(
            title=title,
            description=f"Info: {description}"
        )
    else:
        return discord.Embed(
            title=title,
            description=description
        )
