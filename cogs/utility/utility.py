import discord
from discord.ext import commands
from core import Krypton, Context
from utils import JsonDb

class Utility(commands.Cog):
    def __init__(self, bot: Krypton):
        self.bot = bot


    