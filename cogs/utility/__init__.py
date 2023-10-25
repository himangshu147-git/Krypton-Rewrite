from .utility import Utility
from core import Krypton

async def setup(bot: Krypton):
    await bot.add_cog(Utility(bot))