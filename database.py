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
        else:
            admin_role = []
            default_role = []
            channel = []
        self.instert_data(guild_name, guild_id, guild_roles, admin_role, default_role, channel)

    def instert_data(self, guild_name, guild_id, guild_roles, admin_role, default_role, channel): # Default case
        if guild_name in self.data:
            self.data[guild_name]["roles_id"] = guild_roles
            self.data[guild_name]["admin_role"] = admin_role
            self.data[guild_name]["default_role"] = default_role
            self.data[guild_name]["channel"] = channel
        else:
            self.data[guild_name] = {
                "id": guild_id,
                "roles_id": guild_roles,
                "admin_role": admin_role,
                "default_role": default_role,
                "channel": channel
            }
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=4, ensure_ascii=False)

    def is_admin_role(self, guild_name, roles):
        for role in roles:
            if role in self.data[guild_name]["admin_role"]:
                return True
        return False

    def add_admin(self, guild_name, role):
        admin_roles = self.data[guild_name]["admin_role"]
        if role in admin_roles:
            return False
        admin_roles.append(role)
        self.data[guild_name]["admin_role"] = admin_roles
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=4, ensure_ascii=False)

    def remove_admin(self, guild_name, role):
        admin_roles = self.data[guild_name]["admin_role"]
        if role not in admin_roles:
            return False
        admin_roles.remove(role)
        self.data[guild_name]["admin_role"] = admin_roles
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=4, ensure_ascii=False)

    def set_default_value(self, guild_name, key, channel):
        current_channel = self.data[guild_name][key]
        if not current_channel:
            print(f"ERROR set_default_value, {key} value was not set for {guild_name}!")
        if current_channel == channel:
            return False
        self.data[guild_name][key] = channel
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=4, ensure_ascii=False)
        return True

    def get_value(self, guild_name, key):
        return self.data[guild_name][key]