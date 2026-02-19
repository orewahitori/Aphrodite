import discord
from discord import app_commands
from discord.ext import commands

from functools import wraps
import random

from cog_services.service_gen import GeneralService

class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.service_gen = GeneralService(bot.config_file)
        self.bot.log.write("INFO", "general - __init__", "General initialized")


    def silent_mode(func):
        @wraps(func)
        async def wrapper(self, interaction: discord.Interaction, *args, **kwargs):
            guild = interaction.guild.name
            silent_mode = self.bot.config_file.get_value(guild, "silent_mode")
            command_list = self.bot.config_file.get_value(guild, "command_list")
            if (command_list and func.__name__ in command_list) or silent_mode:
                return await interaction.response.send_message("Включен silent mode, обратитесь к администраторам сервера",
                                                               ephemeral=True)
            return await func(self, interaction, *args, **kwargs)
        return wrapper


    @app_commands.command(name="avatar", description="Показать аватар пользователя")
    @silent_mode
    async def avatar(
        self,
        interaction: discord.Interaction,
        member: discord.Member
    ):
        result = self.service_gen.avatar(member)

        await interaction.response.send_message(f"{result}")


    @app_commands.command(name="roll", description="Выдать случайное число")
    @silent_mode
    async def roll(
        self,
        interaction: discord.Interaction,
        range_value: str
    ):
        result = self.service_gen.roll(range_value)

        await interaction.response.send_message(f"{result}")


    @app_commands.command(name="rules", description="Отобразить правила сообщества")
    @silent_mode
    async def rules(
        self,
        interaction: discord.Interaction
    ):
        result = self.service_gen.rules()

        await interaction.response.send_message("TBD!")


async def setup(bot):
    await bot.add_cog(General(bot))