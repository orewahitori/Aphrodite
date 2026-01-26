import discord
import os
import json
import database

from discord import app_commands, Interaction
from dotenv import load_dotenv
from discord.ext import commands

load_dotenv()

class MyBot(discord.Client):
    def __init__(self):
        intents = discord.Intents.default() # Adding permissions
        intents.message_content = True
        intents.members = True
        self.config_file = database.GuildDataStorage("guild_config.json")

        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        await self.tree.sync()

    async def on_guild_join(self, guild: discord.Guild):
        guild_roles = [role.id for role in guild.roles]
        admins = [member.id for member in guild.members
                  if member.guild_permissions.administrator
        ]
        default_role = guild.roles[0]
        main_channel = guild.system_channel or next(
            (channel for channel in guild.text_channels  if channel.permissions_for(guild.me).send_messages),
            None
        )
        self.config_file.instert_data(guild.name, guild.id, guild_roles, admins.id,
                                      default_role.id, main_channel.id)
        await main_channel.send(f"Привет, {default_role.mention}!")

    async def on_member_join(self, member: discord.Member):
        channel_id = self.config_file.get_value(member.guild.name, "channel")
        default_role = self.config_file.get_value(member.guild.name, "default_role")

        channel = member.guild.get_channel(channel_id)
        role = member.guild.get_role(default_role)

        if channel:
            await channel.send(f"Привет, {member.mention}!")
        else:
            print(f"ERROR: on_member_join - Failed to connect to {channel} channel")
        if role:
            await member.add_roles(role)
        else:
            print(f"ERROR: on_member_join - Failed to add {role} role to {member}")

Aphrodite = MyBot()

# Implement a reacton to commands
@Aphrodite.tree.command(name="rules", description="Отобразить правила сообщества")
async def rules(interaction: discord.Interaction):
    await interaction.response.send_message("TBD")

@Aphrodite.tree.command(name="set_role", description="Заменить роли на выданную")
async def set_role(
    interaction: discord.Interaction,
    member: discord.Member,
    role: discord.Role
):
    if role:
        roles_to_remove = [r for r in member.roles if r != member.guild.default_role]
        if roles_to_remove:
            await member.remove_roles(*roles_to_remove)
    await member.remove_roles()
    await member.add_roles(role)
    await interaction.response.send_message(f"✅ {member.mention} теперь с ролью {role.name}",
                                            ephemeral=True)

@Aphrodite.tree.command(name="extend_rights", description="Выдать роли расширенные права на бота")
async def extend_rights(
    interaction: discord.Interaction,
    role: discord.Role
):
    config_file = Aphrodite.config_file
    guild = interaction.guild
    user_roles = [role.id for role in interaction.user.roles]

    if guild.roles[-1].id in user_roles or config_file.is_admin_role(guild.name, user_roles):
        if config_file.add_admin(guild.name, role.id) == False:
            await interaction.response.send_message("Роль уже обладает расширенными правами",
                                                    ephemeral=True)
        else:
            await interaction.response.send_message(f"Роль {role.name} получила расширенные права",
                                                ephemeral=True)
    else:
        await interaction.response.send_message("Недостаточно прав",
                                                ephemeral=True)

@Aphrodite.tree.command(name="take_away_rights", description="Забрать у роли расширенные права на бота")
async def take_away_rights(
    interaction: discord.Interaction,
    role: discord.Role
):
    config_file = Aphrodite.config_file
    guild = interaction.guild
    user_roles = [role.id for role in interaction.user.roles]

    if guild.roles[-1].id in user_roles or config_file.is_admin_role(guild.name, user_roles):
        if config_file.remove_admin(guild.name, role.id) == False:
            await interaction.response.send_message("Роль не обладает расширенными правами",
                                                    ephemeral=True)
        else:
            await interaction.response.send_message(f"Роль {role.name} лишилась расширенных прав",
                                                ephemeral=True)
    else:
        await interaction.response.send_message("Недостаточно прав",
                                                ephemeral=True)

@Aphrodite.tree.command(name="sync_roles", description="Обновить ID ролей на сервере")
async def sync_roles(
    interaction: discord.Interaction
):
    config_file = Aphrodite.config_file
    guild = interaction.guild
    guild_roles = [guild_role.id for guild_role in guild.roles]
    user_roles = [role.id for role in interaction.user.roles]

    if guild.roles[-1].id in user_roles or config_file.is_admin_role(guild.name, user_roles):
        config_file.sync_data(guild.name, guild.id, guild_roles)
        await interaction.response.send_message("Роли успешно обновлены",
                                                ephemeral=True)
    else:
        await interaction.response.send_message("Недостаточно прав",
                                                ephemeral=True)

@Aphrodite.tree.command(name="set_channel", description="Изменить основной канал бота")
async def set_channel(
    interaction: discord.Interaction,
    channel: discord.TextChannel
):
    config_file = Aphrodite.config_file
    guild = interaction.guild
    user_roles = [role.id for role in interaction.user.roles]

    if guild.roles[-1].id in user_roles or config_file.is_admin_role(guild.name, user_roles):
        if config_file.set_default_value(guild.name, "channel", channel.id) == False:
            await interaction.response.send_message("Канал уже является основным",
                                                    ephemeral=True)
        else:
            await interaction.response.send_message("Канал успешно обновлен",
                                                ephemeral=True)
    else:
        await interaction.response.send_message("Недостаточно прав",
                                                ephemeral=True)

@Aphrodite.tree.command(name="set_default_role", description="Изменить роль участников по умолчанию")
async def set_channel(
    interaction: discord.Interaction,
    role: discord.Role
):
    config_file = Aphrodite.config_file
    guild = interaction.guild
    user_roles = [role.id for role in interaction.user.roles]

    if guild.roles[-1].id in user_roles or config_file.is_admin_role(guild.name, user_roles):
        if config_file.set_default_value(guild.name, "default_role", role.id) == False:
            await interaction.response.send_message("Роль уже выставлена по умолчанию",
                                                    ephemeral=True)
        else:
            await interaction.response.send_message("Роль по умолчанию успешно обновлена",
                                                ephemeral=True)
    else:
        await interaction.response.send_message("Недостаточно прав",
                                                ephemeral=True)

@Aphrodite.tree.error
async def on_app_command_error(
    interaction: discord.Interaction,
    error: app_commands.errors.CheckFailure
):
    print(f"ERROR: {error}")
    await interaction.response.send_message("❌ У вас нет прав использовать эту команду!",
                                            ephemeral=True)

Aphrodite.run(os.getenv("DISCORD_TOKEN"))