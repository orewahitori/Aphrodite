import discord
import os

from dotenv import load_dotenv
load_dotenv()
from discord.ext import commands

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

help_text = """
***Список команд бота:***
/help - показать это сообщение
/rules - показать правила сервера
"""
# Channels IDs
GENERAL_TXT_ID = 829417871653601322

intents = discord.Intents.default() # Adding permissions

# Intents from Discord Development Portal
# https://discord.com/developers/applications/1463994781989601418
intents.message_content = True
intents.members = True

# Prefixes, used to set the trigger character
bot = commands.Bot(command_prefix='/', intents=intents, help_command=None) 

def has_role(role_id):
    async def predicate(ctx):
        return any(r.id == role_id for r in ctx.author.roles)
    return commands.check(predicate)

# Implement a reacton to commands
@bot.command()
async def rules(ctx):
    await ctx.send("TBD")
@bot.command()
async def help(ctx):
    await ctx.send(help_text)
@bot.command()
@has_role(EMPEROR_ROLE)
async def set_role(ctx, user: discord.Member, given_role: str):
    role_id = switch_role.get(given_role.lower())
    if not role_id:
        await ctx.send("Такой роли не существует")
        return
    role = ctx.guild.get_role(role_id)

    # Removing previously given roles
    roles_to_remove = [r for r in user.roles if r.id in switch_role.values()]
    if roles_to_remove:
        await user.remove_roles(*roles_to_remove)

    # Adding given role to the member
    await user.add_roles(role)
    await ctx.send(f"✅ {user.mention} теперь с ролью {given_role}")


bot.run(os.getenv("DISCORD_TOKEN"))