import discord
from discord.ext import commands
from core import Krypton, Context

class Mod(commands.Cog):
    def __init__(self, bot: Krypton) -> None:
        self.bot = bot