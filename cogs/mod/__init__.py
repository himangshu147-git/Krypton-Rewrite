from .mod import Mod
from core import Krypton

async def setup(bot: Krypton):
    await bot.add_cog(Mod(bot))