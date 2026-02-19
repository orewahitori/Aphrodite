import discord

class ConfService:
    def __init__(self, config_file, log):
        self.config_file = config_file
        self.log = log
        self.bot_commands = ["rules", "avatar", "roll"]
        self.log.write("INFO", "service_conf - __init__", "ConfService initialized")


    def admin_only_wrapper(
        self,
        interaction: discord.Interaction
    ):
            guild = interaction.guild.name
            admin_roles = self.config_file.get_value(guild, "admin_role")
            user_roles = [role.id for role in interaction.user.roles]
            is_admin = interaction.user.guild_permissions.administrator

            if any(admin in user_roles for admin in admin_roles) or is_admin:
                return True

            return False


    def roles_to_remove(
        self,
        member: discord.Member,
        role: discord.Role
    ):
        return [r for r in member.roles if r != member.guild.default_role]
    

    def extend_rights(
        self,
        guild: discord.Guild,
        role: discord.Role
    ):
        if self.config_file.add_value(guild.name, "admin_role", role.id) == False:
            result = "Роль уже обладает расширенными правами"
        else:
            result = f"Роль {role.name} получила расширенные права"

        return result


    def take_away_rights(
        self,
        guild: discord.Guild,
        role: discord.Role
    ):
        if self.config_file.rem_value(guild.name, "admin_role", role.id) == False:
            result = "Роль не обладает расширенными правами"
        else:
            result = f"Роль {role.name} лишилась расширенных прав"

        return result


    def sync_roles(
        self,
        guild: discord.Guild
    ):
        guild_roles = [guild_role.id for guild_role in guild.roles]

        self.config_file.sync_data(guild.name, guild.id, guild_roles)
        result = "Роли успешно обновлены"

        return result


    def set_channel(
        self,
        guild: discord.Guild,
        channel: discord.TextChannel
    ):
        if self.config_file.set_value(guild.name, "channel", channel.id) == False:
            result = "Канал уже является основным"
        else:
            result = "Канал успешно обновлен"

        return result


    def set_default_role(
        self,
        guild: discord.Guild,
        channel: discord.TextChannel
    ):
        if self.config_file.set_value(guild.name, "default_role", channel.id) == False:
            result = "Роль уже выставлена по умолчанию"
        else:
            result = "Роль по умолчанию успешно обновлена"

        return result


    def enable_silent_mode(
        self,
        guild: discord.Guild,
    ):
        if self.config_file.set_value(guild.name, "silent_mode", True) == False:
            result = "silent mode уже включен"
        else:
            result = "silent mode включен"

        return result


    def disable_silent_mode(
        self,
        guild: discord.Guild,
    ):
        if self.config_file.set_value(guild.name, "silent_mode", False) == False:
            result = "silent mode уже выключен"
        else:
            result = "silent mode выключен"

        return result


    def disable_command(
        self,
        guild: discord.Guild,
        command: str
    ):
        if command in self.bot_commands:
            if self.config_file.add_value(guild.name, "command_list", command) == False:
                result = "Команда уже отключена"
            else:
                result = "Команда успешно отключена"
        else:
            result = "Указанной команды не существует"

        return result


    def enable_command(
        self,
        guild: discord.Guild,
        command: str
    ):
        if command in self.bot_commands:
            if self.config_file.rem_value(guild.name, "command_list", command) == False:
                result = "Команда уже включена"
            else:
                result = "Команда успешно включена"
        else:
            result = "Указанной команды не существует"

        return result