import json
from pathlib import Path

class JsonStorage:
    def __init__(self, path):
        self.path = Path(path)
        if not self.path.exists():
            self.path.write_text("{}", encoding="utf-8")
        self.data = self.load()

    def load(self):
        with open(self.path, "r", encoding="utf-8") as f:
            return json.load(f)

class GuildDataStorage(JsonStorage):
    def save_data(self):
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=4, ensure_ascii=False)

    def sync_data(self, guild_name, guild_id, guild_roles): # Sync case only
        if guild_name in self.data:
            admin_role = self.data[guild_name]["admin_role"]
            default_role = self.data[guild_name]["default_role"]
            channel = self.data[guild_name]["channel"]
            command_list = self.data[guild_name]["command_list"]
            silent_mode = self.data[guild_name]["silent_mode"]
        else:
            admin_role = []
            default_role = []
            channel = []
            command_list = []
            silent_mode = False
        self.instert_data(guild_name, guild_id, guild_roles, admin_role,
                          default_role, channel, command_list, silent_mode)

    def instert_data(self, guild_name, guild_id, guild_roles, admin_role,
                     default_role, channel, command_list, silent_mode):
        if guild_name in self.data:
            self.data[guild_name]["id"] = guild_id
            self.data[guild_name]["roles_id"] = guild_roles
            self.data[guild_name]["admin_role"] = admin_role
            self.data[guild_name]["default_role"] = default_role
            self.data[guild_name]["channel"] = channel
            self.data[guild_name]["command_list"] = command_list
            self.data[guild_name]["silent_mode"] = silent_mode
        else:
            self.data[guild_name] = {
                "id": guild_id,
                "roles_id": guild_roles,
                "admin_role": admin_role,
                "default_role": default_role,
                "channel": channel,
                "command_list": command_list,
                "silent_mode": silent_mode
            }
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=4, ensure_ascii=False)

    def is_admin_role(self, guild_name, roles):
        for role in roles:
            if role in self.data[guild_name]["admin_role"]:
                return True
        return False

    def add_value(self, guild_name, key, value):
        values = self.data[guild_name][key]
        if value in values:
            return False
        values.append(value)
        self.data[guild_name][key] = values
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=4, ensure_ascii=False)

    def rem_value(self, guild_name, key, value):
        values = self.data[guild_name][key]
        if value not in values:
            return False
        values.remove(value)
        self.data[guild_name][key] = values
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=4, ensure_ascii=False)

    def set_value(self, guild_name, key, channel):
        current_channel = self.data[guild_name][key]
        if not current_channel:
            print(f"ERROR set_value, {key} value was not set for {guild_name}!")
        if current_channel == channel:
            return False
        self.data[guild_name][key] = channel
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=4, ensure_ascii=False)
        return True

    def get_value(self, guild_name, key):
        if self.data[guild_name][key]:
            return self.data[guild_name][key]
        return ""