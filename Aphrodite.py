import discord
import os
import deepl

from code import interact
from dotenv import load_dotenv
from discord import app_commands, Interaction
from discord.ext import commands
from deepl import deepl_client

from databases.database import GuildDataStorage
from cog_services.service_cb import CallbackService

load_dotenv()


deepl_client = deepl.DeepLClient(os.getenv("DEEPL_KEY"))

class MyBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default() # Adding permissions
        intents.message_content = True
        intents.members = True

        self.config_file = GuildDataStorage("guild_config.json")
        self.service_cb = CallbackService(self.config_file)

        super().__init__(command_prefix="/", intents=intents)

    async def setup_hook(self):
        await self.load_extension("cogs.general")
        await self.load_extension("cogs.configuration")
        await self.tree.sync()

    async def on_guild_join(self, guild: discord.Guild):
        channel, role = self.service_cb.on_guild_join(guild)
        await channel.send("Привет!")

    async def on_member_join(self, member: discord.Member):
        channel, role = self.service_cb.on_member_join(member)

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