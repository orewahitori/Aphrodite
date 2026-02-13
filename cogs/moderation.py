import discord
from discord import app_commands
from discord.ext import commands
from functools import wraps


class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def admin_only(func):
        @wraps(func)
        async def wrapper(self, interaction: discord.Interaction, *args, **kwargs):
            guild = interaction.guild.name
            admin_roles = self.bot.config_file.get_value(guild, "admin_role")
            user_roles = [role.id for role in interaction.user.roles]
            is_admin = interaction.permissions.administrator
            if any(admin in user_roles for admin in admin_roles) or is_admin:
                return await func(self, interaction, *args, **kwargs)

            return await interaction.response.send_message("❌ У вас нет прав использовать эту команду!",
                                                        ephemeral=True)
        return wrapper

    @app_commands.command(name="set_role", description="Заменить роли на выданную")
    @admin_only
    async def set_role(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        role: discord.Role
    ):
        roles_to_remove = [r for r in member.roles if r != member.guild.default_role]
        if roles_to_remove:
            await member.remove_roles(*roles_to_remove)
        await member.add_roles(role)
        await interaction.response.send_message(f"✅ {member.mention} теперь с ролью {role.name}",
                                                ephemeral=True)

    @app_commands.command(name="extend_rights", description="Выдать роли расширенные права на бота")
    @admin_only
    async def extend_rights(
        self,
        interaction: discord.Interaction,
        role: discord.Role
    ):
        config_file = self.bot.config_file

        if config_file.add_value(interaction.guild.name, "admin_role", role.id) == False:
            await interaction.response.send_message("Роль уже обладает расширенными правами",
                                                    ephemeral=True)
        else:
            await interaction.response.send_message(f"Роль {role.name} получила расширенные права",
                                                    ephemeral=True)

    @app_commands.command(name="take_away_rights", description="Забрать у роли расширенные права на бота")
    @admin_only
    async def take_away_rights(
        self,
        interaction: discord.Interaction,
        role: discord.Role
    ):
        config_file = self.bot.config_file

        if config_file.rem_value(interaction.guild.name, "admin_role", role.id) == False:
            await interaction.response.send_message("Роль не обладает расширенными правами",
                                                    ephemeral=True)
        else:
            await interaction.response.send_message(f"Роль {role.name} лишилась расширенных прав",
                                                    ephemeral=True)

    @app_commands.command(name="sync_roles", description="Обновить ID ролей на сервере")
    async def sync_roles(
        self,
        interaction: discord.Interaction
    ):
        config_file = self.bot.config_file
        guild = interaction.guild
        guild_roles = [guild_role.id for guild_role in guild.roles]

        config_file.sync_data(interaction.guild.name, guild.id, guild_roles)
        await interaction.response.send_message("Роли успешно обновлены",
                                                ephemeral=True)

    @app_commands.command(name="set_channel", description="Изменить основной канал бота")
    @admin_only
    async def set_channel(
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel
    ):
        config_file = self.bot.config_file

        if config_file.set_value(interaction.guild.name, "channel", channel.id) == False:
            await interaction.response.send_message("Канал уже является основным",
                                                    ephemeral=True)
        else:
            await interaction.response.send_message("Канал успешно обновлен",
                                                    ephemeral=True)


    @app_commands.command(name="set_default_role", description="Изменить роль участников по умолчанию")
    @admin_only
    async def set_channel(
        self,
        interaction: discord.Interaction,
        role: discord.Role
    ):
        config_file = self.bot.config_file

        if config_file.set_value(interaction.guild.name, "default_role", role.id) == False:
            await interaction.response.send_message("Роль уже выставлена по умолчанию",
                                                    ephemeral=True)
        else:
            await interaction.response.send_message("Роль по умолчанию успешно обновлена",
                                                    ephemeral=True)

    @app_commands.command(name="enable_silent_mode", description="Отключить команды бота")
    @admin_only
    async def enable_silent_mode(
        self,
        interaction: discord.Interaction
    ):
        config_file = self.bot.config_file
        guild = interaction.guild

        if config_file.set_value(interaction.guild.name, "silent_mode", True) == False:
            await interaction.response.send_message("silent mode уже включен",
                                                    ephemeral=True)
        else:
            await interaction.response.send_message("silent mode включен",
                                                    ephemeral=True)

    @app_commands.command(name="disable_silent_mode", description="Включить команды бота")
    @admin_only
    async def disable_silent_mode(
        self,
        interaction: discord.Interaction
    ):
        config_file = self.bot.config_file
        guild = interaction.guild

        if config_file.set_value(interaction.guild.name, "silent_mode", False) == False:
            await interaction.response.send_message("silent mode уже выключен",
                                                    ephemeral=True)
        else:
            await interaction.response.send_message("silent mode выключен",
                                                    ephemeral=True)

    @app_commands.command(name="disable_command", description="Отключить отдельную команду")
    @admin_only
    async def disable_command(
        self,
        interaction: discord.Interaction,
        command: str
    ):
        config_file = self.bot.config_file
        guild = interaction.guild

        if command in self.bot.bot_commands:
            if config_file.add_value(interaction.guild.name, "command_list", command) == False:
                await interaction.response.send_message("Команда уже отключена",
                                                        ephemeral=True)
            else:
                await interaction.response.send_message("Команда успешно отключена",
                                                        ephemeral=True)
        else:
            await interaction.response.send_message("Указанной команды не существует",
                                                    ephemeral=True)

    @app_commands.command(name="enable_command", description="Включить отдельную команду")
    @admin_only
    async def enable_command(
        self,
        interaction: discord.Interaction,
        command: str
    ):
        config_file = self.bot.config_file
        guild = interaction.guild

        if command in self.bot.bot_commands:
            if config_file.rem_value(interaction.guild.name, "command_list", command) == False:
                await interaction.response.send_message("Команда уже включена",
                                                        ephemeral=True)
            else:
                await interaction.response.send_message("Команда успешно включена",
                                                        ephemeral=True)
        else:
            await interaction.response.send_message("Указанной команды не существует",
                                                    ephemeral=True)


async def setup(bot):
    await bot.add_cog(Moderation(bot))