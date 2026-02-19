import discord

class CallbackService:
    def __init__(self, config_file, log):
        self.config_file = config_file
        self.log = log
        self.log.write("INFO", "service_cb - __init__", "CallbackService initialized")


    def on_guild_join(
        self,
        guild: discord.Guild
):
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
        return main_channel


    def on_member_join(
        self,
        member: discord.Member
):
        channel_id = self.config_file.get_value(member.guild.name, "channel")
        default_role = self.config_file.get_value(member.guild.name, "default_role")

        channel = member.guild.get_channel(channel_id)
        role = member.guild.get_role(default_role)

        return channel, role