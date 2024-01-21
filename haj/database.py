import json
import os


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
            "admins": [],
            "config": {
                "command_prefix": '&',
                "tokens": {
                    "discord": None,
                    "tba": None
                }
            }
        }
        self.guild_structure = {
            "task_channel_id": None,
            "mod_channel_id": None,
            "enforce_mod_channel": False,
            "mod_role_ids": [],
            "mod_user_ids": [],
            "command_prefix": None
        }
        self.initialize_data(self.data, self.structure)
        for guild in self.data["guilds"]:
            self.initialize_data(self.data["guilds"][guild], self.guild_structure)
        self.data["guilds"] = {int(guild): data for guild, data in self.data["guilds"].items()}

    def save(self) -> None:
        temp = self.data.copy()
        temp["guilds"] = {str(guild): data for guild, data in temp["guilds"].items()}
        with open(self.filepath, 'w') as f:
            json.dump(temp, f)
            f.close()
        del temp

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
