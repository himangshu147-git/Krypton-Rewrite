import discord
from discord.ext import commands

from core import Context, Krypton


class Guild(commands.Cog):
    def __init__(self, bot: Krypton) -> None:
        self.bot = bot