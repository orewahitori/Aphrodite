import discord
import os
import database
import deepl

from deepl import deepl_client
from code import interact
from discord import app_commands, Interaction
from dotenv import load_dotenv
from discord.ext import commands
from functools import wraps

load_dotenv()


deepl_client = deepl.DeepLClient(os.getenv("DEEPL_KEY"))

class MyBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default() # Adding permissions
        intents.message_content = True
        intents.members = True
        self.config_file = database.GuildDataStorage("guild_config.json")
        self.bot_commands = ["rules"]

        super().__init__(command_prefix="/", intents=intents)

    async def setup_hook(self):
        await self.load_extension("cogs.general")
        await self.load_extension("cogs.moderation")
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

        self.config_file.insert_data(guild.name, guild.id, guild_roles, admins, default_role.id,
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


@Aphrodite.tree.context_menu(name="Translate")
async def translate_message(
    interaction: discord.Interaction,
    message: discord.Message
):
    if not message.content:
        await interaction.response.send_message("No message to translate",
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