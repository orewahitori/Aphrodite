from unittest import result
import discord


class ModerationService:
    def __init__(self, config_file):
        self.config_file = config_file


    
    async def kick_user(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        reason: str
    ):
        if interaction.permissions.kick_members == True:
            await interaction.guild.kick(member)
            return "Пользователь удален с сервера"


    async def ban_user(
        self,
        interaction: discord.Integration,
        member: discord.Member,
        reason: str
    ):
        if interaction.permissions.ban_members == True:
            await interaction.guild.ban(member)
            return "Пользователь забанен"

        
    async def unban_user(
        self,
        interaction: discord.Interaction,
        user: str,
        reason: str  
    ):
        try:
            user_id = int(user.strip())
            if interaction.permissions.ban_members == True:
                await interaction.guild.unban(discord.Object(id=user_id))
                return "Пользователь разбанен"
        except:
            return "Не удалось разблокировать"
        