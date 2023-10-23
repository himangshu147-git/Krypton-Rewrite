from .developer import Developer
from core import Krypton

async def setup(bot: Krypton):
    await bot.add_cog(Developer(bot))