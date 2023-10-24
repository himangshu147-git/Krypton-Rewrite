from .error import *
from .guild import *

from core import Krypton

async def setup(bot: Krypton):
    await bot.add_cog(Error(bot))
    await bot.add_cog(Guild(bot))