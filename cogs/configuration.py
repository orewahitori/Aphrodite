import discord
from discord import app_commands
from discord.ext import commands

from functools import wraps

from cog_services.service_conf import ConfService


class Configuration(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.service_conf = ConfService(bot.config_file, bot.log)
        self.bot.log.write("INFO", "configuration - __init__",
                           "Configuration initialized")


    def admin_only(func):
        @wraps(func)
        async def wrapper(self, interaction: discord.Interaction, *args, **kwargs):
            if self.service_conf.admin_only_wrapper(interaction):
                return await func(self, interaction, *args, **kwargs)
            self.bot.log.write("WARN", "configuration - admin_only",
                               f"Forbidden to use {func} func by {interaction.user} on {interaction.guild}")
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
        roles_to_remove = self.service_conf.roles_to_remove(member, role)
        if roles_to_remove:
            for r in roles_to_remove: await member.remove_roles(r)
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
        response = self.service_conf.extend_rights(interaction.guild, role)

        await interaction.response.send_message(f"{response}",
                                                ephemeral=True)
        

    @app_commands.command(name="take_away_rights", description="Забрать у роли расширенные права на бота")
    @admin_only
    async def take_away_rights(
        self,
        interaction: discord.Interaction,
        role: discord.Role
    ):
        response = self.service_conf.take_away_rights(interaction.guild, role)

        await interaction.response.send_message(f"{response}",
                                                ephemeral=True)


    @app_commands.command(name="sync_roles", description="Обновить ID ролей на сервере")
    async def sync_roles(
        self,
        interaction: discord.Interaction
    ):
        response = self.service_conf.sync_roles(interaction.guild)
        
        await interaction.response.send_message(f"{response}",
                                                ephemeral=True)


    @app_commands.command(name="set_channel", description="Изменить основной канал бота")
    @admin_only
    async def set_channel(
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel
    ):
        response = self.service_conf.set_channel(interaction.guild, channel)
        
        await interaction.response.send_message(f"{response}",
                                                ephemeral=True)


    @app_commands.command(name="set_default_role", description="Изменить роль участников по умолчанию")
    @admin_only
    async def set_default_role(
        self,
        interaction: discord.Interaction,
        role: discord.Role
    ):
        response = self.service_conf.set_default_role(interaction.guild, role)
        
        await interaction.response.send_message(f"{response}",
                                                ephemeral=True)


    @app_commands.command(name="enable_silent_mode", description="Отключить команды бота")
    @admin_only
    async def enable_silent_mode(
        self,
        interaction: discord.Interaction
    ):
        response = self.service_conf.enable_silent_mode(interaction.guild)
        
        await interaction.response.send_message(f"{response}",
                                                ephemeral=True)


    @app_commands.command(name="disable_silent_mode", description="Включить команды бота")
    @admin_only
    async def disable_silent_mode(
        self,
        interaction: discord.Interaction
    ):
        response = self.service_conf.disable_silent_mode(interaction.guild)
        
        await interaction.response.send_message(f"{response}",
                                                ephemeral=True)


    @app_commands.command(name="disable_command", description="Отключить отдельную команду")
    @admin_only
    async def disable_command(
        self,
        interaction: discord.Interaction,
        command: str
    ):
        response = self.service_conf.disable_command(interaction.guild, command)
        
        await interaction.response.send_message(f"{response}",
                                                ephemeral=True)


    @app_commands.command(name="enable_command", description="Включить отдельную команду")
    @admin_only
    async def enable_command(
        self,
        interaction: discord.Interaction,
        command: str
    ):
        response = self.service_conf.enable_command(interaction.guild, command)
        
        await interaction.response.send_message(f"{response}",
                                                ephemeral=True)


async def setup(bot):
    await bot.add_cog(Configuration(bot))