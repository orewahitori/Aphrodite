import discord
import os

from discord import app_commands, Interaction
from dotenv import load_dotenv
from discord.ext import commands

load_dotenv()

# Channels IDs
GENERAL_TXT_ID = 829417871653601322

# Roles IDs
SOLDIER_ROLE = 1464012394937454744
SPARTAN_ROLE = 1464011950722908273
SENATOR_ROLE = 907256530821324860
EMPEROR_ROLE = 907237685855420416

switch_role = {
    "soldier": SOLDIER_ROLE,
    "spartan": SPARTAN_ROLE,
    "senator": SENATOR_ROLE
}

class MyBot(discord.Client):
    def __init__(self):
        intents = discord.Intents.default() # Adding permissions
        intents.message_content = True
        intents.members = True
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        await self.tree.sync()
    async def on_member_join(self, member: discord.Member):
        channel = member.guild.get_channel(GENERAL_TXT_ID)
        role = member.guild.get_role(SOLDIER_ROLE)

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
@app_commands.checks.has_role(EMPEROR_ROLE)
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

@Aphrodite.tree.error
async def on_app_command_error(
    interaction: discord.Interaction,
    error: app_commands.errors.CheckFailure
):
    await interaction.response.send_message("❌ У вас нет прав использовать эту команду!")

Aphrodite.run(os.getenv("DISCORD_TOKEN"))