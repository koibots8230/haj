import sqlite3

import discord


database_ro = sqlite3.connect("haj.db")


def update_guild_ids(client: discord.Client) -> None:
    database = sqlite3.connect("haj.db")
    for guild in client.guilds:
        if not database.execute("select * from guilds where guild_id = ?", (guild.id,)).fetchall():
            database.execute("insert into guilds (guild_id) values (?)", (guild.id,))
    database.commit()
    database.close()


def is_admin(user_id: int) -> bool:
    if database_ro.execute("select * from admins where user_id = ?", (user_id,)):
        return True
    return False
