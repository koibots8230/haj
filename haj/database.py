from __future__ import annotations
import os
from typing import TextIO

import json

import haj


class Database:
    layout = {
        "guilds": {
            "0": {
                "mod_roles": [],
                "mod_users": [],
                "prefix": None
            }
        },
        "bot": {
            "admins": [],
            "prefix": "&"
        }
    }

    def __init__(self, config: str | os.PathLike):
        self._path = config
        self._file = self._open_file()
        self._data = json.load(self._file)
        self.guilds = self._get_guilds()

    def _open_file(self, mode: str = None) -> TextIO:
        try:
            file = open(self._path, mode)
        except FileNotFoundError:
            open(self._path, 'x').close()
            file = open(self._path, mode)
        return file

    def _get_guilds(self) -> dict[int, haj.database.Guild]:
        return {
            guild.id: guild for guild in [
                haj.database.Guild(id_, guild) for (id_, guild) in self._data["guilds"].items()
            ]
        }


class Guild:
    def __init__(self, id_: int, config: dict[str]):
        try:
            self.id = id_
            self.mod_users = config["mod_users"]
            self.mod_roles = config["mod_roles"]
            self.prefix = config["prefix"]
        except KeyError:
            raise Exception(f"Error decoding config file: error in 'guilds'")
