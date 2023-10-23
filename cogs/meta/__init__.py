from .meta import Meta
from core import Krypton

async def setup(bot: Krypton):
    await bot.add_cog(Meta(bot))