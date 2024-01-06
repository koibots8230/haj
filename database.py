import sqlite3

import discord

connection = sqlite3.connect("haj.db")
cursor = connection.cursor()


def update_guild_ids(client: discord.Client) -> None:
    for guild in client.guilds:
        if cursor.execute(f"select * from guild where guild_id='{guild.id}'").fetchall() is None:
            cursor.execute(f"insert into guild values ({guild.id}, null)")
            connection.commit()


def is_admin(id: int) -> bool:
    if cursor.execute(f"select * from admins where user_id='{id}'") is not None:
        return True
    return False
