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
        else:
            admin_role = []
            default_role = []
        self.instert_data(guild_name, guild_id, guild_roles, admin_role, default_role)

    def instert_data(self, guild_name, guild_id, guild_roles, admin_role, default_role): # Default case
        if guild_name in self.data:
            self.data[guild_name]["roles_id"] = guild_roles
            self.data[guild_name]["admin_role"] = admin_role
            self.data[guild_name]["default_role"] = default_role
        else:
            self.data[guild_name] = {
                "id": guild_id,
                "roles_id": guild_roles,
                "admin_role": admin_role,
                "default_role": default_role
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