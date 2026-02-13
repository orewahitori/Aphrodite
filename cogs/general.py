import discord
import random

from discord import app_commands
from discord.ext import commands
from functools import wraps

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

class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="avatar", description="Показать аватар пользователя")
    @silent_mode
    async def avatar(
        self,
        interaction: discord.Interaction,
        member: discord.Member
    ):
        if member.avatar!=None:
            await interaction.response.send_message(member.display_avatar.url)
        else:
            await interaction.response.send_message(f"У пользователя {member.name} отсутствует аватар",
                                                ephemeral=True)

    @app_commands.command(name="roll", description="Выдать случайное число")
    @silent_mode
    async def roll(
        self,
        interaction: discord.Interaction,
        range_value: str
    ):
        try:
            result = random.randint(1, int(range_value))
            await interaction.response.send_message(f"Результат до {range_value}:\n{result}")
        except ValueError:
            await interaction.response.send_message("Введенные данные не являются числом",
                                                ephemeral=True)

    @app_commands.command(name="rules", description="Отобразить правила сообщества")
    @silent_mode
    async def rules(self, interaction: discord.Interaction):
        await interaction.response.send_message("TBD!",
                                                ephemeral=True)

async def setup(bot):
    await bot.add_cog(General(bot))