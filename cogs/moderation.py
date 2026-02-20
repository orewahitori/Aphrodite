from typing import Required
from urllib import response
import discord
from discord import Interaction, app_commands
from discord.ext import commands

from functools import wraps

from cog_services.service_mod import ModerationService

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.service_mod = ModerationService(bot.config_file)


    @app_commands.command(name="kick_user", description="Выгнать пользователя")
    async def kick_user(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        reason: str = None,
    ):
        result = await self.service_mod.kick_user(interaction, member, reason)
        await interaction.response.send_message("Пользователь удален с сервера",
                                                ephemeral = True)


    @app_commands.command(name="ban_user", description="Забанить пользователя")
    async def ban_user(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        reason: str = None
    ):
        result = await self.service_mod.ban_user(interaction, member, reason)
        await interaction.response.send_message("Пользователь забанен",
                                                ephemeral = True)

        
    @app_commands.command(name="unban_user", description="Разбанить пользователя")
    async def unban_user(
        self,
        interaction: discord.Interaction,
        user: str,
        reason: str = None
    ):
        result = await self.service_mod.unban_user(interaction, user, reason)
        await interaction.response.send_message("Пользователь разбанен",
                                                ephemeral = True)
        

async def setup(bot):
    await bot.add_cog(Moderation(bot))