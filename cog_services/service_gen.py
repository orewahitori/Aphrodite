import discord
import random

class GeneralService:
    def __init__(self, config_file):
        self.config_file = config_file


    def avatar(
        self,
        member: discord.Member
    ):
        if member.avatar!=None:
            result = member.display_avatar.url
        else:
            result = f"У пользователя {member.name} отсутствует аватар"

        return result


    def roll(
        self,
        range_value: str
    ):
        try:
            rand_value = random.randint(1, int(range_value))
            result = f"Результат до {range_value}:\n{rand_value}"
        except ValueError:
            result = "Введенные данные не являются числом"

        return result

    def rules(self):
        return "TBD!"