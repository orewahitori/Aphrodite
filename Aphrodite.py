from code import interact
from re import S
import discord
import os
import json
import database
import deepl
from deepl import deepl_client
import random

from discord import app_commands, Interaction
from dotenv import load_dotenv
from discord.ext import commands
from functools import wraps
from enum import Enum, auto

load_dotenv()

bot_commands = ["rules"]

deepl_client = deepl.DeepLClient(os.getenv("DEEPL_KEY"))

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
        commands_list = []
        silent_mode = False

        self.config_file.instert_data(guild.name, guild.id, guild_roles, admins, default_role.id,
                                      main_channel.id, commands_list, silent_mode)
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

@Aphrodite.tree.command(name="avatar", description="Показать аватар пользователя")
async def avatar(
    interaction: discord.Interaction,
    member: discord.Member
):
    if member.avatar!=None:
        await interaction.response.send_message(member.display_avatar.url)
    else:
        await interaction.response.send_message(f"У пользователя {member.name} отсутствует аватар",
                                                ephemeral=True)

@Aphrodite.tree.command(name="roll", description="Выдать случайное число")
async def roll(
    interaction: discord.Interaction,
    range_value: str
):
    try:
        result = random.randint(1, int(range_value))
        await interaction.response.send_message(result)
    except ValueError:
        await interaction.response.send_message("Введенные данные не являются числом",
                                                ephemeral=True)
def silent_mode(func):
    @wraps(func)
    async def wrapper(interaction: discord.Interaction, *args, **kwargs):
        guild = interaction.guild.name
        silent_mode = Aphrodite.config_file.get_value(guild, "silent_mode")
        command_list = Aphrodite.config_file.get_value(guild, "command_list")
        if (command_list and func.__name__ in command_list) or silent_mode:
            return await interaction.response.send_message("Включен silent mode, обратитесь к администраторам сервера",
                                                           ephemeral=True)
        return await func(interaction, *args, **kwargs)
    return wrapper

def admin_only(func):
    @wraps(func)
    async def wrapper(interaction: discord.Interaction, *args, **kwargs):
        guild = interaction.guild.name
        admin_roles = Aphrodite.config_file.get_value(guild, "admin_role")
        user_roles = [role.id for role in interaction.user.roles]
        is_admin = interaction.permissions.administrator
        if any(admin in user_roles for admin in admin_roles) or is_admin:
            return await func(interaction, *args, **kwargs)

        return await interaction.response.send_message("❌ У вас нет прав использовать эту команду!",
                                                       ephemeral=True)
    return wrapper

# Implement a reacton to commands
@Aphrodite.tree.command(name="rules", description="Отобразить правила сообщества")
@silent_mode
async def rules(interaction: discord.Interaction):
    await interaction.response.send_message("TBD!",
                                            ephemeral=True)

@Aphrodite.tree.command(name="set_role", description="Заменить роли на выданную")
@admin_only
async def set_role(
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

@Aphrodite.tree.command(name="extend_rights", description="Выдать роли расширенные права на бота")
@admin_only
async def extend_rights(
    interaction: discord.Interaction,
    role: discord.Role
):
    config_file = Aphrodite.config_file

    if config_file.add_value(interaction.guild.name, "admin_role", role.id) == False:
        await interaction.response.send_message("Роль уже обладает расширенными правами",
                                                ephemeral=True)
    else:
        await interaction.response.send_message(f"Роль {role.name} получила расширенные права",
                                                ephemeral=True)

@Aphrodite.tree.command(name="take_away_rights", description="Забрать у роли расширенные права на бота")
@admin_only
async def take_away_rights(
    interaction: discord.Interaction,
    role: discord.Role
):
    config_file = Aphrodite.config_file

    if config_file.rem_value(interaction.guild.name, "admin_role", role.id) == False:
        await interaction.response.send_message("Роль не обладает расширенными правами",
                                                ephemeral=True)
    else:
        await interaction.response.send_message(f"Роль {role.name} лишилась расширенных прав",
                                                ephemeral=True)

@Aphrodite.tree.command(name="sync_roles", description="Обновить ID ролей на сервере")
#@admin_only
async def sync_roles(
    interaction: discord.Interaction
):
    config_file = Aphrodite.config_file
    guild = interaction.guild
    guild_roles = [guild_role.id for guild_role in guild.roles]

    config_file.sync_data(interaction.guild.name, guild.id, guild_roles)
    await interaction.response.send_message("Роли успешно обновлены",
                                            ephemeral=True)

@Aphrodite.tree.command(name="set_channel", description="Изменить основной канал бота")
@admin_only
async def set_channel(
    interaction: discord.Interaction,
    channel: discord.TextChannel
):
    config_file = Aphrodite.config_file

    if config_file.set_value(interaction.guild.name, "channel", channel.id) == False:
        await interaction.response.send_message("Канал уже является основным",
                                                ephemeral=True)
    else:
        await interaction.response.send_message("Канал успешно обновлен",
                                                ephemeral=True)


@Aphrodite.tree.command(name="set_default_role", description="Изменить роль участников по умолчанию")
@admin_only
async def set_channel(
    interaction: discord.Interaction,
    role: discord.Role
):
    config_file = Aphrodite.config_file

    if config_file.set_value(interaction.guild.name, "default_role", role.id) == False:
        await interaction.response.send_message("Роль уже выставлена по умолчанию",
                                                ephemeral=True)
    else:
        await interaction.response.send_message("Роль по умолчанию успешно обновлена",
                                                ephemeral=True)

@Aphrodite.tree.command(name="enable_silent_mode", description="Отключить команды бота")
@admin_only
async def enable_silent_mode(
    interaction: discord.Interaction
):
    config_file = Aphrodite.config_file
    guild = interaction.guild

    if config_file.set_value(interaction.guild.name, "silent_mode", True) == False:
        await interaction.response.send_message("silent mode уже включен",
                                                ephemeral=True)
    else:
        await interaction.response.send_message("silent mode включен",
                                                ephemeral=True)

@Aphrodite.tree.command(name="disable_silent_mode", description="Включить команды бота")
@admin_only
async def disable_silent_mode(
    interaction: discord.Interaction
):
    config_file = Aphrodite.config_file
    guild = interaction.guild

    if config_file.set_value(interaction.guild.name, "silent_mode", False) == False:
        await interaction.response.send_message("silent mode уже выключен",
                                                ephemeral=True)
    else:
        await interaction.response.send_message("silent mode выключен",
                                                ephemeral=True)

@Aphrodite.tree.command(name="disable_command", description="Отключить отдельную команду")
@admin_only
async def disable_command(
    interaction: discord.Interaction,
    command: str
):
    config_file = Aphrodite.config_file
    guild = interaction.guild

    if command in bot_commands:
        if config_file.add_value(interaction.guild.name, "command_list", command) == False:
            await interaction.response.send_message("Команда уже отключена",
                                                    ephemeral=True)
        else:
            await interaction.response.send_message("Команда успешно отключена",
                                                    ephemeral=True)
    else:
        await interaction.response.send_message("Указанной команды не существует",
                                                ephemeral=True)

@Aphrodite.tree.command(name="enable_command", description="Включить отдельную команду")
@admin_only
async def enable_command(
    interaction: discord.Interaction,
    command: str
):
    config_file = Aphrodite.config_file
    guild = interaction.guild

    if command in bot_commands:
        if config_file.rem_value(interaction.guild.name, "command_list", command) == False:
            await interaction.response.send_message("Команда уже включена",
                                                    ephemeral=True)
        else:
            await interaction.response.send_message("Команда успешно включена",
                                                    ephemeral=True)
    else:
        await interaction.response.send_message("Указанной команды не существует",
                                                ephemeral=True)

@Aphrodite.tree.context_menu(name="Translate")
async def translate_message(
    interaction: discord.Interaction,
    message: discord.Message
):
    if not message.content:
        interaction.response.send_message("No message to translate",
                                          ephemeral=True)
        return

    translated = deepl_client.translate_text(message.content, target_lang="RU")
    await interaction.response.send_message(f"{translated}")


"""
@Aphrodite.tree.error
async def on_app_command_error(
    interaction: discord.Interaction,
    error: app_commands.errors.CheckFailure
):
    print(f"ERROR: {error}")
    await interaction.response.send_message("❌ У вас нет прав использовать эту команду!",
                                            ephemeral=True)"""

Aphrodite.run(os.getenv("DISCORD_TOKEN"))