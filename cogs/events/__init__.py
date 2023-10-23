from .error import *

from core import Krypton

async def setup(bot: Krypton):
    await bot.add_cog(Error(bot))