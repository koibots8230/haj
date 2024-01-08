import json
import os

import discord


class Database:
    def __init__(self, file: str):
        self.filepath = file
        if not os.path.exists(self.filepath):
            open(self.filepath, 'x').close()
        self.file = open(self.filepath, 'r')
        if self.file.read():
            self.file.seek(0)
            self.data = json.load(self.file)
        else:
            self.data = {}
        self.structure = {
            "guilds": {},
            "admins": {},
            "config": {
                "command_prefix": '&'
            }
        }
        self.guild_structure = {
            "task_channel_id": None,
            "mod_role_ids": {},
            "mod_user_ids": {},
            "command_prefix": None
        }
        self.initialize_data(self.data, self.structure)
        for guild in self.data["guilds"]:
            self.initialize_data(self.data["guilds"][guild], self.guild_structure)

    def save(self) -> None:
        with open(self.filepath, 'w') as f:
            json.dump(self.data, f)
            f.close()

    def close(self) -> None:
        self.save()
        self.file.close()
        del self

    def initialize_data(self, data: dict, structure: dict) -> None:
        for item in structure:
            if item not in data:
                if isinstance(item, dict):
                    data[item] = {}
                    self.initialize_data(structure[item], data[item])
                else:
                    data[item] = structure[item]
        self.save()


database = Database("haj.json")


def update_guild_ids(client: discord.Client) -> None:
    for guild in client.guilds:
        if str(guild.id) not in database.data["guilds"]:
            database.data["guilds"][str(guild.id)] = database.guild_structure.copy()
    database.save()


def is_admin(user_id: int) -> bool:
    if str(user_id) in database.data["admins"]:
        return True
    return False
